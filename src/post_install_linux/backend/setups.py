import os
import subprocess
import shutil
import zipfile
import tempfile
import urllib.request

from pathlib import Path

from src.post_install_linux.backend.utils.utils import get_data, check_connection, detect_battery
from src.post_install_linux.backend.utils.system import remove_trava
from src.post_install_linux.env import TEMP_DIR, DISTRO, ZIP_DIR, SO


def setup_yay():
    if DISTRO != "arch":
        return
    if shutil.which("yay") is not None:
        return

    print("\033[1;34m===== 🔥 Installing YAY =====\033[0m")
    subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "--needed", "base-devel", "git"])
    os.makedirs(TEMP_DIR, exist_ok=True)

    yay_path = os.path.join(TEMP_DIR, "yay")
    if os.path.exists(yay_path):
        shutil.rmtree(yay_path)

    subprocess.run(["git", "clone", "https://aur.archlinux.org/yay.git", yay_path])
    subprocess.run(["makepkg", "-si", "--noconfirm"], cwd=yay_path)
    subprocess.run(["yay", "-Sy", "--aur", "--devel", "--timeupdate"])
    subprocess.run(["yay", "-Syu"])
    shutil.rmtree(yay_path, ignore_errors=True)

def install_theme_grub():
    try:
        subprocess.run(["grub-install", "--version"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return

    print("\033[1;34m===== 🔥 Installing Theme Grub =====\033[0m")
    grub_path = "/boot/grub/themes"
    os.makedirs(grub_path, exist_ok=True)

    with subprocess.Popen(["sudo", "bash"], stdin=subprocess.PIPE) as proc:
        proc.stdin.write(b"""
        cd /boot/grub/themes || exit 1
        [ ! -d grub2-themes ] && git clone https://github.com/vinceliuice/grub2-themes.git
        cd grub2-themes || exit 1
        ./install.sh -t whitesur -i whitesur
        """)
        if DISTRO == "fedora":
            proc.stdin.write(b"grub2-mkconfig -o /boot/grub2/grub.cfg\n")
        else:
            proc.stdin.write(b"update-grub\n")

def install_oh_my_bash():
    print("\033[1;34m===== 🔥 Installing Oh My Bash =====\033[0m")
    home = os.path.expanduser("~")
    oh_my_bash_dir = os.path.join(home, ".oh-my-bash")

    if os.path.isdir(oh_my_bash_dir):
        print("Oh My Bash is already installed. Skipping...")
        return

    subprocess.run(["git", "clone", "--depth=1", "https://github.com/ohmybash/oh-my-bash.git", oh_my_bash_dir])
    bashrc_template = os.path.join(oh_my_bash_dir, "templates/bashrc.osh-template")
    bashrc = os.path.join(home, ".bashrc")
    shutil.copy(bashrc_template, bashrc)

    with open(bashrc, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if line.startswith("OSH_THEME="):
                f.write('OSH_THEME="powerline"\n')
            else:
                f.write(line)
        f.truncate()

    print("\033[1;32mOh My Bash installed with 'powerline' theme. Restart terminal to apply.\033[0m")

def git_config():
    print("\033[1;34m===== 🔥 Git Config =====\033[0m")
    choice = input("Are you sure you want to set up git? (y/n): ")
    if choice.lower() != "y":
        print("Skipping git setup.")
        return

    name = input("Enter your user name: ")
    email = input("Enter your email: ")
    subprocess.run(["git", "config", "--global", "user.name", name])
    subprocess.run(["git", "config", "--global", "user.email", email])
    print("Git config set successfully.")

    ssh_choice = input("Do you want to generate a new SSH key for Git? (y/n): ")
    if ssh_choice.lower() == "y":
        key_path = os.path.expanduser("~/.ssh/id_ed25519")
        if not os.path.isfile(key_path):
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-C", email, "-f", key_path, "-N", ""])
            subprocess.run(["eval", "$(ssh-agent -s)"], shell=True)
            subprocess.run(["ssh-add", key_path])
        with open(f"{key_path}.pub") as f:
            print("Public key:")
            print(f.read())
        print("Now add the above public key to your Git provider.")

def corrigir_vscode_sources():
    keyring_path = "/usr/share/keyrings/microsoft.gpg"
    sources_file = "/etc/apt/sources.list.d/vscode.sources"

    subprocess.run(f"curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee {keyring_path} > /dev/null", shell=True)
    if os.path.exists(sources_file):
        os.remove(sources_file)

    content = f"""Types: deb
    URIs: https://packages.microsoft.com/repos/code/
    Suites: stable
    Components: main
    Signed-By: {keyring_path}
    """
    with open(sources_file, "w") as f:
        f.write(content)
    subprocess.run(["sudo", "apt", "update"])

def setup_tlp():
    if not detect_battery():
        print("\033[33m⚠️  No battery detected. Skipping TLP installation.\033[0m")
        return

    print("\n\033[34m🔧 Installing TLP and dependencies...\033[0m")
    if DISTRO == "arch":
        subprocess.run(["yay", "-S", "--noconfirm", "tlp", "tlp-rdw"])
    elif DISTRO == "debian":
        remove_trava()
        subprocess.run(["sudo", "apt", "install", "-y", "tlp", "tlp-rdw"])
    elif DISTRO == "fedora":
        subprocess.run(["sudo", "dnf", "install", "-y", "tlp", "tlp-rdw"])
    else:
        print("\033[31m❌  Unsupported distribution for installing TLP.\033[0m")
        return

    subprocess.run(["sudo", "systemctl", "enable", "--now", "tlp.service"])
    subprocess.run(["sudo", "tlp-stat", "-s"])


def setup_aliases_and_tools():
    print("\033[1;34m===== 🔥 Configuration of the Aliases =====\033[0m")
    bash_aliases = os.path.expanduser("~/.bash_aliases")
    aliases = """
    # Aliases úteis
    alias ll='ls -lah'
    alias gs='git status'
    alias gp='git push'
    alias gl='git log --oneline --graph'
    alias bat='upower -i /org/freedesktop/UPower/devices/battery_BAT1'
    """
    with open(bash_aliases, "a") as f:
        f.write(aliases)

    bashrc = os.path.expanduser("~/.bashrc")
    with open(bashrc, "a+") as f:
        f.seek(0)
        if "source ~/.bash_aliases" not in f.read():
            f.write("\nsource ~/.bash_aliases\n")
            print("Added 'source ~/.bash_aliases' to ~/.bashrc")

    print("Aliases added to ~/.bash_aliases")


def setup_bt_service():
    # Lê o ID da distro do arquivo /etc/os-release
    distro_id = None
    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("ID="):
                distro_id = line.strip().split("=")[1].replace('"', '')
                break

    if distro_id in ("debian", "pop", "pop_os", "pop-os"):
        service_content = """[Unit]
        Description=Bloquear Bluetooth no boot
        After=bluetooth.service
        ConditionPathExists=/usr/sbin/rfkill

        [Service]
        Type=oneshot
        ExecStart=/usr/sbin/rfkill block bluetooth

        [Install]
        WantedBy=multi-user.target
        """
        # Escreve o arquivo do serviço via sudo tee
        proc = subprocess.run(
            ["sudo", "tee", "/etc/systemd/system/rfkill-bluetooth.service"],
            input=service_content.encode(),
            stdout=subprocess.DEVNULL,
            check=True
        )

        # Recarrega o daemon e habilita o serviço
        subprocess.run(["sudo", "systemctl", "daemon-reexec"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "rfkill-bluetooth.service"], check=True)



def set_configs_fastfetch():
    fastzip = os.path.join(ZIP_DIR, "fast.zip")
    home_config = Path.home() / ".config"
    fastfetch_dir = home_config / "fastfetch"

    if not fastzip.is_file():
        print("❌ File 'resources/fast.zip' not found!")
        return 1

    # Descompacta fast.zip na pasta atual
    unzip_proc = subprocess.run(["unzip", "-o", str(fastzip)])
    if unzip_proc.returncode != 0:
        print("❌ Failed to unzip fast.zip")
        return 1

    # Remove configuração antiga
    if fastfetch_dir.exists():
        shutil.rmtree(fastfetch_dir)

    # Move pasta .config/fastfetch para ~/.config/
    if Path(".config/fastfetch").exists():
        shutil.move(".config/fastfetch", str(fastfetch_dir))
        print("✅ fastfetch config installed.")
    else:
        print("❌ fastfetch config not found after unzip.")
        return 1

    # Remove pasta .config temporária se existir
    if Path(".config").exists():
        shutil.rmtree(".config")



def configs():
    home = Path.home()
    # Cria pastas padrão
    for folder in ["Projects", "Downloads", "Documents", "Pictures", "Videos", "Music", "Desktop"]:
        (home / folder).mkdir(parents=True, exist_ok=True)

    # Comandos gsettings para configurar GNOME
    cmds = [
        ["gsettings", "set", "org.gnome.desktop.interface", "show-battery-percentage", "true"],
        ["gnome-extensions", "enable", "user-theme@gnome-shell-extensions.gcampax.github.com"],
        ["gsettings", "set", "org.gnome.shell", "favorite-apps",
         "['org.gnome.Nautilus.desktop','firefox.desktop','org.gnome.Console.desktop','code.desktop','jetbrains-idea.desktop','org.gnome.TextEditor.desktop','com.discordapp.Discord.desktop','com.obsproject.Studio.desktop','org.gnome.Software.desktop','org.gnome.Settings.desktop','org.gnome.tweaks.desktop']"],
        ["gsettings", "set", "org.gnome.desktop.app-folders", "folder-children", "['System', 'Office']"],

        # System folder
        ["gsettings", "set", "org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/System/", "name", "System"],
        ["gsettings", "set", "org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/System/", "apps",
         "['htop.desktop','org.gnome.Loupe.desktop','org.gnome.Logs.desktop','org.freedesktop.MalcontentControl.desktop','qv4l2.desktop','qvidcap.desktop','org.gnome.Tour.desktop','vim.desktop','org.gnome.Epiphany.desktop','avahi-discover.desktop','bssh.desktop','bvnc.desktop','nm-connection-editor.desktop','org.gnome.Characters.desktop','org.gnome.Connections.desktop','org.gnome.baobab.desktop','org.gnome.font-viewer.desktop','yelp.desktop']"],

        # Office folder
        ["gsettings", "set", "org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/Office/", "name", "Office"],
        ["gsettings", "set", "org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/Office/", "translate", "true"],
        ["gsettings", "set", "org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/Office/", "apps",
         "['libreoffice-writer.desktop','libreoffice-calc.desktop','libreoffice-impress.desktop','libreoffice-draw.desktop','libreoffice-math.desktop','libreoffice-base.desktop','libreoffice-startcenter.desktop','libreoffice-xsltfilter.desktop']"]
    ]

    for cmd in cmds:
        subprocess.run(cmd, check=False)



def set_profile_picture_current_user(distro):
    if distro != "debian":
        return

    user = os.getenv("USER")
    home_dir = Path.home()
    svg_path = home_dir / ".face"
    png_path = home_dir / ".face.png"
    icon_path = Path("/var/lib/AccountsService/icons") / user
    user_conf_path = Path("/var/lib/AccountsService/users") / user

    if not svg_path.is_file():
        return 1

    # Converter SVG para PNG (precisa ter imagem convertida)
    result = subprocess.run(["convert", str(svg_path), str(png_path)])
    if result.returncode != 0:
        return 1

    try:
        subprocess.run(["sudo", "cp", str(png_path), str(icon_path)], check=True)
    except subprocess.CalledProcessError:
        return 1

    conf_content = f"[User]\nIcon={icon_path}\n"
    subprocess.run(
        ["sudo", "bash", "-c", f"echo '{conf_content}' > '{user_conf_path}'"], check=True
    )

    subprocess.run(["sudo", "chmod", "644", str(icon_path)])
    subprocess.run(["sudo", "chown", "root:root", str(icon_path)])



def configs_keyboard():
    BASE_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"

    SHORTCUTS = [
        "firefox;firefox;<Super>b",
        "files;nautilus;<Super>e",
        "code;code;<Super>c",
    ]

    match SO:
        case "arch":
            SHORTCUTS.append("terminal;kgx;<Super>Return")
        case "fedora" | "debian":
            SHORTCUTS.append("terminal;gnome-terminal;<Super>Return")


    # Limpa atalhos antigos
    subprocess.run(["gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys", "custom-keybindings", "[]"])

    PATHS = []

    for i, shortcut in enumerate(SHORTCUTS):
        name, command, binding = shortcut.split(";")
        key_path = f"{BASE_PATH}/custom{i}/"
        PATHS.append(f'"{key_path}"')

        subprocess.run(["gsettings", "set", f"org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{key_path}", "name", name])
        subprocess.run(["gsettings", "set", f"org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{key_path}", "command", command])
        subprocess.run(["gsettings", "set", f"org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{key_path}", "binding", binding])

    joined = ",".join(PATHS)
    subprocess.run(["gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys", "custom-keybindings", f"[{joined}]"])

    LEFT_SHORTCUT = "<Control><Super>Left"
    RIGHT_SHORTCUT = "<Control><Super>Right"
    CLOSE_SHORTCUT = "<Super>q"
    MINIMIZE_SHORTCUT = "<Super>d"

    subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "move-to-workspace-left", f"['{LEFT_SHORTCUT}']"])
    subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "move-to-workspace-right", f"['{RIGHT_SHORTCUT}']"])
    subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "close", f"['{CLOSE_SHORTCUT}']"])
    subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "minimize", f"['{MINIMIZE_SHORTCUT}']"])