import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

import sys
import builtins
import threading
import subprocess

# Controller simulado que executa comandos e envia output para a GUI
class Controller:
    def __init__(self, output_buffer):
        self.output_buffer = output_buffer

    def run_command(self, cmd):
        print(f"Executando comando: {' '.join(cmd)}\n")
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   bufsize=1,
                                   universal_newlines=True)

        for line in process.stdout:
            # Atualiza buffer GTK na thread principal
            GLib.idle_add(self.append_text, line)
        process.stdout.close()
        process.wait()

    def append_text(self, text):
        end_iter = self.output_buffer.get_end_iter()
        self.output_buffer.insert(end_iter, text)

        # Scroll automático
        mark = self.output_buffer.create_mark(None, self.output_buffer.get_end_iter(), True)
        self.output_buffer.place_cursor(mark)
        self.output_buffer.delete_mark(mark)

    def install_full(self):
        # Exemplo: lista arquivos /tmp (troque pelos seus comandos)
        self.run_command(["ls", "-l", "/tmp"])

    def install_packages(self):
        self.run_command(["echo", "Simulando instalação de pacotes..."])

    def install_gtk_theme(self):
        self.run_command(["echo", "Aplicando tema GTK..."])

    def install_oh_my_bash(self):
        self.run_command(["echo", "Configurando Oh My Bash..."])

class TextRedirector:
    def __init__(self, buffer):
        self.buffer = buffer

    def write(self, text):
        GLib.idle_add(self._write, text)

    def _write(self, text):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, text)

        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), True)
        self.buffer.place_cursor(mark)
        self.buffer.delete_mark(mark)

    def flush(self):
        pass

class InputDialog(Gtk.Dialog):
    def __init__(self, parent, prompt):
        super().__init__(title="Entrada necessária", transient_for=parent)
        self.set_modal(True)
        self.set_default_size(300, 100)

        self.set_child(Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6))

        self.label = Gtk.Label(label=prompt)
        self.entry = Gtk.Entry()
        self.button = Gtk.Button(label="Confirmar")

        self.get_child().append(self.label)
        self.get_child().append(self.entry)
        self.get_child().append(self.button)

        self.button.connect("clicked", self.on_confirm)

        self.input_value = None

    def on_confirm(self, button):
        self.input_value = self.entry.get_text()
        self.response(Gtk.ResponseType.OK)

    def get_input(self):
        self.present()
        self.wait_for_response()
        return self.input_value

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Post Install Linux")
        self.set_default_size(800, 600)

        self.set_child(Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                               margin_top=10, margin_bottom=10, margin_start=10, margin_end=10))
        box = self.get_child()

        self.full_install = Gtk.Switch()
        self.install_apps = Gtk.Switch()
        self.apply_theme = Gtk.Switch()
        self.config_terminal = Gtk.Switch()

        box.append(self._row("Full Install", self.full_install))
        box.append(self._row("Install Apps", self.install_apps))
        box.append(self._row("Apply Theme", self.apply_theme))
        box.append(self._row("Configure Terminal", self.config_terminal))

        self.output_view = Gtk.TextView()
        self.output_buffer = self.output_view.get_buffer()
        self.output_view.set_monospace(True)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.output_view)
        scrolled_window.set_vexpand(True)

        box.append(scrolled_window)

        self.execute_button = Gtk.Button(label="Executar")
        self.execute_button.connect("clicked", self.on_execute)
        box.append(self.execute_button)

        # Instancia controller passando output_buffer para manipular saída
        self.controller = Controller(self.output_buffer)

        # Redireciona print() e input()
        sys.stdout = TextRedirector(self.output_buffer)
        sys.stderr = TextRedirector(self.output_buffer)
        builtins.input = self.custom_input

    def _row(self, label_text, widget):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.append(Gtk.Label(label=label_text))
        row.append(widget)
        return row

    def custom_input(self, prompt):
        dialog = InputDialog(self, prompt)
        response = dialog.get_input()
        self.output_buffer.insert(self.output_buffer.get_end_iter(), f"{prompt}{response}\n")
        return response

    def on_execute(self, button):
        self.output_buffer.set_text("")
        thread = threading.Thread(target=self.run_tasks)
        thread.start()

    def run_tasks(self):
        if self.full_install.get_active():
            print("[+] Executando instalação completa...")
            self.controller.install_full()

        if self.install_apps.get_active():
            print("[+] Instalando apps...")
            self.controller.install_packages()

        if self.apply_theme.get_active():
            print("[+] Aplicando tema GTK...")
            self.controller.install_gtk_theme()

        if self.config_terminal.get_active():
            print("[+] Configurando terminal...")
            self.controller.install_oh_my_bash()

        print("\n[✓] Concluído.")

class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.ruan.PostInstall")

    def do_activate(self):
        win = MainWindow(self)
        win.present()

def start_gui():
    app = App()
    app.run()

if __name__ == "__main__":
    start_gui()
