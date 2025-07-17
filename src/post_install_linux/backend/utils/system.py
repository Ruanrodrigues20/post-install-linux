from src.post_install_linux.backend.env import DISTRO, PASSWORD
import src.post_install_linux.backend.utils.utils as utils


def is_gnome() -> bool:
    """
    Verifica se o GNOME está instalado no sistema, checando se o comando
    'gnome-shell --version' existe.

    Returns:
        bool: True se GNOME estiver instalado, False caso contrário.
    """
    try:
        result = utils.run_cmd(
            ["gnome-shell", "--version"],
            check=True,
            capture_output=True
        )
        return result.returncode == 0
    except Exception:
        return False


def remove_trava():
    if DISTRO == "debian":
        print("🔧 Removing APT lock files...")
        locks = [
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/dpkg/lock",
            "/var/cache/apt/archives/lock",
            "/var/lib/apt/lists/lock"
        ]
        for lock in locks:
            utils.run_cmd(["rm", "-rf", lock], sudo=True, password=PASSWORD)
        utils.run_cmd(["dpkg", "--configure", "-a"], sudo=True, password=PASSWORD)


def update_system():
    print("\033[1;34m===== 🔥 Updating System =====\033[0m")

    if DISTRO == "debian":
        utils.run_cmd(["dpkg", "--configure", "-a"], sudo=True, password=PASSWORD)
        utils.run_cmd(["apt", "update"], sudo=True, password=PASSWORD)
        utils.run_cmd(["apt", "upgrade", "-y"], sudo=True, password=PASSWORD)
        utils.run_cmd(["apt", "autoremove", "-y"], sudo=True, password=PASSWORD)
        utils.run_cmd(["apt", "clean"], sudo=True, password=PASSWORD)
    elif DISTRO == "arch":
        utils.run_cmd(["yay", "-Syu", "--noconfirm"], sudo=True, password=PASSWORD)
    elif DISTRO == "fedora":
        utils.run_cmd(["dnf", "upgrade", "--refresh", "-y"], sudo=True, password=PASSWORD)


def install(type: str, packages: list[str]):
    if type == "flatpak":
        _install_flatpaks(packages)
        return
    elif type == "snap":
        _install_snaps(packages)
        return
    elif type == "pkg":
        for pkg in packages:
            print(f"\033[1;33mInstalling {pkg}...\033[0m")
            _install_pkg(pkg)
    

def _install_pkg(pkg: str):
    """
    Install a package depending on the distribution.

    Args:
        pkg (str): package name
        distro (str): 'arch', 'debian', 'fedora', etc.
    """
    if DISTRO == "arch":
        result = utils.run_cmd(["pacman", "-Qi", pkg])
        if result.returncode != 0:
            utils.run_cmd(["yay", "-S", "--noconfirm", pkg], password=PASSWORD, sudo=True)
        else:
            print(f"\033[1;32m✔️  {pkg} is already installed.\033[0m")

    elif DISTRO == "debian":
        remove_trava()
        result = utils.run_cmd(["dpkg", "-s", pkg], sudo=True, password=PASSWORD)
        if result.returncode != 0:
            utils.run_cmd(["apt", "install", "-y", pkg], sudo=True, password=PASSWORD)
        else:
            print(f"\033[1;32m✔️  {pkg} is already installed.\033[0m")

    elif DISTRO == "fedora":
        result = utils.run_cmd(["rpm", "-q", pkg], sudo=True, password=PASSWORD)
        if result.returncode != 0:
            utils.run_cmd([ "dnf", "install", "-y",pkg], sudo=True, password=PASSWORD)
        else:
            print(f"\033[1;32m✔️  {pkg} is already installed.\033[0m")

    else:
        print(f"❌ Unsupported distribution for installation: {DISTRO}")
        return 1



def _install_flatpaks(apps: list[str]):
    for app in apps:
        print(f"\033[1;33mInstalling {app} via Flatpak...\033[0m")
        utils.run_cmd(["flatpak", "install", "-y", "flathub", app])


def _install_snaps(snaps: list[str]):
    for snap in snaps:
        result = utils.run_cmd(["snap", "list", snap])
        if result.returncode == 0:
            print(f"✅ {snap} is already installed. Skipping...")
        else:
            print(f"🔹 Installing: {snap}")
            utils.run_cmd(["snap", "install", snap, "--classic"], sudo=True, password=PASSWORD)
