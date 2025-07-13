import os
import subprocess

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



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../../data')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')
JSON_DIR = os.path.join(DATA_DIR, 'json')
ZIP_DIR = os.path.join(DATA_DIR, 'zip')
DISTRO = get_distro()