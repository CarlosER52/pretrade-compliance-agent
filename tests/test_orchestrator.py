# tests/test_orchestrator.py
import pytest
from unittest.mock import MagicMock
from src.orchestrator.state_machine import PreTradeOrchestrator
from src.rules.rules_engine import RulesEngine
from src.agents.context_agent import ContextAgent

@pytest.fixture
def mock_agent():
    agent = MagicMock(spec=ContextAgent)
    agent.analizar_contexto.return_value = {
        "orden_id": "ORD-2026-00001",
        "cliente_en_watchlist": True,
        "patron_inusual": True,
        "conflicto_politica": False,
        "justificacion": "El cliente está en watchlist y tiene un patrón inusual.",
        "confianza": 0.9
    }
    return agent

@pytest.fixture
def orchestrator(mock_agent):
    limites = {"TSLA": {"limite_posicion": 1000, "sector": "Tech"}, "limites_sector": {"Tech": 25.0}}
    rules_engine = RulesEngine(limites_config=limites)
    return PreTradeOrchestrator(rules_engine=rules_engine, context_agent=mock_agent)

def test_flujo_completo_hasta_rechazo_humano(orchestrator):
    """Prueba el happy path y luego el rechazo humano."""
    orden = {
        "orden_id": "ORD-2026-00001",
        "cliente_id": "CLI-001",
        "instrumento": "TSLA",
        "tipo": "buy",
        "cantidad": 500, # Esto generará un fallo de posición si el contexto tiene 800
        "cuenta_id": "ACC-123"
    }
    contexto = {"posicion_actual": 800} # 800 + 500 = 1300 > 1000 (Falla R1)

    # 1. Ejecutamos el flujo hasta el Gate
    state = orchestrator.ejecutar_flujo(orden, contexto)
    
    assert state["estado_actual"] == "REVISION_HUMANA"
    assert state["artefactos"]["clasificacion_riesgo"]["riesgo"] == "HIGH"
    assert state["artefactos"]["validacion_reglas"]["fallos_total"] == 1

    # 2. Simulamos la decisión del humano (Rechazar)
    success, error, final_state = orchestrator.procesar_decision_humana(
        workflow_state=state,
        decision="RECHAZADA",
        oficial_id="oficial_humano_007",
        justificacion="La orden excede el límite de posición permitido para este cliente."
    )

    assert success is True
    assert error == ""
    assert final_state["estado_actual"] == "ARCHIVADA"
    assert final_state["artefactos"]["acta_compliance"]["decision"] == "RECHAZADA"
    assert "audit_trail" in final_state["artefactos"]