#!/bin/bash




###########################################################################################
#Configs fot the program

setup_yay() {
    if [[ "$DISTRO" != "arch" ]]; then
        return
    fi
    
    if ! command -v yay &>/dev/null; then
        echo -e "\e[1;34m===== 🔥 Installing YAY =====\e[0m"

        sudo pacman -S --noconfirm --needed base-devel git

        mkdir -p resources

        (
            cd resources
            git clone https://aur.archlinux.org/yay.git
            cd yay && makepkg -si --noconfirm
            yay -Sy --aur --devel --timeupdate
            rm -rf ~/.cache/yay/completion.cache
            yay -Syu
            cd .. && rm -rf yay
        )
    fi
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


install_oh_my_bash() {
    echo -e "\e[1;34m===== 🔥 Installing Oh My Bash =====\e[0m"

    if [ -d "$HOME/.oh-my-bash" ]; then
        echo "Oh My Bash is already installed. Skipping..."
        return
    fi

    echo "Cloning Oh My Bash..."
    git clone --depth=1 https://github.com/ohmybash/oh-my-bash.git ~/.oh-my-bash

    echo "Setting up ~/.bashrc with the powerline theme..."
    cp ~/.oh-my-bash/templates/bashrc.osh-template ~/.bashrc

    # Set the powerline theme in .bashrc
    sed -i 's/^OSH_THEME=.*/OSH_THEME="powerline"/' ~/.bashrc
    echo -e "\e[1;32mOh My Bash has been installed with the 'powerline' theme. Restart the terminal to apply the changes.\e[0m"
}




git_config(){
    echo -e "\e[1;34m===== 🔥 Git Config =====\e[0m"

    echo "Are you sure you want to set up git? (y/n)"
    read -p "Enter your choice: " choice
    if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
        echo "Skipping git setup."
        return
    fi

    echo "Setting up git..."

    read -p "Enter your user name: " name
    echo "Your user name is: $name"

    read -p "Enter your email: " email
    echo "Your email is: $email"

    git config --global user.name "$name"
    git config --global user.email "$email"

    echo "Git config set successfully."

    echo "Do you want to generate a new SSH key for Git? (y/n)"
    read -p "Enter your choice: " ssh_choice
    if [[ "$ssh_choice" == "y" || "$ssh_choice" == "Y" ]]; then
        ssh_key_path="$HOME/.ssh/id_ed25519"

        if [[ -f "$ssh_key_path" ]]; then
            echo "SSH key already exists at $ssh_key_path"
        else
            ssh-keygen -t ed25519 -C "$email" -f "$ssh_key_path" -N ""
            echo "SSH key generated at $ssh_key_path"
        fi

        eval "$(ssh-agent -s)"
        ssh-add "$ssh_key_path"

        echo "Public key:"
        cat "${ssh_key_path}.pub"

        echo "Now add the above public key to your Git provider (e.g., GitHub, GitLab)."
    else
        echo "Skipping SSH key generation."
    fi
}

corrigir_vscode_sources() {
    local keyring_path="/usr/share/keyrings/microsoft.gpg"
    local sources_file="/etc/apt/sources.list.d/vscode.sources"

    sudo mkdir -p "$(dirname "$keyring_path")"
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee "$keyring_path" > /dev/null

    if [ -f "$sources_file" ]; then
        sudo rm -f "$sources_file"
    fi

    sudo tee "$sources_file" > /dev/null <<EOF
Types: deb
URIs: https://packages.microsoft.com/repos/code/
Suites: stable
Components: main
Signed-By: $keyring_path
EOF

    sudo apt update
}



setup_bt_service() {
  local DISTRO_ID
  DISTRO_ID=$(grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '"')

  if [[ "$DISTRO_ID" == "debian" || "$DISTRO_ID" == "pop" || "$DISTRO_ID" == "pop_os" || "$DISTRO_ID" == "pop-os" ]]; then
    sudo tee /etc/systemd/system/rfkill-bluetooth.service > /dev/null <<EOF
[Unit]
Description=Bloquear Bluetooth no boot
After=bluetooth.service
ConditionPathExists=/usr/sbin/rfkill

[Service]
Type=oneshot
ExecStart=/usr/sbin/rfkill block bluetooth

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reexec
    sudo systemctl enable rfkill-bluetooth.service
  fi
}



setup_tlp() {
    if ! detect_battery; then
        echo -e "\e[33m⚠️  No battery detected. Skipping TLP installation.\e[0m"
        return 0
    fi

    echo -e "\n\e[34m🔧 Installing TLP and dependencies...\e[0m"

    if [[ "$DISTRO" == "arch" ]]; then
        yay -S --noconfirm tlp tlp-rdw &> /dev/null
        echo -e "\e[32m✔️  TLP installed successfully on Arch.\e[0m"
        echo -e "\n\e[34m🔌 Enabling TLP service...\e[0m"
        sudo systemctl enable tlp.service &> /dev/null
        sudo systemctl start tlp.service &> /dev/null

    elif [[ "$DISTRO" == "debian" ]]; then
        sudo apt install -y tlp &> /dev/null
        echo -e "\e[32m✔️  TLP installed successfully on Debian.\e[0m"
        remove_trava
        sudo apt install -y tlp tlp-rdw
        sudo systemctl enable tlp
        sudo systemctl start tlp
        sudo tlp-stat -s
    elif [[ "$DISTRO" == "fedora" ]]; then
        sudo dnf install -y tlp tlp-rdw &> /dev/null
        echo -e "\e[32m✔️  TLP installed successfully on Fedora.\e[0m"
        sudo systemctl enable tlp.service &> /dev/null
        sudo systemctl start tlp.service &> /dev/null
        sudo tlp-stat -s
    else
        echo -e "\e[31m❌  Unsupported distribution for installing TLP.\e[0m"
        return 1
    fi

}


set_configs_fastfetch() {
    if [ ! -f resources/fast.zip ]; then
        echo "❌ File 'resources/fast.zip' not found!"
        return 1
    fi

    (
        unzip -o resources/fast.zip || { echo "❌ Failed to unzip fast.zip"; exit 1; }

        rm -rf ~/.config/fastfetch

        if [ -d .config/fastfetch ]; then
            mv .config/fastfetch ~/.config/
            echo "✅ fastfetch config installed."
        else
            echo "❌ fastfetch config not found after unzip."
            exit 1
        fi

        rm -rf .config
    )
}


setup_aliases_and_tools(){
    echo -e "\e[1;34m===== 🔥 Configuration of the Aliases =====\e[0m"
    echo ""

    # Aliases
    cat <<EOF >> ~/.bash_aliases

# Aliases úteis
alias ll='ls -lah'
alias gs='git status'
alias gp='git push'
alias gl='git log --oneline --graph'
alias bat='upower -i /org/freedesktop/UPower/devices/battery_BAT1'
EOF

    echo "Aliases adicionados a ~/.bash_aliases"

    # Garante que o arquivo ~/.bash_aliases será carregado no .bashrc
    if ! grep -q "source ~/.bash_aliases" ~/.bashrc; then
        echo "source ~/.bash_aliases" >> ~/.bashrc
        echo "Linha 'source ~/.bash_aliases' adicionada ao ~/.bashrc"
    fi
}





###########################################################################################
#Configs fot the Gnome 
configs(){

    mkdir -p ~/Projects ~/Downloads ~/Documents ~/Pictures ~/Videos ~/Music ~/Desktop

	gsettings set org.gnome.desktop.interface show-battery-percentage  true
	gnome-extensions enable user-theme@gnome-shell-extensions.gcampax.github.com
	gsettings set org.gnome.shell favorite-apps "[
				  'org.gnome.Nautilus.desktop',
				  'firefox.desktop',
				  'org.gnome.Console.desktop',
				  'code.desktop',
				  'jetbrains-idea.desktop',
				  'org.gnome.TextEditor.desktop',
				  'com.discordapp.Discord.desktop',
				  'com.obsproject.Studio.desktop',
				  'org.gnome.Software.desktop',
				  'org.gnome.Settings.desktop',
				  'org.gnome.tweaks.desktop'
				]"

	# Define as pastas visíveis no grid
	gsettings set org.gnome.desktop.app-folders folder-children "['System', 'Office']"

	### ----- Pasta: System -----
	gsettings set org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/System/ name 'System'

	gsettings set org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/System/ apps "[
	  'htop.desktop',
	  'org.gnome.Loupe.desktop',
	  'org.gnome.Logs.desktop',
	  'org.freedesktop.MalcontentControl.desktop',
	  'qv4l2.desktop',
	  'qvidcap.desktop',
	  'org.gnome.Tour.desktop',
	  'vim.desktop',
	  'org.gnome.Epiphany.desktop',
	  'avahi-discover.desktop',
	  'bssh.desktop',
	  'bvnc.desktop',
	  'nm-connection-editor.desktop',
	  'org.gnome.Characters.desktop',
	  'org.gnome.Connections.desktop',
	  'org.gnome.baobab.desktop',
	  'org.gnome.font-viewer.desktop',
	  'yelp.desktop'
	]"

	### ----- Pasta: Office -----
	gsettings set org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/Office/ name 'Office'
	gsettings set org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/Office/ translate true

	gsettings set org.gnome.desktop.app-folders.folder:/org/gnome/desktop/app-folders/folders/Office/ apps "[
	  'libreoffice-writer.desktop',
	  'libreoffice-calc.desktop',
	  'libreoffice-impress.desktop',
	  'libreoffice-draw.desktop',
	  'libreoffice-math.desktop',
	  'libreoffice-base.desktop',
	  'libreoffice-startcenter.desktop',
	  'libreoffice-xsltfilter.desktop'
	]"
}



