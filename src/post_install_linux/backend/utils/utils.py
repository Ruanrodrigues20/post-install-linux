import subprocess
import sys
import os
import json
from post_install_linux.backend.env import JSON_DIR, DISTRO


def run_cmd(cmd, cwd=None, sudo=False, check=False, capture_output=False):
    if sudo:
        cmd = ["sudo"] + cmd
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(1)
    return result
def run_cmd(cmd, cwd=None, sudo=False, check=False, capture_output=False, password=None):
    if sudo:
        if password is None:
            raise ValueError("⚠️ Você deve fornecer a senha quando sudo=True.")
        full_cmd = ['sudo', '-S'] + cmd
    else:
        full_cmd = cmd

    try:
        if capture_output:
            # Usa subprocess.run para capturar output e returncode
            result = subprocess.run(
                full_cmd,
                cwd=cwd,
                input=(password + '\n') if sudo else None,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=check
            )
            return result  # CompletedProcess, tem returncode, stdout, stderr
        else:
            # Usa Popen para output direto no terminal
            proc = subprocess.Popen(
                full_cmd,
                cwd=cwd,
                stdin=subprocess.PIPE if sudo else None,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            if sudo:
                proc.stdin.write(password + '\n')
                proc.stdin.flush()
            proc.wait()
            if check and proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd)
            return proc  # Popen, tem returncode
    except Exception as e:
        print(f"❌ Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        sys.exit(1)

def get_data(distro: str, categoria: str) -> list[str]:
    json_path = os.path.join(JSON_DIR, f'{distro}.json')

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


