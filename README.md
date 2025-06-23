# 🛠️ Post-Install-Linux

This is a **post-install automation script for Arch Linux-based, Debian-based, and Fedora-based systems**, designed to streamline the configuration of a fresh installation.

## 📁 Project Structure

```
Post-Install-Linux/
├── main.sh               # Main script that sources and runs all modules
├── LICENSE.txt           # License file
├── data/                 # JSON package lists per distro
│   ├── arch.json
│   ├── common.json
│   ├── debian.json
│   └── fedora.json
├── scripts/              # Modular scripts for each setup task
│   ├── configs.sh
│   ├── install_packages.sh
│   ├── list_packages.py
│   ├── theme.sh
│   └── utils.sh
└── resources/
    └── fast.zip
```

## 🚀 What It Does

* ✅ Checks internet connection
* 📦 Installs essential packages using `yay` (Arch), `apt` (Debian), or `dnf` (Fedora)
* 📦 Installs Flatpak applications
* 🎨 Applies GTK themes
* 🧑‍💻 Configures Git
* 🔧 Sets up aliases and useful tools
* 📂 Creates standard directories
* 🔋 Configures power-saving with TLP
* 🖼️ Applies wallpapers
* 📃 Shows a summary and asks to restart

## ▶️ Quick Usage

Run the following one-liner in your terminal:

```bash
git clone https://github.com/Ruanrodrigues20/Post-Install-Linux.git && cd Post-Install-Linux && bash ./main.sh
```


## 📜 License

See `LICENSE.txt` for license information.
