#!/bin/bash

# Welcome message
show_intro_message(){
    echo -e "\e[1;34m🎉 Welcome! Starting the Arch Linux/Debian post-installation setup... 🚀\e[0m"
    echo "This script will install essential software, themes, aliases,"
    echo "developer tools, and configure your system for productivity."
    echo ""
    echo "Developed by: Ruan Rodrigues 👨‍💻"
    echo "GitHub: https://github.com/Ruanrodrigues20"
    echo ""

    echo -e "\e[1;33mThe setup will start automatically in 10 seconds... ⏳"
    echo -e "Or press any key to start immediately.\e[0m"

    for i in {10..1}; do
        echo -ne "\rStarting in $i... Press any key to begin ⏰"
        read -t 1 -n 1 -s key && break
    done
    echo -e "\rStarting now... 🚀                           \n"
}

# Show a summary of completed actions
show_summary() {
    echo -e "\e[1;34m===== 📋 Post-Installation Summary =====\e[0m"
    echo -e "\e[1;32m✔\e[0m System updated"
    echo -e "\e[1;32m✔\e[0m yay installed (Arch Linux only)"
    echo -e "\e[1;32m✔\e[0m Snap applications installed (Based Debian distro)"
    echo -e "\e[1;32m✔\e[0m Essential packages installed"
    echo -e "\e[1;32m✔\e[0m Flatpak applications installed"
    echo -e "\e[1;32m✔\e[0m WhiteSur GTK theme installed"
    echo -e "\e[1;32m✔\e[0m Aliases configured"
    echo -e "\e[1;32m✔\e[0m Git configuration completed"
    echo -e "\e[1;32m✔\e[0m User directories created"
    echo -e "\e[1;32m✔\e[0m TLP configured for power saving"
    echo -e "\e[1;34m🎉 All tasks completed successfully!\e[0m\n"
}


show_logo(){
    clear
    echo ""

    echo "██████╗  ██████╗ ███████╗████████╗
██╔══██╗██╔═══██╗██╔════╝╚══██╔══╝
██████╔╝██║   ██║███████╗   ██║   
██╔═══╝ ██║   ██║╚════██║   ██║   
██║     ╚██████╔╝███████║   ██║   
╚═╝      ╚═════╝ ╚══════╝   ╚═╝   
"

    echo "██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     
██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     
██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     
██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║     
██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
"

    echo ""
}


ask_to_restart(){
    if [ $DISTRO == "arch" ]; then
        yay -Sy --aur --devel --timeupdate
        rm -rf ~/.cache/yay/completion.cache
        yay -Syu
    fi

    read -p "Do you want to restart your system now? (y/n): " ans
    if [[ "$ans" == "y" || "$ans" == "Y" ]]; then
        sudo reboot
    fi
}


check_internet_connection() {
    echo -e "\e[1;34m===== 🌐 Checking internet connection =====\e[0m"
    if ping -c 1 1.1.1.1 &>/dev/null || ping -c 1 google.com &>/dev/null; then
        echo -e "\e[1;32m✔️ Internet is connected.\e[0m"
    else
        echo -e "\e[1;31m❌ No internet connection detected. Please check your network.\e[0m"
        exit 1
    fi
}




remove_trava(){
    if [ "$DISTRO" = "debian" ]; then
        sudo rm -f /var/lib/dpkg/lock-frontend
        sudo rm -f /var/lib/dpkg/lock
        sudo rm -f /var/cache/apt/archives/lock
        sudo rm -f /var/lib/apt/lists/lock
        sudo dpkg --configure -a
    fi
}

update(){
    echo -e "\e[1;34m===== 🔥 Updating System =====\e[0m"
    echo ""
    remove_trava
    sudo apt update
    sudo apt upgrade -y
    sudo apt autoremove -y
    sudo apt clean
}


detect_distro() {
    if command -v apt &> /dev/null; then
        DISTRO="debian"
    elif command -v pacman &> /dev/null; then
        DISTRO="arch"
    else
        echo "Distribution not supported."
        exit 1
    fi
}

is_gnome() {
    if gnome-shell --version >/dev/null 2>&1; then
        return 0  # GNOME está instalado
    else
        return 1  # GNOME não está instalado
    fi
}


detect_battery() {
    if [ -d "/sys/class/power_supply/BAT0" ] || [ -d "/sys/class/power_supply/BAT1" ]; then
        return 0  # Sucesso: bateria detectada
    else
        return 1  # Falha: nenhuma bateria detectada
    fi
}


install() {
    local packages=("$@")

    if [ "$DISTRO" = "debian" ]; then
        remove_trava
    fi

    for pkg in "${packages[@]}"; do
        echo ""
        echo -e "\e[33mInstalling $pkg...\e[0m"
        install_pkg "$pkg"
    done
}


install_pkg() {
    local pkg="$1"
    if [ "$DISTRO" = "arch" ]; then
        if ! pacman -Qi "$pkg" &> /dev/null; then
            yay -S --noconfirm "$pkg"
        else
            echo -e "\e[32m✔️  $pkg is already installed.\e[0m"
        fi
    elif [ "$DISTRO" = "debian" ]; then
        if ! dpkg -l | grep -E "^ii\s+$pkg" &> /dev/null; then
            sudo apt install -y "$pkg"
        else
            echo -e "\e[32m✔️  $pkg is already installed.\e[0m"
        fi
    else
        echo "Distribuição não suportada para instalação."
        return 1
    fi
}


install_f() {
  for app in "$@"; do
    echo -e "\e[33mInstalling $app...\e[0m"
    flatpak install -y flathub "$app"
  done
}


_install_snaps() {
  for snap in "$@"; do
    if snap list "$snap" >/dev/null 2>&1; then
      echo "✅ $snap is already installed. Skipping..."
    else
      echo "🔹 Installing: $snap"
      sudo snap install "$snap" --classic
    fi
  done
}



get_data() {
  local cod=$1
  local dados=()
  read -ra dados <<< "$(python3 scripts/list_packages.py "$cod")"
  
  # Usa o array local dentro da função, por exemplo:
  printf '%s\n' "${dados[@]}"
}



