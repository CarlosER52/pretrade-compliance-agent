# ADR-005: Artifacts as Immutable Contracts

## Status
Accepted

## Context
As an order moves through the state machine, data is passed between scripts and AI agents. If an agent hallucinates a new field or returns a string instead of a boolean, the system could crash or make wrong decisions. We need a way to guarantee data integrity at every step.

## Decision
We defined 5 JSON Schemas (using Draft-07) for the artifacts that travel between states: `orden`, `validacion_reglas`, `analisis_contexto`, `clasificacion_riesgo`, and `acta_compliance`. 
The AI agent's output is strictly validated against `analisis_contexto.schema.json` (with `additionalProperties: false`). If the LLM returns invalid data, the system throws an error and the transition is blocked.

## Consequences
*   **Positive:** Data integrity is mathematically guaranteed. The AI cannot inject unexpected fields or wrong data types into the pipeline.
*   **Negative:** Every change to an artifact's structure requires updating the schema, the code, and the tests. This slows down rapid prototyping but ensures production safety.

---
*(Versión en Español)*
# ADR-005: Artefactos como Contratos Inmutables

## Estado
Aceptado

## Contexto
A medida que una orden avanza por la máquina de estados, los datos pasan entre scripts y agentes de IA. Si un agente alucina un campo nuevo o devuelve un string en lugar de un booleano, el sistema podría fallar. Necesitamos garantizar la integridad de los datos en cada paso.

## Decisión
Definimos 5 JSON Schemas para los artefactos que viajan entre estados. La salida del agente se valida estrictamente contra `analisis_contexto.schema.json` (con `additionalProperties: false`). Si el LLM devuelve datos inválidos, el sistema lanza un error y bloquea la transición.

## Consecuencias
*   **Positivas:** La integridad de los datos está garantizada matemáticamente. La IA no puede inyectar campos inesperados.
*   **Negativas:** Cada cambio en la estructura de un artefacto requiere actualizar el schema, el código y los tests. Ralentiza el prototipado pero asegura la producción.