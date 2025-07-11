#!/bin/bash

set -e

source src/scripts/utils.sh
source src/scripts/configs.sh

$RESOURCES = src/resources 

install_dependencies(){
    echo -e "\e[1;34m===== 🔥 Installing Dependencies =====\e[0m"

    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ] || [ "$DISTRO" = "fedora" ]; then
        install pkg $(get_data common dependencies)
    else
        echo "$DISTRO"
        return 1
    fi
}

install_packages() {
    echo -e "\e[1;34m===== 🔥 Installing Packages =====\e[0m"

    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ] || [ "$DISTRO" = "fedora" ]; then        
        install pkg $(get_data common common)
        install pkg $(get_data "$DISTRO" apps)
        if is_gnome; then
            install pkg $(get_data "$DISTRO" "gnome")
        fi

        if [ "$DISTRO" = "fedora" ]; then
            install_rpms
            install_docker_fedora
        fi
    else
        echo "Invalid Distro: $DISTRO"
        return 1
    fi
}

install_fonts() {
    echo -e "\e[1;34m===== 🔥 Installing Fonts =====\e[0m"
    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ] || [ "$DISTRO" = "fedora" ]; then
        install pkg $(get_data "$DISTRO" "fonts")

        local font_dir="$HOME/.local/share/fonts"
        local tmp_dir="$(mktemp -d)"

        mkdir -p "$font_dir"

        # Instalar JetBrainsMono Nerd Font
        local jb_url="https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip"
        curl -fsSL "$jb_url" -o "$tmp_dir/JetBrainsMono.zip"
        unzip -q "$tmp_dir/JetBrainsMono.zip" -d "$font_dir"

        # Instalar Hack Nerd Font
        local hack_url="https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Hack.zip"
        curl -fsSL "$hack_url" -o "$tmp_dir/Hack.zip"
        unzip -q "$tmp_dir/Hack.zip" -d "$font_dir"

        fc-cache -f "$font_dir"
        rm -rf "$tmp_dir"
    else
        echo "Invalid Distro: $DISTRO"
        return 1
    fi
}

snaps_install() {
    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "fedora" ]; then
        echo -e "\e[1;34m===== 🔥 Installing Snaps =====\e[0m"
        if [[ "$DISTRO" == "fedora" && ! -e /snap ]]; then
            sudo ln -s /var/lib/snapd/snap /snap
        fi
        install snap $(get_data common snaps)
    fi
}

install_flatpaks() {
    echo -e "\e[1;34m===== 🔥 Installing Flatpak Applications =====\e[0m"
    echo ""
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    install flatpak $(get_data common flatpaks)
}

downloads_debs() {
    if [ "$DISTRO" = "debian" ]; then
        echo -e "\e[1;34m===== 📥 Downloading Extra Software =====\e[0m"
        echo ""

        mkdir -p $RESOURCES

        (
            local downloads_debs=($(get_data debian downloads_debs))            
            cd $RESOURCES || exit 1

            for link in "${downloads_debs[@]}"; do
                echo "🔹 Downloading: $link"
                wget "$link"
            done
        )
    fi
}

install_debs(){
    if [ "$DISTRO" = "debian" ]; then
        echo -e "\e[1;34m===== 🔥 Installing DEB Packages =====\e[0m"
        echo ""

        (
            cd $RESOURCES || exit 1
            local programs=(./*.deb)

            for p in "${programs[@]}"; do
                install pkg $p
            done
            rm ./*.deb
            corrigir_vscode_sources
        )
    fi
}

intellij_install(){
    if [ "$DISTRO" = "debian" ]; then
        mkdir -p $RESOURCES
        echo -e "\e[1;34m===== 🔥 Installing IntelliJ =====\e[0m"

        (
            cd $RESOURCES || return 1
            git clone https://github.com/Ruanrodrigues20/intelliJ-install || {
                echo "❌ Failed to clone intelliJ-install repository."
                return 1
            }
            cd intelliJ-install || return 1
            bash install.sh
        )
    fi
}

install_firefox_deb() {
    if [ "$DISTRO" = "debian" ]; then
        read -p "Do you want to install Firefox (DEB)? [y/N] " answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            echo -e "\e[1;34m===== 🔥 Installing Firefox (DEB) =====\e[0m"
            echo ""

            remove_trava  

            sudo install -d -m 0755 /etc/apt/keyrings

            wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | \
                sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null

            gpg -n -q --import --import-options import-show /etc/apt/keyrings/packages.mozilla.org.asc | \
                awk '/pub/{getline; gsub(/^ +| +$/,""); if($0 == "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3") print "\nO fingerprint da chave corresponde ("$0").\n"; else print "\nFalha na verificação: o fingerprint ("$0") não corresponde ao esperado.\n"}'

            echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | \
                sudo tee /etc/apt/sources.list.d/mozilla.list > /dev/null

            echo '
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
' | sudo tee /etc/apt/preferences.d/mozilla > /dev/null

            sudo apt remove -y firefox-esr firefox >/dev/null 2>&1

            if command -v snap >/dev/null 2>&1 && snap list | grep -q "^firefox "; then
                sudo snap remove firefox >/dev/null 2>&1
            fi

            sudo apt update
            install pkg firefox
        fi
    fi
}

install_docker_fedora() {
    echo "📦 Instalando Docker no Fedora..."

    echo "🧪 Instalando dependências..."
    install pkg dnf-plugins-core curl

    echo "➕ Adicionando repositório oficial da Docker..."
    sudo tee /etc/yum.repos.d/docker-ce.repo > /dev/null <<EOF
[docker-ce-stable]
name=Docker CE Stable - \$basearch
baseurl=https://download.docker.com/linux/fedora/\$releasever/\$basearch/stable
enabled=1
gpgcheck=1
gpgkey=https://download.docker.com/linux/fedora/gpg
EOF

    echo "⬇️ Instalando Docker e componentes..."
    apps=(
        docker-ce
        docker-ce-cli
        containerd.io
        docker-buildx-plugin
        docker-compose-plugin
    )
    install pkg $apps

    sudo usermod -aG docker $USER

    echo "🚀 Ativando e iniciando o Docker..."
    sudo systemctl enable --now docker

    echo "🧪 Testando com hello-world..."
    sudo docker run hello-world

    echo "✅ Docker instalado com sucesso!"
}

install_rpms(){
    if [ "$DISTRO" = "fedora" ]; then
        echo -e "\e[1;34m===== 🔥 Installing rpms =====\e[0m"
        install pkg $(get_data "$DISTRO" "rpms")
    fi
}
