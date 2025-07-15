# src/post_install_linux/frontend/controller.py

from src.post_install_linux.backend.controller.controller import Controller as BackendController

class Controller:
    def __init__(self):
        self.backend = BackendController()

    def setup_yay(self):
        return self.backend.setup_yay()

    def test(self):
        return self.backend.test()

    def install_wallpapers(self):
        return self.backend.install_wallpapers()

    def install_dependencies(self):
        return self.backend.install_dependencies()

    def install_packages(self):
        return self.backend.install_packages()

    def install_fonts(self):
        return self.backend.install_fonts()

    def install_debs(self):
        return self.backend.install_debs()

    def install_flatpaks(self):
        return self.backend.install_flatpaks()

    def install_snaps(self):
        return self.backend.install_snaps()

    def install_intellij(self):
        return self.backend.install_intellij()

    def install_rpms(self):
        return self.backend.install_rpms()

    def install_gtk_theme(self):
        return self.backend.install_gtk_theme()

    def setup_aliases_and_tools(self):
        return self.backend.setup_aliases_and_tools()

    def git_config(self):
        return self.backend.git_config()

    def setup_tlp(self):
        return self.backend.setup_tlp()

    def setup_bt_service(self):
        return self.backend.setup_bt_service()

    def configs(self):
        return self.backend.configs()

    def set_profile_picture_current_user(self):
        return self.backend.set_profile_picture_current_user()

    def configs_keyboard(self):
        return self.backend.configs_keyboard()

    def set_configs_fastfetch(self):
        return self.backend.set_configs_fastfetch()

    def install_oh_my_bash(self):
        return self.backend.install_oh_my_bash()

    def install_theme_grub(self):
        return self.backend.install_theme_grub()

    def install_minimal(self):
        return self.backend.install_minimal()

    def install_complete(self):
        return self.backend.install_complete()

    def install_full(self):
        return self.backend.install_full()

    def get_apps(self):
        return self.backend.get_apps()
