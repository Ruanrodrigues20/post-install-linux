#!/bin/bash
set -e

gtk_theme() {
    echo "Do you want to install the WhiteSur GTK theme? (y/n)"
    read -p "Enter your choice: " choice
    if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
        echo "Skipping GTK theme installation."
        return
    fi

    mkdir -p resources
    (
        cd resources
        clone_repositories
        install_gtk_theme
        install_themes_icons
        install_theme_cursors
        install_w_themes
        apply_configs_themes
    )

}

clone_repositories() {
    local reps=($(get_data themes))
    
    for rep in "${reps[@]}"; do
        local folder=$(basename "$rep" .git)
        if [ -d "$folder" ]; then
            echo "📁 Repository '$folder' already cloned. Skipping."
        else
            echo "⬇️ Cloning '$rep'..."
            git clone "$rep"
        fi
    done
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
}


configs_wallpapers() {
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local WALLPAPER_DIR="$HOME/.local/share/backgrounds"

    mkdir -p resources

    (
        cd resources || { echo "Failed to enter resources directory"; return 1; }

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
