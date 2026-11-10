# tests/test_agents.py
import pytest
from unittest.mock import patch, MagicMock
from src.agents.context_agent import ContextAgent

@pytest.fixture
def mock_openai_response():
    """Simula una respuesta válida de OpenAI."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '''
    {
      "cliente_en_watchlist": true,
      "patron_inusual": true,
      "conflicto_politica": false,
      "justificacion": "El cliente está en watchlist y la orden es 3x su promedio histórico.",
      "confianza": 0.95
    }
    '''
    return mock_response

@patch('src.agents.context_agent.OpenAI')
def test_agente_analiza_contexto_exitosamente(mock_openai_class, mock_openai_response):
    """Prueba que el agente procesa y valida correctamente una respuesta del LLM."""
    # Configuramos el mock para que devuelva la respuesta falsa
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_openai_response
    mock_openai_class.return_value = mock_client

    agente = ContextAgent(api_key="fake_key")
    orden = {"orden_id": "ORD-2026-00001", "instrumento": "TSLA"}
    contexto = {"historial": "cliente tiene 3 años"}

    resultado = agente.analizar_contexto(orden, contexto)

    # Aserciones
    assert resultado["orden_id"] == "ORD-2026-00001"
    assert resultado["cliente_en_watchlist"] is True
    assert resultado["confianza"] == 0.95
    assert len(resultado["justificacion"]) >= 20

@patch('src.agents.context_agent.OpenAI')
def test_agente_falla_si_llm_alucina(mock_openai_class):
    """Prueba que la validación de Schema bloquea un output inválido del LLM."""
    mock_response = MagicMock()
    # El LLM alucina un campo extra y olvida uno obligatorio
    mock_response.choices[0].message.content = '{"cliente_en_watchlist": "SÍ", "justificacion": "corta"}'
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    agente = ContextAgent(api_key="fake_key")
    
    with pytest.raises(RuntimeError, match="Fallo en el Agente de Contexto"):
        agente.analizar_contexto({"orden_id": "ORD-1", "instrumento": "TSLA"}, {})