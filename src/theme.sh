#!/bin/bash
set -e
source src/utils.sh

gtk_theme() {
    if ! is_gnome; then
        echo -e "\e[1;31mThis script is designed for GNOME environments only.\e[0m"
        return 1
    fi
    echo -e "\e[1;34m===== 🔥 Installing GTK Theme =====\e[0m"


    mkdir -p tmp
    clone_repositories
    (   
        cd tmp || { echo "Failed to enter tmp directory"; exit 1; }
        install_gtk_theme
        install_themes_icons
        install_theme_cursors
        install_w_themes
        apply_configs_themes
        install_theme_sound
        cd ..
    )


}

clone_repositories() {
    echo -e "\e[1;34m===== 🔥 Cloning WhiteSur Themes =====\e[0m"

    mkdir -p tmp

    clone_repo common whitesur-gtk        tmp/WhiteSur-gtk-theme
    clone_repo common whitesur-icons      tmp/WhiteSur-icon-theme
    clone_repo common whitesur-wallpapers tmp/WhiteSur-wallpapers
    clone_repo common whitesur-cursors    tmp/WhiteSur-cursors
}


install_gtk_theme() {
    (
        cd WhiteSur-gtk-theme || { echo "❌ Could not enter WhiteSur-gtk-theme"; exit 1; }

        ./install.sh -l
        sudo ./install.sh -a normal -m -N stable -t all
        sudo ./tweaks.sh -F 

        if [ -f ~/.local/share/backgrounds/sequoia.jpeg ]; then
            cp ~/.local/share/backgrounds/sequoia.jpeg ./
            sudo ./tweaks.sh -g -nb -b "sequoia.jpeg" -t blue -c dark
        else
            sudo ./tweaks.sh -g -nb -t blue -c dark
        fi

        sudo flatpak override --filesystem=xdg-config/gtk-3.0
        sudo flatpak override --filesystem=xdg-config/gtk-4.0
    )
}

install_themes_icons() {
    (
        if cd WhiteSur-icon-theme 2>/dev/null; then
            echo "🎨 Installing WhiteSur icon theme..."
            sudo ./install.sh -t all
        fi
    )
}

install_theme_cursors() {
    (
        if cd WhiteSur-cursors 2>/dev/null; then
            echo "🖱️ Installing WhiteSur cursor theme..."
            sudo ./install.sh
        fi
    )
}

install_w_themes() {
    (
        if cd WhiteSur-wallpapers 2>/dev/null; then
            echo "🖼️ Installing WhiteSur wallpapers..."
            sudo ./install-gnome-backgrounds.sh
            sudo ./install-wallpapers.sh
        else
            echo "❌ Directory 'WhiteSur-wallpapers' not found."
            exit 1
        fi
    )
}


apply_configs_themes() {
    echo -e "\e[1;34m===== 🔥 Applying themes =====\e[0m"

    gsettings set org.gnome.desktop.interface gtk-theme 'WhiteSur-Dark-blue' \
        && echo "✅ GTK theme applied." || echo "❌ Failed to apply GTK theme."
    
    gsettings set org.gnome.desktop.interface icon-theme 'WhiteSur-dark' \
        && echo "✅ Icon theme applied." || echo "❌ Failed to apply icon theme."
    
    gsettings set org.gnome.desktop.interface cursor-theme 'WhiteSur-cursors' \
        && echo "✅ Cursor theme applied." || echo "❌ Failed to apply cursor theme."
    
    gsettings set org.gnome.desktop.interface accent-color 'blue' \
        && echo "✅ Accent color applied." || echo "❌ Failed to apply accent color."
    
    gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:' \
        && echo "✅ Button layout applied." || echo "❌ Failed to apply button layout."
    
    gsettings set org.gnome.desktop.background picture-uri "file://$HOME/.local/share/backgrounds/sequoia.jpeg" \
        && echo "✅ Background applied." || echo "❌ Failed to apply background."
    
    gsettings set org.gnome.desktop.background picture-uri-dark "file://$HOME/.local/share/backgrounds/sequoia.jpeg" \
        && echo "✅ Dark background applied." || echo "❌ Failed to apply dark background."

    gsettings set org.gnome.desktop.sound theme-name "MacOs-Sounds"
        && echo "✅ Sound theme applied." || echo "❌ Failed to apply sound theme."
}


configs_wallpapers() {

    echo -e "\e[1;34m===== 🔥 Install Wallpapers =====\e[0m"

    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local WALLPAPER_DIR="$HOME/.local/share/backgrounds"

    mkdir -p tmp

    (
        cd tmp || { echo "Failed to enter tmp directory"; return 1; }

        if [ ! -d wallpapers ]; then
            git clone https://github.com/Ruanrodrigues20/wallpapers.git
        else
            echo "📁 wallpapers repo already cloned. Skipping clone."
        fi

        cd wallpapers || { echo "Failed to enter wallpapers directory"; return 1; }

        mkdir -p "$WALLPAPER_DIR"

        bash main.sh 

        cd ..
        rm -rf wallpapers
    )

    cd "$SCRIPT_DIR" || { echo "Failed to return to script directory"; return 1; }
}


install_theme_grub() {
    if grub-install --version &>/dev/null; then
        echo -e "\e[1;34m===== 🔥 Installing Theme Grub =====\e[0m"

        sudo mkdir -p /boot/grub/themes
        
        (
            cd /boot/grub/themes || { echo "Failed to enter /boot/grub/themes"; return 1; }
            
            if [ ! -d grub2-themes ]; then
                sudo git clone https://github.com/vinceliuice/grub2-themes.git
            fi
            
            cd grub2-themes || { echo "Failed to enter grub2-themes"; return 1; }
            
            sudo ./install.sh -t whitesur -i whitesur
            if [ $DISTRO == "fedora" ]; then
                sudo grub2-mkconfig -o /boot/grub2/grub.cfg
            else
                sudo update-grub
            fi
        )
    fi
}

install_theme_sound(){
    echo -e "\e[1;34m===== 🔥 Installing MacOS Sounds =====\e[0m"
    (
        cd tmp
        unzip MacOs-Sounds.zip -d MacOs-Sounds
        mv MacOs-Sounds/MacOs-Sounds ~/.local/share/sounds/MacOs-Sounds
        cd ..
        rm -rf tmp/MacOs-Sounds.zip
        rm -rf tmp/MacOs-Sounds
    )
    
}