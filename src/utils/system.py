import subprocess


def _get_distro():
    """
    Get the name of the Linux distribution from /etc/os-release.
    Returns the distribution name as a string, or None if not found.
    """
    result = subprocess.run(
        ["cat", "/etc/os-release"],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.strip().split("\n"):
        if line.startswith("NAME="):
            # Remove NAME= e possíveis aspas
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None  # se não achar


def get_distro():
    """
    return this system's distribution name
    """
    type_distro = ""
    distro = _get_distro().lower()
    if "fedora" in distro:
        type_distro = "fedora"
    elif "debian" in distro or "ubuntu" in distro or "linuxmint" in distro or "pop!_os" in distro:
        type_distro = "debian"
    elif "arch" in distro:
        type_distro = "arch"
    else:
        raise ValueError(f"Unsupported distribution: {distro}")
    return type_distro


def is_gnome() -> bool:
    """
    Verifica se o GNOME está instalado no sistema, checando se o comando
    'gnome-shell --version' existe.

    Returns:
        bool: True se GNOME estiver instalado, False caso contrário.
    """
    try:
        subprocess.run(
            ["gnome-shell", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    

def remove_lock_files():
    if get_distro() == "debian":
        print("🔧 Removing APT lock files...")
        locks = [
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/dpkg/lock",
            "/var/cache/apt/archives/lock",
            "/var/lib/apt/lists/lock"
        ]
        for lock in locks:
            subprocess.run(["sudo", "rm", "-f", lock])
        subprocess.run(["sudo", "dpkg", "--configure", "-a"])


def update_system():
    print("\033[1;34m===== 🔥 Updating System =====\033[0m")
    DISTRO = get_distro()

    if DISTRO == "debian":
        remove_lock_files()
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "upgrade", "-y"])
        subprocess.run(["sudo", "apt", "autoremove", "-y"])
        subprocess.run(["sudo", "apt", "clean"])
    elif DISTRO == "arch":
        subprocess.run(["yay", "-Syu", "--noconfirm"])
    elif DISTRO == "fedora":
        subprocess.run(["sudo", "dnf", "upgrade", "--refresh", "-y"])


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
    DISTRO = get_distro()
    if DISTRO == "arch":
        result = subprocess.run(["pacman", "-Qi", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            subprocess.run(["yay", "-S", "--noconfirm", pkg])
        else:
            print(f"\033[1;32m✔️  {pkg} is already installed.\033[0m")

    elif DISTRO == "debian":
        remove_lock_files()
        result = subprocess.run(["dpkg", "-s", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            subprocess.run(["sudo", "apt", "install", "-y", pkg])
        else:
            print(f"\033[1;32m✔️  {pkg} is already installed.\033[0m")

    elif DISTRO == "fedora":
        result = subprocess.run(["rpm", "-q", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            subprocess.run(["sudo", "dnf", "install", "-y", pkg])
        else:
            print(f"\033[1;32m✔️  {pkg} is already installed.\033[0m")

    else:
        print(f"❌ Unsupported distribution for installation: {DISTRO}")
        return 1



def _install_flatpaks(apps: list[str]):
    for app in apps:
        print(f"\033[1;33mInstalling {app} via Flatpak...\033[0m")
        subprocess.run(["flatpak", "install", "-y", "flathub", app])


def _install_snaps(snaps: list[str]):
    for snap in snaps:
        result = subprocess.run(["snap", "list", snap], stdout=subprocess.DEVNULL)
        if result.returncode == 0:
            print(f"✅ {snap} is already installed. Skipping...")
        else:
            print(f"🔹 Installing: {snap}")
            subprocess.run(["sudo", "snap", "install", snap, "--classic"])

