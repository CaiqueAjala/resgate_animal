import json
import os
from typing import List, Dict, Any

JSON_FILE = "pets.json"

INICIATIVA_INFO = {
    "nome": "Adoção de Pets Salvador",
    "cidade": "Salvador - BA",
    "chave_pix": "adocaodepetsssa@gmail.com",
    "tipo_chave": "E-mail",
    "titular": "Iniciativa Resgate e Adoção",
    "whatsapp": "(71) 91096096"
}

def carregar_pets() -> List[Dict[Any, Any]]:
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_pets(pets: List[Dict[Any, Any]]):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(pets, f, ensure_ascii=False, indent=4)

def obter_info_iniciativa():
    return INICIATIVA_INFO

def obter_animais_por_especie(especie: str):
    pets = carregar_pets()
    return [pet for pet in pets if pet["especie"] == especie]

def adicionar_novo_pet(novo_pet: dict):
    pets = carregar_pets()
    # Gera um ID automático
    novo_id = max([p["id"] for p in pets], default=0) + 1
    novo_pet["id"] = novo_id
    pets.append(novo_pet)
    salvar_pets(pets)