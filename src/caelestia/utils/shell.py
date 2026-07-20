from pathlib import Path

from caelestia.utils.dots.packages import PackageInstaller

# Known AUR package names for the CLI itself
CLI_PKG_NAMES = ("dim-caelestia-cli-git",)

# Known AUR package names for the Caelestia shell
SHELL_PKG_NAMES = ("dim-caelestia-shell-git",)


def detect_shell_management_source(installer: PackageInstaller) -> str | None:
    """Detect where the shell is (or should be) managed from.

    Returns:
      - "shell" if the shell package is installed (pacman/AUR)
      - "cli" if the CLI package is installed (suggesting AUR-managed intent)
      - "manual" if a manual-install marker exists (~/.local/state/caelestia/shell-managed)
      - None if no sign of external management was found

    Priority is intentionally:
      1) shell package present
      2) CLI package present
      3) manual marker
    so that a fresh install (where the shell package is not yet present) can
    still infer the user's intent from how the CLI was installed.
    """
    # 1) shell package present
    if any(installer.is_installed(name) for name in SHELL_PKG_NAMES):
        return "shell"

    # 2) CLI package present (installer itself comes from the CLI package)
    if any(installer.is_installed(name) for name in CLI_PKG_NAMES):
        return "cli"

    # 3) manual marker
    marker = Path.home() / ".local" / "state" / "caelestia" / "shell-managed"
    if marker.exists():
        return "manual"

    return None


def should_skip_pkgit_for_shell(installer: PackageInstaller) -> bool:
    """Return True if pkgit should definitely be skipped for managing the shell.

    This is a convenience for callers that only need to know whether they
    should avoid invoking pkgit. Note that "cli" intent does NOT imply
    skipping pkgit; it implies the installer should prefer the system
    package manager to install the shell. Only an existing shell package or
    a manual marker should cause pkgit to be skipped outright.
    """
    src = detect_shell_management_source(installer)
    return src in ("shell", "manual")
