import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw
from src.gui.main_window import MainWindow
from src.configs.env import DISTRO
from src.utils.utils import check_connection, ask_to_restart, get_data
from src.utils.system import remove_lock_files, is_gnome, install, get_distro
from src.scripts.theme import gtk_theme
from src.scripts.install_packages import install_dependencies
import src.scripts.install_packages as ins



class PostInstallApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.PostInstall")

    def do_activate(self):
        win = MainWindow(self)
        win.present()


if __name__ == "__main__":
    import sys

    ins.install_flatpaks()
    
    
