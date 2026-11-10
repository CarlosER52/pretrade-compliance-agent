# tests/test_rules.py
import pytest
from src.rules.rules_engine import RulesEngine

@pytest.fixture
def engine():
    # Configuración de límites de prueba
    limites = {
        "TSLA": {"limite_posicion": 1000, "sector": "Tech"},
        "limites_sector": {"Tech": 25.0}
    }
    return RulesEngine(limites_config=limites)

@pytest.fixture
def orden_base():
    return {
        "orden_id": "ORD-2026-00001",
        "cliente_id": "CLI-001",
        "instrumento": "TSLA",
        "tipo": "buy",
        "cantidad": 500,
        "cuenta_id": "ACC-123"
    }

def test_r1_posicion_falla(engine, orden_base):
    """Prueba que R1 falla si la posición excede el límite."""
    contexto = {"posicion_actual": 800} # 800 + 500 = 1300 > 1000
    resultado = engine.evaluar_todas(orden_base, contexto)
    
    r1 = next(r for r in resultado["reglas"] if r["regla_id"] == "R1_posicion")
    assert r1["resultado"] == "fail"
    assert "excede el límite" in r1["detalle"]
    assert resultado["fallos_total"] >= 1

def test_r2_lista_restringida_falla(engine, orden_base):
    """Prueba que R2 falla si el instrumento está en la lista."""
    orden_base["instrumento"] = "BABA" # En lista restringida simulada
    contexto = {"posicion_actual": 0}
    resultado = engine.evaluar_todas(orden_base, contexto)
    
    r2 = next(r for r in resultado["reglas"] if r["regla_id"] == "R2_lista_restringida")
    assert r2["resultado"] == "fail"

def test_r4_wash_trading_falla(engine, orden_base):
    """Prueba que R4 detecta wash trading."""
    contexto = {
        "posicion_actual": 0,
        "historial_ordenes_24h": [{"instrumento": "TSLA", "tipo": "sell"}]
    }
    resultado = engine.evaluar_todas(orden_base, contexto)
    
    r4 = next(r for r in resultado["reglas"] if r["regla_id"] == "R4_wash_trading")
    assert r4["resultado"] == "fail"
    assert "Posible wash trading" in r4["detalle"]

def test_todas_pasan(engine, orden_base):
    """Prueba el happy path."""
    contexto = {
        "posicion_actual": 100, 
        "exposicion_sector": 10.0, 
        "valor_orden": 10000, 
        "valor_portafolio": 1000000,
        "historial_ordenes_24h": []
    }
    resultado = engine.evaluar_todas(orden_base, contexto)
    assert resultado["fallos_total"] == 0