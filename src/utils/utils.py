import subprocess
import sys
import os
import json
from src.utils.system import get_distro



# Caminho absoluto para o diretório onde está o script atual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto para a pasta data
DATA_DIR = os.path.join(BASE_DIR, '../../data')

def get_data(distro: str, categoria: str) -> list[str]:
    json_path = os.path.join(DATA_DIR, f'{distro}.json')

    if not os.path.isfile(json_path):
        print(f"⚠️ JSON file not found: {json_path}")
        return []

    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Error decoding JSON file: {json_path}")
            return []

    return data.get(categoria, [])




def check_connection():    
    try:
        # Primeiro tenta 1.1.1.1
        subprocess.run(["ping", "-c", "1", "1.1.1.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        connected = True
    except subprocess.CalledProcessError:
        # Se 1.1.1.1 falhar, tenta google.com
        try:
            subprocess.run(["ping", "-c", "1", "google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            connected = True
        except subprocess.CalledProcessError:
            connected = False

    if not connected:
        print("\033[1;31m❌ No internet connection detected. Please check your network.\033[0m")
        sys.exit(1)

def ask_to_restart():
    DISTRO = get_distro()
    if DISTRO == "arch":
        subprocess.run(["yay", "-Sy", "--aur", "--devel", "--timeupdate"])
        subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/yay/completion.cache")])
        subprocess.run(["yay", "-Syu"])

    print("\033[1;34m===== 🔥 Installing Finished =====\033[0m")

    choice = input("Do you want to restart your system now? (y/n): ") 
    if choice.lower() == 'y':
        print("\033[1;34m🔄 Restarting your system...\033[0m")
        subprocess.run(["sudo", "systemctl", "reboot"])
    else:
        print("\033[1;33m⚠️ You can restart later to complete the installation.\033[0m")


def detect_battery() -> bool:
    """
    Verifica se o sistema possui uma bateria (BAT0 ou BAT1).

    Returns:
        bool: True se houver bateria, False caso contrário.
    """
    return (
        os.path.isdir("/sys/class/power_supply/BAT0") or
        os.path.isdir("/sys/class/power_supply/BAT1")
    )


