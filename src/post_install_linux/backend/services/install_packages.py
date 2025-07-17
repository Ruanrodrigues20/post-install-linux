import os
import tempfile
import urllib.request
import zipfile
import glob
from post_install_linux.backend.utils.system import install, is_gnome
from src.post_install_linux.backend.utils.utils import get_data
from src.post_install_linux.backend.env import TEMP_DIR, DISTRO, PASSWORD
import src.post_install_linux.backend.utils.utils as utils



def install_dependencies():
    print("\033[1;34m===== 🔥 Installing Dependencies =====\033[0m")
    if DISTRO in ("debian", "arch", "fedora"):
        packages = get_data(distro="common", categoria="dependencies")
        if packages:
            install("pkg", packages)
    else:
        print(f"❌ Unsupported distribution: {DISTRO}")
        return 1
    
def install_packages():
    print("\033[1;34m===== 🔥 Installing Packages =====\033[0m")
    if DISTRO not in ("debian", "arch", "fedora"):
        print(f"❌ Invalid Distro: {DISTRO}")
        return 1

    # Instala pacotes comuns para qualquer distro
    common_pkgs = get_data("common", "common")
    if common_pkgs:
        install("pkg", common_pkgs)

    # Instala pacotes específicos da distro
    distro_pkgs = get_data(DISTRO, "apps")
    if distro_pkgs:
        install("pkg", distro_pkgs)

    # Se GNOME, instala pacotes específicos para GNOME
    if is_gnome():
        gnome_pkgs = get_data(DISTRO, "gnome")
        if gnome_pkgs:
            install("pkg", gnome_pkgs)
      
    if DISTRO == "fedora":
        install_rpms()
        install_docker_fedora()


def install_rpms():
    print("\033[1;34m===== 🔥 Installing RPMs Applications =====\033[0m")
    print()

    rpms = get_data("common", "flatpaks")
    if rpms:
        install("rpm", rpms)


def install_fonts():
    print("\033[1;34m===== 🔥 Installing Fonts =====\033[0m")
    if DISTRO not in ("debian", "arch", "fedora"):
        print(f"❌ Invalid Distro: {DISTRO}")
        return 1

    # Instala fontes da distro via package manager
    fonts = get_data(DISTRO, "fonts")
    if fonts:
        install("pkg", fonts)

    # Diretório de fontes local
    font_dir = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(font_dir, exist_ok=True)

    # Diretório temporário
    tmp_dir = tempfile.mkdtemp()

    try:
        # Instalar JetBrainsMono Nerd Font
        jb_url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip"
        jb_zip_path = os.path.join(tmp_dir, "JetBrainsMono.zip")
        urllib.request.urlretrieve(jb_url, jb_zip_path)
        with zipfile.ZipFile(jb_zip_path, 'r') as zip_ref:
            zip_ref.extractall(font_dir)

        # Instalar Hack Nerd Font
        hack_url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Hack.zip"
        hack_zip_path = os.path.join(tmp_dir, "Hack.zip")
        urllib.request.urlretrieve(hack_url, hack_zip_path)
        with zipfile.ZipFile(hack_zip_path, 'r') as zip_ref:
            zip_ref.extractall(font_dir)

        # Atualiza cache de fontes
        utils.run_cmd(["fc-cache", "-f", font_dir], check=True)

    finally:
        # Remove diretório temporário
        import shutil
        shutil.rmtree(tmp_dir)

  

def snaps_install():
    if DISTRO in ("debian", "fedora"):
        print("\033[1;34m===== 🔥 Installing Snaps =====\033[0m")

        if DISTRO == "fedora" and not os.path.exists("/snap"):
            utils.run_cmd(["ln", "-s", "/var/lib/snapd/snap", "/snap"], check=False, sudo=True, password=PASSWORD)

        snaps = get_data("common", "snaps")
        if snaps:
            install("snap", snaps)

def install_flatpaks():
    print("\033[1;34m===== 🔥 Installing Flatpak Applications =====\033[0m")
    print()

    # Adiciona o repositório flathub
    utils.run_cmd(["flatpak", "remote-add", "--if-not-exists"], check=True, sudo=True, password=PASSWORD)
    utils.run_cmd(["flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"], check=True, sudo=True, password=PASSWORD)

    flatpaks = get_data("common", "flatpaks")
    if flatpaks:
        install("flatpak", flatpaks)



def downloads_debs():
    if DISTRO != "debian":
        return

    print("\033[1;34m===== 📥 Downloading Extra Software =====\033[0m\n")

    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    links = get_data("debian", "downloads_debs")
    if not links:
        print("⚠️ No download links found.")
        return

    for link in links:
        filename = os.path.basename(link)
        dest_path = os.path.join(temp_dir, filename)

        print(f"🔹 Downloading: {link}")
        try:
            urllib.request.urlretrieve(link, dest_path)
        except Exception as e:
            print(f"❌ Failed to download {link}: {e}")



def install_debs():
    if DISTRO != "debian":
        return

    print("\033[1;34m===== 🔥 Installing DEB Packages =====\033[0m\n")

    deb_dir = os.path.join(TEMP_DIR)  # RESOURCES_DIR é o caminho global do projeto, ex: src/resources
    os.chdir(deb_dir)

    debs = glob.glob("*.deb")
    for deb in debs:
        print(f"📦 Installing {deb}")
        install("pkg", os.path.abspath(deb))

    # Remove os arquivos .deb após instalar
    for deb in debs:
        os.remove(deb)



def intellij_install():
    if DISTRO != "debian":
        return

    print("\033[1;34m===== 🔥 Installing IntelliJ =====\033[0m")
    os.makedirs(TEMP_DIR, exist_ok=True)

    os.chdir(TEMP_DIR)
    repo_url = "https://github.com/Ruanrodrigues20/intelliJ-install"

    if not os.path.isdir("intelliJ-install"):
        utils.run_cmd(["git", "clone", repo_url], check=True)
    else:
        print("📁 IntelliJ repo already cloned. Skipping.")

    install_path = os.path.join(TEMP_DIR, "intelliJ-install", "install.sh")
    utils.run_cmd(["bash", install_path], check=True)

def install_docker_fedora():
    print("📦 Installing Docker on Fedora...")

    print("🧪 Installing dependencies...")
    install("pkg", ["dnf-plugins-core", "curl"])

    print("➕ Adding Docker's official repository...")
    docker_repo = """[docker-ce-stable]
    name=Docker CE Stable - $basearch
    baseurl=https://download.docker.com/linux/fedora/$releasever/$basearch/stable
    enabled=1
    gpgcheck=1
    gpgkey=https://download.docker.com/linux/fedora/gpg
    """
    repo_path = "/etc/yum.repos.d/docker-ce.repo"
    utils.run_cmd(["tee", repo_path],sudo=True, password=PASSWORD, input=docker_repo.encode(), check=True)

    print("⬇️ Installing Docker and components...")
    apps = [
        "docker-ce",
        "docker-ce-cli",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin"
    ]
    install("pkg", apps)

    print("👤 Adding current user to docker group...")
    utils.run_cmd(["usermod", "-aG", "docker", os.getlogin()], sudo=True, password=PASSWORD,check=False)

    print("🚀 Enabling and starting Docker...")
    utils.run_cmd(["systemctl", "enable", "--now", "docker"], sudo=True, password=PASSWORD,check=True)

    print("🧪 Testing Docker with hello-world...")
    utils.run_cmd(["docker", "run", "hello-world"], sudo=True, password=PASSWORD, check=False)

    print("✅ Docker installed successfully!")

