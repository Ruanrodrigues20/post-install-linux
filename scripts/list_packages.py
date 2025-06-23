import json
import sys
import os

if len(sys.argv) < 3:
    print("Uso: python list_packages.py <distro> <categoria>", file=sys.stderr)
    sys.exit(1)

distro = sys.argv[1]
categoria = sys.argv[2]

# Caminho do JSON correspondente à distro
json_path = os.path.join('data', f'{distro}.json')

if not os.path.isfile(json_path):
    print(f"Arquivo JSON para '{distro}' não encontrado.", file=sys.stderr)
    sys.exit(1)

with open(json_path) as f:
    data = json.load(f)

pacotes = data.get(categoria, [])

if not pacotes:
    sys.exit(1)

print(' '.join(pacotes))
