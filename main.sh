#!/bin/bash
# System Setup Script
# Author: Ruan
# Description: Automates system setup for Debian/Arch-based systems
# Usage: bash main.sh

set -e

# Save all output to a log file
exec > >(tee -a "log.txt") 2>&1

# Prevent running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root."
    exit 1
fi

# Load all modules from scripts/


# Initial setup steps
setup(){
    for module in scripts/*.sh; do
        source "$module"
    done
    check_internet_connection
    detect_distro
    mkdir -p resources
}


# ======================
# Função principal
# ======================

main() {
    setup

    show_logo
    show_intro_message

    # Etapas principais
    setup_yay
    check_dependencies
    install_packages
    install_fonts
    install_firefox_deb
    downloads_debs
    intellij_install
    install_flatpaks
    snaps_install
    
    configs_wallpapers
    gtk_theme

    #Configuração final
    setup_aliases_and_tools
    install_theme_grub
    git_config
    setup_tlp
    setup_bt_service
    configs
    set_profile_picture_current_user
    configs_keyboard
    install_fonts
    set_configs_fastfetch
    install_oh_my_bash

    show_summary
    ask_to_restart
}

# ======================
# Execução
# ======================
main
