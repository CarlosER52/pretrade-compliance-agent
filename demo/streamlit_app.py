# demo/streamlit_app.py
import streamlit as st
import time
import json
import uuid
from datetime import datetime, timezone

# Importamos nuestras piezas del backend
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rules.rules_engine import RulesEngine
from src.agents.context_agent import ContextAgent
from src.orchestrator.state_machine import PreTradeOrchestrator
from src.guards.clasificacion_guard import guarda_clasificacion_valida
from src.guards.gate_guard import guarda_gate_valido

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pre-Trade Compliance", layout="wide", page_icon="🛡️")

# --- INICIALIZACIÓN DE ESTADO ---
# Usamos session_state para que la app no se reinicie al hacer clic en botones
if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None
if "clasificacion" not in st.session_state:
    st.session_state.clasificacion = None

# Inicializamos el orquestador (usando datos falsos para la demo)
@st.cache_resource
def get_orchestrator():
    limites = {
        "TSLA": {"limite_posicion": 1000, "sector": "Tech"},
        "BTC": {"limite_posicion": 10, "sector": "Crypto"},
        "limites_sector": {"Tech": 25.0, "Crypto": 20.0}
    }
    # Mockeamos el agente para que la demo no dependa de una API Key real
    class MockAgent:
        def analizar_contexto(self, orden, contexto):
            time.sleep(1.5) # Simulamos latencia del LLM
            return {
                "orden_id": orden["orden_id"],
                "cliente_en_watchlist": contexto.get("en_watchlist", False),
                "patron_inusual": contexto.get("patron_inusual", False),
                "conflicto_politica": False,
                "justificacion": f"Análisis de contexto para {orden['cliente_id']}: Cliente en watchlist ({contexto.get('en_watchlist', False)}). Patrón inusual detectado ({contexto.get('patron_inusual', False)}).",
                "confianza": 0.88
            }
    
    rules_engine = RulesEngine(limites_config=limites)
    return PreTradeOrchestrator(rules_engine=rules_engine, context_agent=MockAgent())

orchestrator = get_orchestrator()

# --- INTERFAZ PRINCIPAL ---
st.title("🛡️ Pre-Trade Compliance Agent")
st.markdown("*Sistema agéntico de validación de órdenes con Gate Humano obligatorio.*")

# --- PANEL LATERAL (INPUTS) ---
with st.sidebar:
    st.header("1. Ingesta de Orden")
    
    orden_id = f"ORD-2026-{str(uuid.uuid4().int)[:5]}"
    st.text_input("ID de Orden", value=orden_id, disabled=True)
    
    cliente_id = st.selectbox("Cliente", ["CLI-4471 (Watchlist)", "CLI-9902 (Normal)"])
    instrumento = st.selectbox("Instrumento", ["TSLA", "BTC", "AAPL"])
    tipo = st.selectbox("Tipo", ["buy", "sell"])
    cantidad = st.number_input("Cantidad", min_value=1, value=500)
    
    # Contexto simulado
    st.subheader("Contexto del Cliente")
    en_watchlist = st.checkbox("Cliente en Watchlist", value=True if "4471" in cliente_id else False)
    patron_inusual = st.checkbox("Patrón Inusual", value=True if "4471" in cliente_id else False)
    posicion_actual = st.number_input("Posición Actual", min_value=0, value=800)
    
    ejecutar = st.button("🚀 Ejecutar Validación", type="primary", use_container_width=True)

# --- FLUJO PRINCIPAL ---
if ejecutar:
    # Construimos los inputs
    orden = {
        "orden_id": orden_id,
        "cliente_id": cliente_id.split(" ")[0],
        "instrumento": instrumento,
        "tipo": tipo,
        "cantidad": cantidad,
        "cuenta_id": "ACC-123"
    }
    contexto_cliente = {
        "posicion_actual": posicion_actual,
        "en_watchlist": en_watchlist,
        "patron_inusual": patron_inusual,
        "valor_orden": cantidad * 100, # Simulado
        "valor_portafolio": 1000000,
        "exposicion_sector": 15.0 if instrumento == "TSLA" else 5.0
    }

    # Simulamos el avance visual del Statechart
    with st.status("Ejecutando Workflow...", expanded=True) as status:
        st.write("⏳ Validando Schema de la orden...")
        time.sleep(0.5)
        st.write("✅ Schema validado correctamente.")
        
        st.write("⚙️ Ejecutando 4 Reglas Duras (determinista)...")
        time.sleep(1)
        
        # Llamamos al orquestador real
        state = orchestrator.ejecutar_flujo(orden, contexto_cliente)
        
        if state.get("error"):
            st.error(f"❌ Error en el flujo: {state['error']}")
            status.update(label="Workflow detenido por error.", state="error")
        else:
            st.write("🤖 Agente de IA analizando contexto...")
            time.sleep(1)
            st.write("📊 Clasificando riesgo...")
            time.sleep(0.5)
            
            st.session_state.workflow_state = state
            st.session_state.clasificacion = state["artefactos"]["clasificacion_riesgo"]
            
            status.update(label="Workflow pausado. Esperando revisión humana.", state="complete")

