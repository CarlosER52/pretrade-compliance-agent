# src/guards/gate_guard.py
from typing import Dict, Any, Tuple
from .utils import calcular_hash

def guarda_gate_valido(
    acta_compliance: Dict[str, Any], 
    clasificacion: Dict[str, Any], 
    agente_origen_id: str
) -> Tuple[bool, str]:
    """
    Guarda 5: Valida la decisión del oficial humano.
    """
    
    # 1. Firma y oficial presentes
    if not acta_compliance.get("firma") or not acta_compliance.get("oficial"):
        return False, "Firma u oficial ausentes en el acta."

    # 2. Hash coincide (Evita aprobar datos obsoletos)
    # El acta debe tener el hash de la clasificación exacta que el humano vio en pantalla.
    hash_actual_clasificacion = calcular_hash(clasificacion)
    if acta_compliance.get("hash_clasificacion") != hash_actual_clasificacion:
        return False, "El oficial aprobó datos obsoletos (el hash de la clasificación no coincide)."

    # 3. Conflicto de interés (El agente no puede aprobar su propio trabajo)
    if acta_compliance.get("oficial") == agente_origen_id:
        return False, "VIOLACIÓN: El agente de IA no puede firmar como oficial humano."

    # 4. Rechazo requiere justificación
    if acta_compliance.get("decision") == "RECHAZADA":
        justificacion = acta_compliance.get("justificacion", "")
        if len(justificacion) < 20:
            return False, "Rechazo sin justificación suficiente (mínimo 20 caracteres)."

    return True, ""