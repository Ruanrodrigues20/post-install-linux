import gi
import os
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Game Installer Pro")
        self.set_default_size(900, 600)

        main_box = self.build_ui()

        # Coloca o conteúdo na janela com o método disponível
        for method in ('set_content', 'set_child', 'add'):
            func = getattr(self, method, None)
            if func:
                func(main_box)
                break

    def build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # NÃO usa Adw.HeaderBar nem set_titlebar

        flow = Gtk.FlowBox()
        flow.set_valign(Gtk.Align.START)
        flow.set_max_children_per_line(4)
        flow.set_selection_mode(Gtk.SelectionMode.NONE)

        # Lista dos apps, aqui coloque o que quiser:
        apps = ["install_dependencies", "MangoHud", "RPCS3", "Lutris", "RetroArch"]

        for app in apps:
            flow.append(self.create_card(app))

        scroll_apps = Gtk.ScrolledWindow()
        scroll_apps.set_child(flow)
        scroll_apps.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_apps.set_vexpand(True)

        self.terminal_output = Gtk.TextView(editable=False, monospace=True)
        self.terminal_output.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        scroll_terminal = Gtk.ScrolledWindow()
        scroll_terminal.set_child(self.terminal_output)
        scroll_terminal.set_min_content_height(150)

        main_box.append(scroll_apps)
        main_box.append(scroll_terminal)

        return main_box

    def create_card(self, name):
        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12,
        )
        card.set_css_classes(["frame", "card"])

        title = Gtk.Label(label=name)
        title.set_css_classes(["title-3"])

        btn = Gtk.Button(label="Instalar")
        btn.connect("clicked", self.on_install_clicked, name)

        card.append(title)
        card.append(btn)
        return card

    def on_install_clicked(self, button, app_name):
        buffer = self.terminal_output.get_buffer()
        buffer.set_text("")  # limpa terminal antes

        if app_name == "install_dependencies":
            # Caminho absoluto do script shell
            script_path = os.path.abspath("src/scripts/install_packages.sh")

            if not os.path.isfile(script_path):
                buffer.set_text(f"Erro: script não encontrado: {script_path}\n")
                return

            # Executa o script com bash
            process = subprocess.Popen(
                ["/bin/bash", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

        else:
            # Só exemplo simples, pode ajustar para rodar comandos reais por app
            process = subprocess.Popen(
                ["echo", f"Instalando {app_name}..."],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

        def read_output():
            line = process.stdout.readline()
            if line:
                end_iter = buffer.get_end_iter()
                buffer.insert(end_iter, line)
                return True
            else:
                return False

        GLib.timeout_add(100, read_output)