# --- RENDERIZADO DEL GATE HUMANO ---
if st.session_state.workflow_state and st.session_state.workflow_state["estado_actual"] == "REVISION_HUMANA":
    state = st.session_state.workflow_state
    artefactos = state["artefactos"]
    
    st.divider()
    
    # Dividimos la pantalla en dos columnas: Artefactos vs Decisión
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("2. Análisis del Sistema")
        
        # Mostramos las Reglas Duras
        st.subheader("Reglas Duras (Deterministas)")
        validacion = artefactos["validacion_reglas"]
        if validacion["fallos_total"] > 0:
            st.error(f"❌ {validacion['fallos_total']} regla(s) fallida(s)")
        else:
            st.success("✅ Todas las reglas pasaron")
            
        with st.expander("Ver detalle de reglas"):
            st.json(validacion)
            
        # Mostramos el Análisis del Agente
        st.subheader("Análisis de Contexto (Agente IA)")
        analisis = artefactos["analisis_contexto"]
        st.info(f"**Justificación:** {analisis['justificacion']}")
        st.write(f"**Confianza:** {analisis['confianza'] * 100}%")
        
        # Mostramos la Clasificación Final
        st.subheader("Clasificación de Riesgo Final")
        clasificacion = artefactos["clasificacion_riesgo"]
        
        color = "red" if clasificacion["riesgo"] in ["HIGH", "CRITICAL"] else "orange" if clasificacion["riesgo"] == "MEDIUM" else "green"
        st.markdown(f"### Riesgo: :{color}[**{clasificacion['riesgo']}**]")
        
        if clasificacion.get("piso_aplicado"):
            st.warning("⚠️ **Piso de Reglas Duras Aplicado:** El agente intentó bajar el riesgo, pero la guarda lo bloqueó.")

    with col2:
        st.header("3. Gate Humano")
        st.markdown("Como Compliance Officer, revisa el análisis y toma una decisión.")
        
        with st.form("gate_form"):
            decision = st.radio("Decisión", ["APROBADA", "RECHAZADA"])
            justificacion = st.text_area("Justificación (mín. 20 caracteres)", 
                                         placeholder="Explica por qué apruebas o rechazas esta orden...")
            
            oficial_id = st.text_input("Oficial ID", value="oficial_humano_007")
            
            submit = st.form_submit_button("Firmar y Enviar", type="primary", use_container_width=True)
            
            if submit:
                if len(justificacion) < 20:
                    st.error("La justificación debe tener al menos 20 caracteres.")
                else:
                    # Ejecutamos la decisión en el orquestador
                    success, error, final_state = orchestrator.procesar_decision_humana(
                        workflow_state=state,
                        decision=decision,
                        oficial_id=oficial_id,
                        justificacion=justificacion
                    )
                    
                    if not success:
                        st.error(f"❌ Guarda bloqueó la decisión: {error}")
                    else:
                        st.session_state.workflow_state = final_state
                        st.success("✅ Decisión registrada y archivada.")
                        st.rerun() # Refrescamos para mostrar el estado final

# --- ESTADO FINAL (AUDITORÍA) ---
if st.session_state.workflow_state and st.session_state.workflow_state["estado_actual"] == "ARCHIVADA":
    st.divider()
    st.header("4. Auditoría y Archivo")
    st.success("El workflow ha finalizado. El Audit Trail ha sido generado.")
    
    with st.expander("Ver Audit Trail (JSON)"):
        st.json(st.session_state.workflow_state["artefactos"]["audit_trail"])
        
    if st.button("Reiniciar Demo"):
        st.session_state.workflow_state = None
        st.session_state.clasificacion = None
        st.rerun()