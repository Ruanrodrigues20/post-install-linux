#!/bin/bash
# POST INSTALL LINUX
# Author: Ruan
# Description: Automates system setup for Debian/Arch-based systems with user selection
# Usage: bash main.sh

set -e

exec > >(tee -a "log.txt") 2>&1

if [ "$EUID" -eq 0 ]; then
    echo "❌ Do not run this script as root."
    exit 1
fi

# ======================
# Load all modules
# ======================
setup(){
    for module in scripts/*.sh; do
        source "$module"
    done
    check_internet_connection
    detect_distro
    mkdir -p resources
}


# ======================
# Show interactive checklist
# ======================
show_selection_interface() {
    selected=$(whiptail --title "POST INSTALL LINUX - Setup Menu" --checklist \
        "Select the steps you want to execute (use SPACE to select):" \
        30 80 20 \
        "INSTALL_ALL" "Run all steps" OFF \
        "check_dependencies" "Check system dependencies" OFF \
        "install_packages" "Install main packages" OFF \
        "install_firefox_deb" "Install Firefox (.deb)" OFF \
        "downloads_debs" "Download additional .deb files" OFF \
        "intellij_install" "Install IntelliJ IDEA" OFF \
        "install_flatpaks" "Install Flatpak packages" OFF \
        "snaps_install" "Install Snap packages" OFF \
        "configs_wallpapers" "Apply wallpapers and backgrounds" OFF \
        "gtk_theme" "Apply GTK theme" OFF \
        "setup_aliases_and_tools" "Configure aliases and tools" OFF \
        "install_theme_grub" "Apply GRUB theme" OFF \
        "git_config" "Configure Git" OFF \
        "setup_tlp" "Configure TLP (power management)" OFF \
        "setup_bt_service" "Enable and configure Bluetooth" OFF \
        "configs" "Apply custom dotfiles/configs" OFF \
        "set_profile_picture_current_user" "Set user profile picture" OFF \
        "configs_keyboard" "Configure keyboard layout" OFF \
        "install_fonts" "Install fonts" OFF \
        "set_configs_fastfetch" "Configure Fastfetch" OFF \
        "install_oh_my_bash" "Install Oh My Bash" OFF \
        3>&1 1>&2 2>&3)

    if [ $? -ne 0 ]; then
        echo "🚫 Installation cancelled by the user."
        exit 1
    fi

    selected=$(echo "$selected" | tr -d '"')
    IFS=' ' read -r -a SELECTED_OPTIONS <<< "$selected"
}

# ======================
# Run selected functions
# ======================
run_selected() {
    # Full list of available functions (in execution order)
    ALL_OPTIONS=(
        check_dependencies
        install_packages
        install_firefox_deb
        downloads_debs
        intellij_install
        install_flatpaks
        snaps_install
        configs_wallpapers
        gtk_theme
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
    )

    if [[ " ${SELECTED_OPTIONS[*]} " =~ " INSTALL_ALL " ]]; then
        echo "🔁 Running all available steps..."
        for opt in "${ALL_OPTIONS[@]}"; do
            echo "🔧 Executing: $opt"
            if declare -f "$opt" > /dev/null; then
                $opt
            else
                echo "⚠️ Function not found: $opt"
            fi
        done
    else
        for opt in "${SELECTED_OPTIONS[@]}"; do
            echo "🔧 Executing: $opt"
            if declare -f "$opt" > /dev/null; then
                $opt
            else
                echo "⚠️ Function not found: $opt"
            fi
        done
    fi
}

# ======================
# Main execution
# ======================
main() {
    setup
    show_selection_interface
    setup_yay
    run_selected
    ask_to_restart
}

main
