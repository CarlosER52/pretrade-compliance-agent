# ADR-001: Orquestador Determinista en lugar de Agente Orquestador

## Estado
Aceptado

## Contexto
El sistema requiere procesar órdenes financieras que deben pasar por múltiples validaciones y análisis antes de ser aprobadas o rechazadas. Podríamos haber utilizado un LLM (Agente) como el "cerebro" principal para decidir qué pasos tomar a continuación (ej. "decide si esta orden necesita revisión humana"). Sin embargo, en procesos *safety-critical* (críticos para la seguridad), delegar el control del flujo a un modelo probabilístico introduce un riesgo inaceptable de alucinación o saltos de pasos.

## Decisión
Hemos decidido implementar un **Orquestador Determinista** (una máquina de estados en Python). El orquestador es un script rígido que dicta exactamente qué paso sigue después de cuál, basándose en reglas lógicas (ej. `if schema_valido: pasar_a_reglas`). 

El LLM (Agente) solo es invocado en estados específicos (como el análisis de contexto) y actúa como un "trabajador" al que se le asigna una tarea delimitada, no como el "gerente" del flujo.

## Consecuencias
*   **Positivas:** El flujo es 100% predecible, testeable y auditable. Si el sistema falla, sabemos exactamente en qué estado ocurrió. Es imposible que el LLM "decida" saltarse la validación de reglas duras o el gate humano.
*   **Negativas:** La lógica de negocio está codificada en el orquestador. Si el flujo cambia, requiere modificar el código del orquestador en lugar de simplemente cambiar un *prompt*.

---
*(English version)*
# ADR-001: Deterministic Orchestrator over Agent Orchestrator

## Status
Accepted

## Context
The system requires processing financial orders that must pass through multiple validations and analyses before being approved or rejected. We could have used an LLM (Agent) as the main "brain" to decide what steps to take next (e.g., "decide if this order needs human review"). However, in safety-critical processes, delegating flow control to a probabilistic model introduces an unacceptable risk of hallucination or skipping steps.

## Decision
We have decided to implement a **Deterministic Orchestrator** (a Python state machine). The orchestrator is a rigid script that dictates exactly which step follows which, based on logical rules (e.g., `if valid_schema: go_to_rules`). 

The LLM (Agent) is only invoked at specific states (like context analysis) and acts as a "worker" assigned a bounded task, not as the "manager" of the flow.

## Consequences
*   **Positive:** The flow is 100% predictable, testable, and auditable. If the system fails, we know exactly at which state it happened. It is impossible for the LLM to "decide" to skip hard rule validation or the human gate.
*   **Negative:** Business logic is hardcoded into the orchestrator. If the flow changes, it requires modifying the orchestrator code rather than simply changing a prompt.