from pathlib import Path

from caelestia.utils.dots.packages import PackageInstaller

# Known AUR package names for the Caelestia shell
SHELL_PKG_NAMES = ("dim-caelestia-shell-git",)


def shell_managed_externally(installer: PackageInstaller) -> bool:
    """Check whether the shell is managed outside of pkgit.

    Returns True if:
    - An AUR/pacman package for the shell is installed (checked via installer.is_installed)
    - A manual-install marker exists at ~/.local/state/caelestia/shell-managed
    """
    if any(installer.is_installed(name) for name in SHELL_PKG_NAMES):
        return True

    marker = Path.home() / ".local" / "state" / "caelestia" / "shell-managed"
    return marker.exists()
