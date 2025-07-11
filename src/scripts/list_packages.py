import json
import sys
import os


def get_data(distro: str, categoria: str) -> str:
    """
    Retorna uma string com os pacotes de uma determinada categoria e distribuição.
    
    Parâmetros:
    - distro (str): Nome da distribuição (ex: 'ubuntu')
    - categoria (str): Categoria de pacotes (ex: 'editor')

    Retorna:
    - str: Lista de pacotes separados por espaço, ou string vazia se não houver pacotes ou erro.
    """
    json_path = os.path.join('data', f'{distro}.json')

    if not os.path.isfile(json_path):
        return ""

    try:
        with open(json_path) as f:
            data = json.load(f)
    except Exception:
        return ""

    pacotes = data.get(categoria, [])
    if not pacotes:
        return ""

    return ' '.join(pacotes)
