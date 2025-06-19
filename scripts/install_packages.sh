#!bin/bash

set -e

source scripts/utils.sh
source scripts/configs.sh


check_dependencies(){
    echo -e "\e[1;34m===== 🔥 Installing Dependencies =====\e[0m"

    local base_dir="./packages"
    local dependencies=()

    dependencies=$(python3 scripts/list_packages.py "dependencies")

    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ]; then
        install $dependencies
    else
        echo "$DISTRO"
        return 1
    fi
}

install_packages() {
    echo -e "\e[1;34m===== 🔥 Installing Packages =====\e[0m"

    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "arch" ]; then
        install $(python3 scripts/list_packages.py "common")
        install $(python3 scripts/list_packages.py "$DISTRO")
        if is_gnome; then
            install $(python3 scripts/list_packages.py "gnome_debian")
        fi
    else
        echo "Invalid Distro: $DISTRO"
        return 1
    fi
}



snaps_install() {
    if [ "$DISTRO" = "debian" ]; then
        echo -e "\e[1;34m===== 🔥 Installing Snap Applications =====\e[0m"

        # Converte a string retornada pelo Python em um array real
        read -ra snaps <<< "$(python3 scripts/list_packages.py "snaps")"

        for snap in "${snaps[@]}"; do
            if snap list "$snap" >/dev/null 2>&1; then
                echo -e "✅ $snap is already installed. Skipping..."
            else
                echo -e "🔹 Installing: $snap"
                sudo snap install "$snap" --classic
            fi
        done
    fi
}



install_flatpaks(){
    echo -e "\e[1;34m===== 🔥 Installing Flatpak Applications =====\e[0m"
    echo ""

    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

    # Transforma a string em array
    read -ra apps <<< "$(python3 scripts/list_packages.py "flatpaks")"

    install_f "${apps[@]}"
}




downloads_debs() {
    if [ "$DISTRO" = "debian" ]; then
        echo -e "\e[1;34m===== 📥 Downloading Extra Software =====\e[0m"
        echo ""

        read -ra links <<< "$(python3 scripts/list_packages.py "downloads_debs")"

        mkdir -p resources

        (
            cd resources || exit 1

            for link in "${links[@]}"; do
                echo "🔹 Downloading: $link"
                wget "$link"
            done

            local programs=(./*.deb)
            install "${programs[@]}"
            rm ./*.deb
        )

        corrigir_vscode_sources
    fi
}


intellij_install(){
    if [ "$DISTRO" = "debian" ]; then
        mkdir -p resources
        (
            cd resources || return 1
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

            sudo apt update && sudo apt install -y firefox
        fi
    fi
}

