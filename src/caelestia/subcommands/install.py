import shutil
import subprocess
import textwrap
from argparse import Namespace
from pathlib import Path

from caelestia.utils.dots.deployer import Deployer
from caelestia.utils.dots.legacy import (
    LEGACY_META_PKG,
    detect_legacy_repo,
    legacy_config_symlinks,
    legacy_symlinks,
    legacy_to_delete,
)
from caelestia.utils.dots.manifest import ComponentError, Manifest, ManifestError
from caelestia.utils.dots.misc import build_local_packages, run_hooks
from caelestia.utils.dots.packages import DEFAULT_AUR_HELPER, PackageError, PackageInstaller
from caelestia.utils.dots.source import DotsSource, SourceError
from caelestia.utils.dots.state import DotsState
from caelestia.utils.io import confirm, disable_input, fatal, info, log, pause, prompt_selection, warn
from caelestia.utils.paths import (
    config_backup_dir,
    config_dir,
)
from caelestia.utils.shell import shell_managed_externally


def _parse_list_arg(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _deref_symlink(link: Path, target: Path) -> None:
    """Replace symlink `link` with a real copy of `target`'s content."""

    bak = link.rename(link.parent / f"{link.name}.bak")
    try:
        if target.is_dir():
            shutil.copytree(target, link, symlinks=True)
        else:
            shutil.copy2(target, link)
    except OSError:
        bak.rename(link)
        raise
    bak.unlink()


def _install_shell_with_pkgit(installer: PackageInstaller, noconfirm: bool) -> None:
    """Install Caelestia Shell via pkgit, with fallback support for external package managers.

    This function handles shell installation with the following priority:
    1. If shell is managed by AUR package or manual-install marker > skip (externally managed)
    2. If pkgit is available > use pkgit to install
    3. If pkgit is not available > skip (shell will load from system paths)

    This allows installation paths:
    - AUR users: shell managed by pacman, CLI manages only dotfiles
    - Manual install: users set ~/.local/state/caelestia/shell-managed marker
    - pkgit users: CLI manages shell via pkgit
    - Minimal install: neither pkgit nor AUR, shell loads from system paths

    Args:
        installer: PackageInstaller instance
        noconfirm: If True, uses quiet flags (-qi instead of -i)
    """
    print()
    log("Installing Caelestia Shell...")

    # Check if shell is already managed by external package manager
    if shell_managed_externally(installer):
        info("Shell is managed by AUR package or manual install - skipping pkgit")
        info("The shell will load from system paths as configured by the package manager")
        return

    # Check if pkgit is available
    if shutil.which("pkgit") is None:
        info("pkgit not found - shell will load from system paths directly")
        info("To enable pkgit package management, install pkgit-git from AUR:")
        info("  yay -S pkgit-git")
        info("Or, if shell was installed separately (AUR/manual), create marker:")
        info("  mkdir -p ~/.local/state/caelestia && touch ~/.local/state/caelestia/shell-managed")
        return

    # Install via pkgit
    cmd = ["pkgit", "-qi" if noconfirm else "-i", "https://github.com/dim-ghub/caelestia-shell"]
    try:
        subprocess.run(cmd, check=True)
        info("Caelestia Shell installed successfully via pkgit")
    except subprocess.CalledProcessError as e:
        warn(f"Failed to install Caelestia Shell via pkgit: {e}")
        info("The shell will still function from system paths")


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.noconfirm:
            disable_input()

        self.print_greeting()
        self.create_backup()
        legacy_dir = detect_legacy_repo()  # Detect legacy repo first cause deploy overwrites legacy syms

        source, tip, manifest = self.fetch_manifest()
        try:
            installer, packages, local_packages = self.install_packages(source, manifest)
        except PackageError as e:
            fatal(e)
        run_hooks(manifest, "post_package")
        self.dereference_legacy(legacy_dir)  # Copy legacy content into place before deploy overwrites the symlinks
        deployed = self.deploy_configs(source, manifest)
        run_hooks(manifest, "post_install")

        # Install shell with intelligent detection of existing installations
        _install_shell_with_pkgit(installer, self.args.noconfirm)

        DotsState(
            aur_helper=getattr(installer, "helper", DEFAULT_AUR_HELPER),
            applied_rev=tip,
            enabled_components=manifest.enabled_components,
            packages=packages,
            local_packages=local_packages,
            deployed_files=deployed,
        ).save()

        self.migrate_legacy(installer, legacy_dir)
        self.print_done()
