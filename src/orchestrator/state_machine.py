# src/orchestrator/state_machine.py
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

# Importamos nuestras piezas
from src.rules.rules_engine import RulesEngine
from src.agents.context_agent import ContextAgent
from src.guards.clasificacion_guard import guarda_clasificacion_valida
from src.guards.gate_guard import guarda_gate_valido
from src.guards.utils import calcular_hash

class PreTradeOrchestrator:
    def __init__(self, rules_engine: RulesEngine, context_agent: ContextAgent):
        self.rules_engine = rules_engine
        self.context_agent = context_agent

    def ejecutar_flujo(self, orden: Dict[str, Any], contexto_cliente: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el workflow hasta el Gate Humano.
        Retorna el estado final y todos los artefactos generados.
        """
        # Inicializamos el contexto (el "bowl" que se pasa entre estados)
        workflow_state = {
            "estado_actual": "ORDEN_RECIBIDA",
            "artefactos": {},
            "error": None
        }

        try:
            # 1. ESTRUCTURA_VALIDADA (Simulamos la validación de Schema aquí)
            workflow_state["artefactos"]["orden"] = orden
            workflow_state["estado_actual"] = "ESTRUCTURA_VALIDADA"

            # 2. REGLAS_EVALUADAS (Script Determinista)
            validacion_reglas = self.rules_engine.evaluar_todas(orden, contexto_cliente)
            workflow_state["artefactos"]["validacion_reglas"] = validacion_reglas
            workflow_state["estado_actual"] = "REGLAS_EVALUADAS"

            # 3. CONTEXTO_ANALIZADO (Agente de IA)
            analisis_contexto = self.context_agent.analizar_contexto(orden, contexto_cliente)
            workflow_state["artefactos"]["analisis_contexto"] = analisis_contexto
            workflow_state["estado_actual"] = "CONTEXTO_ANALIZADO"

            # 4. RIESGO_CLASIFICADO (Script + Guarda 4)
            # Aquí simulamos la lógica del clasificador (en producción, sería otro script o agente)
            clasificacion_riesgo = self._clasificar_riesgo(
                validacion_reglas, analisis_contexto
            )
            
            # Aplicamos la Guarda 4 (Piso de reglas duras)
            es_valida, error = guarda_clasificacion_valida(
                clasificacion_riesgo, validacion_reglas, analisis_contexto
            )
            if not es_valida:
                workflow_state["estado_actual"] = "ERROR_SISTEMA"
                workflow_state["error"] = f"Guarda de Clasificación falló: {error}"
                return workflow_state

            workflow_state["artefactos"]["clasificacion_riesgo"] = clasificacion_riesgo
            workflow_state["estado_actual"] = "REVISION_HUMANA" # Pausa aquí esperando al humano

        except Exception as e:
            workflow_state["estado_actual"] = "ERROR_SISTEMA"
            workflow_state["error"] = str(e)
        
        return workflow_state

    def procesar_decision_humana(
        self, 
        workflow_state: Dict[str, Any], 
        decision: str, 
        oficial_id: str, 
        justificacion: str = ""
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Se ejecuta cuando el humano presiona el botón en el Gate.
        """
        clasificacion = workflow_state["artefactos"]["clasificacion_riesgo"]
        
        # Construimos el acta de compliance
        acta = {
            "orden_id": workflow_state["artefactos"]["orden"]["orden_id"],
            "decision": decision,
            "oficial": oficial_id,
            "firma": f"FIRMA-{uuid.uuid4().hex[:8].upper()}",
            "timestamp_decision": datetime.now(timezone.utc).isoformat(),
            "hash_clasificacion": calcular_hash(clasificacion),
            "justificacion": justificacion
        }

        # Aplicamos la Guarda 5
        es_valida, error = guarda_gate_valido(acta, clasificacion, agente_origen_id="agente_ia_v1")
        
        if not es_valida:
            return False, error, workflow_state

        # Si pasa la guarda, avanzamos a APROBADA/RECHAZADA
        workflow_state["artefactos"]["acta_compliance"] = acta
        workflow_state["estado_actual"] = decision
        
        # --- AQUÍ ESTÁ EL ARREGLO ---
        # Hacemos una copia profunda (dict) de los artefactos actuales ANTES de añadir el audit_trail
        artefactos_actuales = {
            k: v for k, v in workflow_state["artefactos"].items() if k != "audit_trail"
        }

        # Simulamos el archivado (Paso final) con idempotencia
        # Usamos nuestra función centralizada en lugar de hashlib directo
        idempotency_key = calcular_hash({
            "orden_id": acta["orden_id"],
            "timestamp_decision": acta["timestamp_decision"]
        })

        workflow_state["artefactos"]["audit_trail"] = {
            "idempotency_key": idempotency_key,
            "workflow_id": str(uuid.uuid4()),
            "estado_final": decision,
            "artefactos": artefactos_actuales,
            "timestamp_archivado": datetime.now(timezone.utc).isoformat()
        }

        workflow_state["estado_actual"] = "ARCHIVADA"
        
        return True, "", workflow_state
    
    def _clasificar_riesgo(self, validacion_reglas: Dict, analisis_contexto: Dict) -> Dict[str, Any]:
        """
        Lógica base de clasificación (antes de la Guarda).
        """
        fallos = validacion_reglas["fallos_total"]
        en_watchlist = analisis_contexto["cliente_en_watchlist"]
        patron_inusual = analisis_contexto.get("patron_inusual", False)
        
        # Lógica mejorada para el Golden Dataset
        if fallos >= 2 or (en_watchlist and patron_inusual and fallos > 0):
            # Múltiples fallos o combinación peligrosa
            riesgo = "CRITICAL"
        elif fallos > 0:
            # Al menos un fallo duro
            riesgo = "HIGH"
        elif en_watchlist or patron_inusual:
            # Sin fallos duros, pero hay señales de contexto
            riesgo = "MEDIUM"
        else:
            # Todo limpio
            riesgo = "LOW"

        return {
            "orden_id": validacion_reglas["orden_id"],
            "riesgo": riesgo,
            "justificacion": f"Clasificación basada en {fallos} fallos de reglas, watchlist: {en_watchlist}, patrón inusual: {patron_inusual}.",
            "piso_aplicado": fallos > 0,
            "hash_inputs": calcular_hash({
                "validacion_reglas": validacion_reglas,
                "analisis_contexto": analisis_contexto
            })
        }