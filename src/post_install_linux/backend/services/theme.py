import os
import sys
from src.post_install_linux.backend.utils.utils import get_data
from post_install_linux.backend.utils.system import is_gnome
from post_install_linux.backend.env import TEMP_DIR, DISTRO
import src.post_install_linux.backend.utils.utils as utils

class Theme:

    def __init__(self, password):
        self.PASSWORD = password
        
    def gtk_theme(self):
        if not is_gnome():
            print("\033[1;31mThis script is designed for GNOME environments only.\033[0m")
            return 1

        print("\033[1;34m===== 🔥 Installing GTK Theme =====\033[0m")
        os.makedirs(TEMP_DIR, exist_ok=True)
        self.clone_repositories()
        self.install_gtk_theme()
        self.install_themes_icons()
        self.nstall_theme_cursors()
        self.nstall_w_themes()
        self._configs_themes()
        utils.run_cmd(["rm", "-rf","'WhiteSur-gtk-theme'", "'WhiteSur-icon-theme'", "'WhiteSur-cursors'", "'WhiteSur-wallpapers'"], cwd=TEMP_DIR) 


    def install_wallpapers(self):
        print("\033[1;34m===== 🔥 Installing Wallpapers =====\033[0m")
        wallpapers_path = os.path.join(TEMP_DIR, "wallpapers")
        rep = get_data(distro="common", categoria="wallpapers") 
        if not os.path.isdir(wallpapers_path):
            utils.run_cmd(["git", "clone", rep], cwd=TEMP_DIR)
        if os.path.isdir(wallpapers_path):
            utils.run_cmd(["chmod", "+x", "main.sh"], cwd=wallpapers_path)
            utils.run_cmd(["./main.sh"], cwd=wallpapers_path)

        utils.run_cmd(["rm", "-rf","'wallpapers'"], cwd=TEMP_DIR) 

        
    def clone_repositories(self):
        print("\033[1;34m===== 🔥 Cloning Repositories =====\033[0m")
        os.chdir(TEMP_DIR)

        reps = get_data(distro="common", categoria="themes")  # Você deve implementar get_data
        for rep in reps:
            folder = os.path.basename(rep).replace(".git", "")
            if os.path.isdir(folder):
                print(f"📁 Repository '{folder}' already cloned. Skipping.")
            else:
                print(f"⬇️ Cloning '{rep}'...")
                utils.run_cmd(["git", "clone", rep])

        os.chdir(os.path.dirname(TEMP_DIR))  # volta para a pasta anterior


    def install_gtk_theme(self):
        path = os.path.join(TEMP_DIR, "WhiteSur-gtk-theme")
        if not os.path.isdir(path):
            print(f"❌ Directory '{path}' not found.")
            sys.exit(1)

        utils.run_cmd(["./install.sh", "-l"], cwd=path)
        utils.run_cmd(["./install.sh", "-a", "normal", "-m", "-N", "stable", "-t", "all"], cwd=path)
        utils.run_cmd(["./tweaks.sh", "-F"], cwd=path, sudo=True, password=self.PASSWORD)

        sequoia_path = os.path.expanduser("~/.local/share/backgrounds/sequoia.jpeg")
        if os.path.isfile(sequoia_path):
            utils.run_cmd(["cp", sequoia_path, "."], cwd=path)
            utils.run_cmd(["./tweaks.sh", "-g", "-nb", "-b", "sequoia.jpeg", "-t", "blue", "-c", "dark"], cwd=path, sudo=True, password=self.PASSWORD)
        else:
            utils.run_cmd(["./tweaks.sh", "-g", "-nb", "-t", "blue", "-c", "dark"], cwd=path, sudo=True, password=self.PASSWORD)

        utils.run_cmd(["flatpak", "override", "--filesystem=xdg-config/gtk-3.0"], sudo=True, password=self.PASSWORD)
        utils.run_cmd(["flatpak", "override", "--filesystem=xdg-config/gtk-4.0"], sudo=True, password=self.PASSWORD)


    def install_themes_icons(self):
        path = os.path.join(TEMP_DIR, "WhiteSur-icon-theme")
        if os.path.isdir(path):
            print("🎨 Installing WhiteSur icon theme...")
            utils.run_cmd(["./install.sh", "-t", "all"], cwd=path, sudo=True, password=self.PASSWORD)


    def install_theme_cursors():
        path = os.path.join(TEMP_DIR, "WhiteSur-cursors")
        if os.path.isdir(path):
            print("🖱️ Installing WhiteSur cursor theme...")
            utils.run_cmd(["./install.sh"], cwd=path)


    def install_w_themes(self):
        path = os.path.join(TEMP_DIR, "WhiteSur-wallpapers")
        if os.path.isdir(path):
            print("🖼️ Installing WhiteSur wallpapers...")
            utils.run_cmd(["./install-gnome-backgrounds.sh"], cwd=path)
            utils.run_cmd(["./install-wallpapers.sh"], cwd=path)
        else:
            print("❌ Directory 'WhiteSur-wallpapers' not found.")
            sys.exit(1)


    def apply_configs_themes(self):
        print("\033[1;34m===== 🔥 Applying themes =====\033[0m")

        home = os.path.expanduser("~")
        background_path = f"file://{home}/.local/share/backgrounds/sequoia.jpeg"

        def gsettings_set(schema, key, value):
            cmd = ["gsettings", "set", schema, key, value]
            res = utils.run_cmd(cmd)
            if res.returncode == 0:
                print(f"✅ {key.replace('-', ' ').capitalize()} applied.")
            else:
                print(f"❌ Failed to apply {key.replace('-', ' ')}.")

        gsettings_set("org.gnome.desktop.interface", "gtk-theme", "'WhiteSur-Dark-purple'")
        gsettings_set("org.gnome.desktop.interface", "icon-theme", "'WhiteSur-purple-dark'")
        gsettings_set("org.gnome.desktop.interface", "cursor-theme", "'WhiteSur-cursors'")
        gsettings_set("org.gnome.desktop.interface", "accent-color", "'purple'")
        gsettings_set("org.gnome.desktop.wm.preferences", "button-layout", "'close,minimize,maximize:'")
        gsettings_set("org.gnome.desktop.background", "picture-uri", f"'{background_path}'")
        gsettings_set("org.gnome.desktop.background", "picture-uri-dark", f"'{background_path}'")
        