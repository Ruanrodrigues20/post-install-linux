#!/bin/bash

set -e

source src/utils.sh
source src/configs.sh

install_dependencies(){
    echo -e "\e[1;34m===== 🔥 Installing Dependencies =====\e[0m"

    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ] || [ "$DISTRO" = "fedora" ]; then
        install pkg $(get_common "dependencies")
    else
        echo "$DISTRO"
        return 1
    fi
}

install_packages() {
    echo -e "\e[1;34m===== 🔥 Installing Packages =====\e[0m"

    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ] || [ "$DISTRO" = "fedora" ]; then        
        install pkg $(get_common "common")
        install pkg $(get_packages "$DISTRO" "apps")
        if is_gnome; then
            install pkg $(get_packages "$DISTRO" "gnome")
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
    echo -e "\e[1;34m===== 🔤 Installing Fonts =====\e[0m"

    local font_dir="$HOME/.local/share/fonts"
    mkdir -p "$font_dir"

    # pega fontes (uma por linha)
    local fonts
    fonts=$(get_common "fonts")

    if [ -z "$fonts" ]; then
        echo "ℹ️ Nenhuma fonte definida."
        return 0
    fi

    while IFS= read -r font_url; do
        [ -z "$font_url" ] && continue

        local file_name
        file_name="$(basename "$font_url")"

        local tmp_file="/tmp/$file_name"

        echo "🔹 Baixando: $file_name"
        wget -q "$font_url" -O "$tmp_file"

        if [[ "$file_name" == *.zip ]]; then
            # cria pasta com nome do arquivo sem .zip
            local folder_name="${file_name%.zip}"
            local extract_dir="$font_dir/$folder_name"
            mkdir -p "$extract_dir"

            echo "📦 Extraindo $file_name para $extract_dir"
            unzip -o "$tmp_file" -d "$extract_dir"

            rm -f "$tmp_file"
        else
            echo "📁 Movendo $file_name para $font_dir"
            mv "$tmp_file" "$font_dir/"
        fi

    done <<< "$fonts"

    echo "🔄 Atualizando cache de fontes..."
    fc-cache -fv >/dev/null 2>&1

    echo -e "\e[1;32m✔ Fonts instaladas com sucesso.\e[0m"
}


install_flatpaks() {
    echo -e "\e[1;34m===== 🔥 Installing Flatpak Applications =====\e[0m"
    echo ""
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    install flatpak $(get_common "flatpaks")
}

downloads_debs() {
    if [ "$DISTRO" = "debian" ]; then
        echo -e "\e[1;34m===== 📥 Downloading Extra Software =====\e[0m"
        echo ""

        mkdir -p tmp

        (
            local downloads_debs=($(get_packages "debian" "downloads_debs"))            
            cd tmp || exit 1

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
            cd tmp || exit 1
            local programs=(./*.deb)

            for p in "${programs[@]}"; do
                install pkg $p
            done
            rm ./*.deb
            corrigir_vscode_sources
        )
    fi
}

jetbrain_install() {
    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "fedora" ]; then
        mkdir -p tmp
        echo -e "\e[1;34m===== 🔥 Installing IntelliJ =====\e[0m"

        (
            clone_repo common ides-jetbrain tmp/ides-jetbrain
            cd tmp/ides-jetbrain || return 1
            bash run.sh
            cd ..
            rm -rf ides-jetbrain
            cd ..
        )
    fi
}

install_firefox_deb() {
    if [ "$DISTRO" = "debian" ]; then
        read -p "Do you want to install Firefox (DEB)? [y/N] " answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            echo -e "\e[1;34m===== 🔥 Installing Firefox (DEB) =====\e[0m"
            echo ""

            remove_trava  # <- suponho que essa função esteja definida

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
        install pkg $(get_packages "$DISTRO" "rpms")
    fi
}