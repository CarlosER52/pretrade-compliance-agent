# evals/run_evals.py
import json
from typing import Dict, Any
# Importamos nuestras piezas del backend
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.rules.rules_engine import RulesEngine
from src.agents.context_agent import ContextAgent
from src.orchestrator.state_machine import PreTradeOrchestrator

class MockAgent:
    """Mock del agente para las evals (evita llamar a la API real)."""
    def analizar_contexto(self, orden: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "orden_id": orden["orden_id"],
            "cliente_en_watchlist": contexto.get("en_watchlist", False),
            "patron_inusual": contexto.get("patron_inusual", False),
            "conflicto_politica": False,
            "justificacion": f"Eval mock para {orden['cliente_id']}.",
            "confianza": 0.9
        }

def cargar_casos() -> list:
    ruta = os.path.join(os.path.dirname(__file__), "golden_dataset", "casos.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def ejecutar_evals():
    limites = {
        "TSLA": {"limite_posicion": 1000, "sector": "Tech"},
        "AAPL": {"limite_posicion": 1000, "sector": "Tech"},
        "MSFT": {"limite_posicion": 1000, "sector": "Tech"},
        "NVDA": {"limite_posicion": 1000, "sector": "Tech"},
        "AMZN": {"limite_posicion": 1000, "sector": "Tech"},
        "BABA": {"limite_posicion": 1000, "sector": "Tech"},
        "limites_sector": {"Tech": 25.0}
    }
    rules_engine = RulesEngine(limites_config=limites)
    orchestrator = PreTradeOrchestrator(rules_engine=rules_engine, context_agent=MockAgent())
    
    casos = cargar_casos()
    aciertos = 0
    falsos_positivos = 0
    falsos_negativos = 0

    print(f"{'ID':<10} | {'Esperado':<10} | {'Obtenido':<10} | {'Piso':<5} | {'Resultado'}")
    print("-" * 60)

    for caso in casos:
        state = orchestrator.ejecutar_flujo(caso["orden"], caso["contexto"])
        
        if state.get("error"):
            print(f"{caso['id']:<10} | ERROR: {state['error']}")
            continue
            
        clasificacion = state["artefactos"]["clasificacion_riesgo"]
        riesgo_obtenido = clasificacion["riesgo"]
        riesgo_esperado = caso["esperado"]["riesgo"]
        piso_obtenido = clasificacion.get("piso_aplicado", False)
        piso_esperado = caso["esperado"]["piso_aplicado"]
        
        # Lógica de evaluación
        if riesgo_obtenido == riesgo_esperado and piso_obtenido == piso_esperado:
            resultado = "✅ PASS"
            aciertos += 1
        else:
            resultado = "❌ FAIL"
            # Detectamos si es un falso positivo (escaló de más) o falso negativo (escaló de menos)
            if riesgo_obtenido in ["HIGH", "CRITICAL"] and riesgo_esperado in ["LOW", "MEDIUM"]:
                falsos_positivos += 1
            elif riesgo_obtenido in ["LOW", "MEDIUM"] and riesgo_esperado in ["HIGH", "CRITICAL"]:
                falsos_negativos += 1
        
        print(f"{caso['id']:<10} | {riesgo_esperado:<10} | {riesgo_obtenido:<10} | {str(piso_obtenido):<5} | {resultado}")

    print("-" * 60)
    total = len(casos)
    accuracy = (aciertos / total) * 100 if total > 0 else 0
    
    print(f"📊 RESUMEN DE EVALUACIÓN:")
    print(f"  Total de casos: {total}")
    print(f"  Aciertos (Accuracy): {aciertos}/{total} ({accuracy:.1f}%)")
    print(f"  Tasa de Falsos Positivos: {falsos_positivos}/{total} ({(falsos_positivos/total)*100:.1f}%)")
    print(f"  Tasa de Falsos Negativos: {falsos_negativos}/{total} ({(falsos_negativos/total)*100:.1f}%)")

if __name__ == "__main__":
    ejecutar_evals()