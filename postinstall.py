import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw
from src.gui.main_window import MainWindow


class PostInstallApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.PostInstall")

    def do_activate(self):
        win = MainWindow(self)
        win.present()


if __name__ == "__main__":
    import sys

    from src.configs.env import DISTRO
    print(DISTRO)
