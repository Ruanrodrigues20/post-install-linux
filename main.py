#!/usr/bin/env python3
import sys
import os
import subprocess

import shutil
# outros imports

from pathlib import Path
from src.utils.utils import check_connection, ask_to_restart, detect_battery
from src.utils.setup import setup_yay, install_theme_grub, install_oh_my_bash, git_config, corrigir_vscode_sources, setup_tlp, setup_aliases_and_tools, setup_bt_service, set_configs_fastfetch, configs, set_profile_picture_current_user, configs_keyboard
from src.scripts.install_packages import (
    install_dependencies,
    install_packages,
    install_fonts,
    snaps_install,
    install_flatpaks,
    downloads_debs,
    install_debs,
    intellij_install,
    install_docker_fedora
)
from src.scripts.theme import gtk_theme, install_gtk_theme, install_themes_icons, install_theme_cursors, install_w_themes, apply_configs_themes


# Importa suas funções Python que replicam os scripts bash
# Exemplo:
# from src.setup import setup_yay, install_dependencies, install_packages, ...
# from src.git import git_config
# from src.gnome import configs, configs_keyboard
# etc.
# Aqui vou só supor que você já importou todas funções usadas abaixo.

# Cores ANSI
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # Sem cor

def show_logo():
    # Coloque seu logo aqui, por exemplo:
    print(f"{CYAN}=== Setup Script by Ruan ==={NC}\n")

def ask_to_restart():
    answer = input("Deseja reiniciar o sistema agora? (s/N): ").strip().lower()
    if answer == 's':
        print("Reiniciando...")
        subprocess.run(["sudo", "reboot"])

def check_running_as_root():
    if os.geteuid() == 0:
        print(f"{RED}Por favor, não execute este script como root.{NC}")
        sys.exit(1)

def setup():
    # Simula carregar módulos Python (já importados)
    # Aqui poderia chamar funções como check_internet_connection() e detect_distro()
    # e criar pasta resources
    check_connection()
    Path("resources").mkdir(exist_ok=True)

def install_minimal():
    setup_yay()
    install_dependencies()
    install_packages()
    install_flatpaks()
    snaps_install()

def install_complete():
    setup_yay()
    install_dependencies()
    install_packages()
    install_fonts()
    downloads_debs()
    install_debs()
    intellij_install()
    install_flatpaks()
    snaps_install()

    setup_aliases_and_tools()
    git_config()
    setup_tlp()
    setup_bt_service()
    configs()
    set_profile_picture_current_user()
    configs_keyboard()
    install_fonts()
    set_configs_fastfetch()

def install_full():
    setup_yay()
    install_dependencies()
    install_packages()
    install_fonts()
    downloads_debs()
    install_debs()
    intellij_install()
    install_flatpaks()
    snaps_install()

    gtk_theme()

    setup_aliases_and_tools()
    install_theme_grub()
    git_config()
    setup_tlp()
    setup_bt_service()
    configs()
    set_profile_picture_current_user()
    configs_keyboard()
    install_fonts()
    set_configs_fastfetch()
    install_oh_my_bash()

def main():
    check_running_as_root()
    setup()
    show_logo()

    if len(sys.argv) > 1:
        choice = sys.argv[1].lower()
    else:
        print(f"{CYAN}Por favor, escolha o tipo de instalação:{NC}")
        options = ["minimal", "complete", "full", "exit"]
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        while True:
            try:
                sel = int(input("Escolha uma opção (número): ").strip())
                if 1 <= sel <= len(options):
                    choice = options[sel - 1]
                    break
            except ValueError:
                pass
            print(f"{RED}Opção inválida. Tente novamente.{NC}")

    if choice == "exit":
        print(f"{YELLOW}Saindo.{NC}")
        sys.exit(0)

    print(f"{GREEN}Instalação selecionada: {choice}{NC}")

    if choice == "minimal":
        install_minimal()
    elif choice == "complete":
        install_complete()
    elif choice == "full":
        install_full()
    else:
        print(f"{RED}Opção inválida: {choice}{NC}")
        sys.exit(1)

    # Tenta notificar via notify-send se disponível
    if shutil.which("notify-send"):
        subprocess.run([
            "notify-send", "-u", "normal", "-i", "dialog-information",
            "✅ Post Install Completed", "Tudo foi instalado com sucesso!"
        ])

    ask_to_restart()

if __name__ == "__main__":
    main()
