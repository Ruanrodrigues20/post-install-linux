import json
import sys
import os

if len(sys.argv) < 2:
    print("Uso: python list_packages.py <categoria>", file=sys.stderr)
    sys.exit(1)

categoria = sys.argv[1]

# Caminho relativo do JSON a partir do diretório raiz (onde main.sh está)
json_path = os.path.join('data', 'data.json')

with open(json_path) as f:
    data = json.load(f)

pacotes = data.get(categoria, [])

if not pacotes:
    sys.exit(1)

print(' '.join(pacotes))
