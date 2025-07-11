#!/bin/bash
# System Setup Script
# Author: Ruan
# Description: Automates system setup for Debian/Arch-based systems
# Usage: bash main.sh

set -e

BASEDIR="$(dirname "$(readlink -f "$0")")"
cd "$BASEDIR" || exit 1

# agora os comandos que usam src/*.sh vão funcionar corretamente

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
    for module in src/scripts/*.sh; do
        source "$module"
    done
    check_internet_connection
    detect_distro
    mkdir -p resources
    
}

install_minimal(){
    setup_yay
    install_dependencies
    install_packages
    install_flatpaks
    snaps_install
}


install_complete(){
    setup_yay
    install_dependencies
    install_packages
    install_fonts
    install_firefox_deb
    downloads_debs
    install_debs
    intellij_install
    install_flatpaks
    snaps_install
    

    #Configuração final
    setup_aliases_and_tools
    git_config
    setup_tlp
    setup_bt_service
    configs
    set_profile_picture_current_user
    configs_keyboard
    install_fonts
    set_configs_fastfetch

}

install_full(){
    # Etapas principais
    setup_yay
    install_dependencies
    install_packages
    install_firefox_deb
    downloads_debs
    install_debs
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
}

# ======================
# Função principal
# ======================
# Cores ANSI básicas
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

main() {
    setup
    show_logo

    CHOOSE_INSTALL=$1

    if [[ -z "$CHOOSE_INSTALL" ]]; then
        echo -e "${CYAN}Please choose an installation type:${NC}"
        select option in minimal complete full exit; do
            case "$option" in
                minimal|complete|full)
                    CHOOSE_INSTALL=$option
                    break
                    ;;
                exit)
                    echo -e "${YELLOW}Exiting.${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}Invalid choice. Please try again.${NC}"
                    ;;
            esac
        done
    fi

    echo -e "${GREEN}Selected installation: $CHOOSE_INSTALL${NC}"

    case "$CHOOSE_INSTALL" in
        minimal) install_minimal ;;
        complete) install_complete ;;
        full) install_full ;;
        *)
            echo -e "${RED}Invalid installation option: $CHOOSE_INSTALL${NC}"
            exit 1
            ;;
    esac

    if command -v notify-send >/dev/null; then
        notify-send -u normal -i dialog-information "✅ Post Install Completed" "Everything was installed successfully!"
    fi

    ask_to_restart
}


main "$@"
