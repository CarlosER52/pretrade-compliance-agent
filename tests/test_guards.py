# tests/test_guards.py
import pytest
from src.guards.clasificacion_guard import guarda_clasificacion_valida
from src.guards.gate_guard import guarda_gate_valido
from src.guards.utils import calcular_hash

@pytest.fixture
def validacion_reglas_fallida():
    return {"fallos_total": 1, "reglas": []}

@pytest.fixture
def contexto_watchlist():
    return {"cliente_en_watchlist": True, "patron_inusual": False}

def test_piso_reglas_duras_bloquea_ia(validacion_reglas_fallida, contexto_watchlist):
    """El agente intenta poner LOW, pero hay fallos en reglas. La guarda debe bloquear."""
    analisis = contexto_watchlist
    clasificacion_ia = {
        "riesgo": "LOW", # ¡El agente intenta hacer trampa!
        "hash_inputs": calcular_hash({"validacion_reglas": validacion_reglas_fallida, "analisis_contexto": analisis})
    }
    
    es_valido, error = guarda_clasificacion_valida(
        clasificacion_ia, validacion_reglas_fallida, analisis
    )
    
    assert es_valido is False
    assert "Reglas duras fallidas" in error

def test_gate_bloquea_aprobacion_datos_obsoletos():
    """El humano intenta aprobar, pero la clasificación cambió (hash no coincide)."""
    clasificacion_actual = {"riesgo": "HIGH", "hash_inputs": "abc"}
    
    acta = {
        "oficial": "humano_01",
        "firma": "firma_123",
        "decision": "APROBADA",
        "hash_clasificacion": "hash_viejo_123" # No coincide con la clasificación actual
    }
    
    es_valido, error = guarda_gate_valido(acta, clasificacion_actual, agente_origen_id="agente_ia")
    
    assert es_valido is False
    assert "datos obsoletos" in error

def test_gate_bloquea_autoaprobacion_agente():
    """El agente intenta firmar su propia orden como humano."""
    clasificacion = {"riesgo": "HIGH"}
    acta = {
        "oficial": "agente_ia", # ¡El agente se hace pasar por humano!
        "firma": "firma_123",
        "decision": "APROBADA",
        "hash_clasificacion": calcular_hash(clasificacion)
    }
    
    es_valido, error = guarda_gate_valido(acta, clasificacion, agente_origen_id="agente_ia")
    
    assert es_valido is False
    assert "agente de IA no puede firmar" in error