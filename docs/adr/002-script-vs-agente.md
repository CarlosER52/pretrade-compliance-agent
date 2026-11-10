# ADR-002: Script para clasificación base, Agente solo para contexto

## Status
Accepted

## Context
We need to evaluate financial orders against compliance rules and analyze unstructured context (e.g., client history, unusual patterns). We could use an LLM for everything: reading the JSON, applying position limits, and analyzing context. However, LLMs are expensive, slow, and non-deterministic. Applying hard mathematical limits (like 10% concentration) via an LLM introduces a high risk of hallucination or miscalculation.

## Decision
We split the work based on task nature:
1.  **Deterministic Script:** Handles schema validation, position limits, restricted lists, and basic risk scoring. This is fast, free, and 100% accurate.
2.  **AI Agent:** Only handles the `analisis_contexto` state. It reads unstructured data (watchlists, trading history) and outputs a structured JSON with a confidence score and justification.

## Consequences
*   **Positive:** The most critical part (math and limits) is deterministic and cheap. The AI is used where it shines (interpreting context), not where it fails (math).
*   **Negative:** We need a hybrid pipeline (script + AI), which adds architectural complexity compared to a single "AI wrapper".

---
*(Versión en Español)*
# ADR-002: Script para clasificación base, Agente solo para contexto

## Estado
Aceptado

## Contexto
Necesitamos evaluar órdenes financieras contra reglas de compliance y analizar contexto no estructurado. Podríamos usar un LLM para todo. Sin embargo, los LLMs son caros, lentos y no deterministas. Aplicar límites matemáticos duros (como 10% de concentración) vía LLM introduce un alto riesgo de alucinación.

## Decisión
Dividimos el trabajo según la naturaleza de la tarea:
1. **Script Determinista:** Maneja validación de schema, límites de posición, listas restringidas y scoring básico. Es rápido, gratis y 100% exacto.
2. **Agente de IA:** Solo maneja el estado `analisis_contexto`. Lee datos no estructurados y devuelve un JSON estructurado con confianza y justificación.

## Consecuencias
*   **Positivas:** La parte más crítica es determinista y barata. La IA se usa donde brilla (interpretar contexto), no donde falla (matemáticas).
*   **Negativas:** Requiere un pipeline híbrido (script + IA), lo que añade complejidad arquitectónica.