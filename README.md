# 🛠️ Post-Install-Linux

This is a **post-install automation script for Arch Linux-based and Debian-based systems**, designed to streamline the configuration of a fresh installation.

## 📁 Project Structure

```
Post-Install-Linux/
├── main.sh               # Main script that sources and runs all modules
├── LICENSE.txt           # License file
├── scripts/              # Modular scripts for each setup task
    ├── configs.sh
    ├── install_packages.sh
    ├── list_packages.py
    ├── theme.sh
    └── utils.sh
├── packages/
    └── packages.json
└── resources
    └── fast.zip

```

## 🚀 What It Does

- ✅ Checks internet connection  
- 📦 Installs essential packages using `yay` or using `apt`
- 📦 Installs Flatpak applications  
- 🎨 Applies GTK themes  
- 🧑‍💻 Configures Git  
- 🔧 Sets up aliases and useful tools  
- 📂 Creates standard directories  
- 🔋 Configures power-saving with TLP  
- 🖼️ Applies wallpapers  
- 📃 Shows a summary and asks to restart  

## ▶️ Quick Usage

Run one of the following one-liners in your terminal:

```bash
git clone https://github.com/Ruanrodrigues20/Post-Install-ArchLinux.git && cd Post-Install-ArchLinux && bash ./main.sh
```

> ⚠️ `yay` must be installed before running this script.

## 📜 License

See `LICENSE.txt` for license information.
# post-install-linux
