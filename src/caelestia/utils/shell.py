from pathlib import Path

from caelestia.utils.dots.packages import PackageInstaller

# AUR package names -- git and stable variants
CLI_PKG_NAMES = ("dim-caelestia-cli-git", "dim-caelestia-cli")
SHELL_PKG_NAMES = ("dim-caelestia-shell-git", "dim-caelestia-shell")


def detect_shell_management_source(installer: PackageInstaller) -> str | None:
    """Work out how the shell should be managed.

    Priority follows the advised "install CLI, then run `caelestia install`" flow:
    1. "shell"  - shell AUR package already installed directly.
    2. "cli"    - shell isn't installed yet, but the CLI was installed via AUR;
                  install the shell from the same source.
    3. "manual" - manual-install marker present.
    4. None     - nothing detected; fall back to pkgit.
    """
    if any(installer.is_installed(name) for name in SHELL_PKG_NAMES):
        return "shell"

    if any(installer.is_installed(name) for name in CLI_PKG_NAMES):
        return "cli"

    marker = Path.home() / ".local" / "state" / "caelestia" / "shell-managed"
    if marker.exists():
        return "manual"

    return None


def shell_package_matching_cli(installer: PackageInstaller) -> str:
    """Pick the shell package variant matching whichever CLI variant is installed."""
    if installer.is_installed(CLI_PKG_NAMES[0]):  # -git
        return SHELL_PKG_NAMES[0]
    return SHELL_PKG_NAMES[1]  # stable
