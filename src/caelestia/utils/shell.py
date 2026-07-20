from pathlib import Path

from caelestia.utils.dots.packages import PackageInstaller

# Known AUR package names for the CLI itself
CLI_PKG_NAMES = ("dim-caelestia-cli-git",)

# Known AUR package names for the Caelestia shell
SHELL_PKG_NAMES = ("dim-caelestia-shell-git",)


def shell_managed_externally(installer: PackageInstaller) -> bool:
    """Decide whether pkgit should skip managing the shell.

    Checked in priority order:
    1. How the CLI itself was installed. The advised flow is "install the
       CLI, then run `caelestia install`" -- on a fresh install the shell
       package doesn't exist yet, so shell-based detection alone can't see
       intent on a first run. The CLI is guaranteed to already be installed
       by the time this runs, so its origin is the reliable signal.
    2. Whether the shell package is already installed directly -- covers
       setups where the shell was installed separately from the CLI.
    3. A manual-install marker for users who built the shell by hand.
    """
    # Primary: CLI package presence
    if any(installer.is_installed(name) for name in CLI_PKG_NAMES):
        return True

    # Secondary: shell package presence
    if any(installer.is_installed(name) for name in SHELL_PKG_NAMES):
        return True

    # Fallback: manual-install marker
    marker = Path.home() / ".local" / "state" / "caelestia" / "shell-managed"
    return marker.exists()
