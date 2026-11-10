# src/guards/clasificacion_guard.py
from typing import Dict, Any, Tuple
from .utils import calcular_hash

def guarda_clasificacion_valida(
    clasificacion: Dict[str, Any], 
    validacion_reglas: Dict[str, Any], 
    analisis_contexto: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Guarda 4: Valida la clasificación del agente y aplica el piso de reglas duras.
    Retorna (True, "") si es válida, o (False, "razón del fallo") si debe bloquearse.
    """
    
    # 1. Validar que el riesgo esté en el Enum permitido
    if clasificacion.get("riesgo") not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        return False, f"Riesgo fuera de enum: {clasificacion.get('riesgo')}"

    # 2. EL PISO DE REGLAS DURAS (ADR-003)
    # Si hay fallos en las reglas, el agente NO PUEDE poner LOW o MEDIUM.
    if validacion_reglas.get("fallos_total", 0) > 0 and clasificacion.get("riesgo") in ("LOW", "MEDIUM"):
        return False, "VIOLACIÓN: Reglas duras fallidas, pero el agente intentó clasificar como riesgo bajo/medio."

    # 3. Coherencia con Watchlist
    # Si el cliente está en watchlist, el riesgo no puede ser LOW.
    if analisis_contexto.get("cliente_en_watchlist") and clasificacion.get("riesgo") == "LOW":
        return False, "VIOLACIÓN: Cliente en watchlist no puede tener riesgo LOW."

    # 4. Hash de Inputs (Trazabilidad)
    # Verifica que el agente clasificó basándose EXACTAMENTE en los datos actuales.
    # (Evita que un agente alucine usando datos de una orden anterior).
    hash_esperado = calcular_hash({
        "validacion_reglas": validacion_reglas,
        "analisis_contexto": analisis_contexto
    })
    
    if clasificacion.get("hash_inputs") != hash_esperado:
        return False, "Hash no coincide: La clasificación se hizo sobre datos obsoletos o alterados."

    return True, ""