set_profile_picture_current_user() {
  if [ "$DISTRO" = "debian" ]; then

    local user="$USER"
    local home_dir="$HOME"
    local svg_path="$home_dir/.face"
    local png_path="$home_dir/.face.png"
    local icon_path="/var/lib/AccountsService/icons/$user"
    local user_conf_path="/var/lib/AccountsService/users/$user"

    if [ ! -f "$svg_path" ]; then
      return 1
    fi

    # Converte SVG para PNG
    convert "$svg_path" "$png_path" || {
      return 1
    }

    # Copia PNG para accountsservice
    sudo cp "$png_path" "$icon_path" || {
      return 1
    }

    # Cria arquivo de configuração do usuário no accountsservice
    sudo bash -c "cat > '$user_conf_path'" <<EOF
[User]
Icon=$icon_path
EOF

    # Ajusta permissões
    sudo chmod 644 "$icon_path"
    sudo chown root:root "$icon_path"

  fi
}


configs_keyboard(){

    local BASE_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"

    local SHORTCUTS=(
    "firefox;firefox;<Super>b"
    "files;nautilus;<Super>e"
    "terminal;kgx;<Super>t"
    )

    # Limpa atalhos antigos
    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "[]"

    local  PATHS=()

    for i in "${!SHORTCUTS[@]}"; do
    IFS=';' read -r name command binding <<< "${SHORTCUTS[$i]}"
    key_path="$BASE_PATH/custom$i/"
    PATHS+=("\"$key_path\"")

    gsettings set "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$key_path" name "$name"
    gsettings set "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$key_path" command "$command"
    gsettings set "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$key_path" binding "$binding"
    done

    # Junta os caminhos com vírgulas e aplica
    joined=$(IFS=,; echo "${PATHS[*]}")
    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "[$joined]"


    # Define as combinações desejadas
    local  LEFT_SHORTCUT="<Control><Super>Left"
    local RIGHT_SHORTCUT="<Control><Super>Right"

    # Aplica os atalhos com gsettings
    gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-left "['$LEFT_SHORTCUT']"
    gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-right "['$RIGHT_SHORTCUT']"

    # Define as combinações desejadas
    local CLOSE_SHORTCUT="<Super>q"
    local MINIMIZE_SHORTCUT="<Super>d"

    # Aplica os atalhos
    gsettings set org.gnome.desktop.wm.keybindings close "['$CLOSE_SHORTCUT']"
    gsettings set org.gnome.desktop.wm.keybindings minimize "['$MINIMIZE_SHORTCUT']"

}

