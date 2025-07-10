import subprocess
import sys

def _get_distro():
    """
    Get the name of the Linux distribution from /etc/os-release.
    Returns the distribution name as a string, or None if not found.
    """
    result = subprocess.run(
        ["cat", "/etc/os-release"],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.strip().split("\n"):
        if line.startswith("NAME="):
            # Remove NAME= e possíveis aspas
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None  # se não achar


def get_distro():
    """
    return this system's distribution name
    """
    type_distro = ""
    distro = _get_distro().lower()
    if "fedora" in distro:
        type_distro = "fedora"
    elif "debian" in distro or "ubuntu" in distro or "linuxmint" in distro or "pop!_os" in distro:
        type_distro = "debian"
    elif "arch" in distro:
        type_distro = "arch"
    else:
        raise ValueError(f"Unsupported distribution: {distro}")
    return type_distro


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



if __name__ == "__main__":
    name = D
    print(name)
    check_connection()
