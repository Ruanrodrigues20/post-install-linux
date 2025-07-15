# src/post_install_linux/frontend/ui/main_window.py

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import threading

from ..controller.controller import Controller

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Post Install Linux - GTK4")
        self.set_default_size(600, 400)

        self.controller = Controller()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for side in ("start", "end", "top", "bottom"):
            getattr(vbox, f"set_margin_{side}")(10)
        self.set_child(vbox)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.buffer = self.textview.get_buffer()
        vbox.append(self.textview)

        # Botões
        btn_get_apps = Gtk.Button(label="Obter Lista de Apps")
        btn_get_apps.connect("clicked", self.on_get_apps)
        vbox.append(btn_get_apps)

        btn_install_minimal = Gtk.Button(label="Instalar Mínimo")
        btn_install_minimal.connect("clicked", self.on_install_minimal)
        vbox.append(btn_install_minimal)

    def append_text(self, text):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, text)
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
        self.textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        return False

    def on_get_apps(self, button):
        self.buffer.set_text("Carregando lista de apps...\n")
        threading.Thread(target=self.load_apps_thread, daemon=True).start()

    def load_apps_thread(self):
        try:
            apps = self.controller.get_apps()
            text = "Apps:\n" + "\n".join(f"- {app}" for app in apps) + "\n"
        except Exception as e:
            text = f"Erro ao obter apps: {e}\n"
        GLib.idle_add(self.append_text, text)

    def on_install_minimal(self, button):
        self.buffer.set_text("Iniciando instalação mínima...\n")
        threading.Thread(target=self.run_install_minimal_thread, daemon=True).start()

    def run_install_minimal_thread(self):
        def output_callback(text):
            GLib.idle_add(self.append_text, text)

        try:
            self.controller.install_minimal(output_callback)
        except Exception as e:
            GLib.idle_add(self.append_text, f"Erro na instalação: {e}\n")
