# src/guards/utils.py
import hashlib
import json
from typing import Dict, Any

def calcular_hash(data: Dict[str, Any]) -> str:
    """Genera un hash SHA-256 determinista de un diccionario."""
    # sort_keys=True asegura que el orden de las llaves no altere el hash
    encoded = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()