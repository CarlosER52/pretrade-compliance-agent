# ADR-006: Input Hashing to Prevent Stale Approvals

## Status
Accepted

## Context
In a real-world scenario, a human compliance officer might take hours to review an order. During that time, the client's status could change (e.g., they get added to a sanctions list). If the officer approves the order based on the analysis they saw hours ago, they are approving stale data.

## Decision
Every classification artifact (`clasificacion_riesgo.json`) includes a `hash_inputs` field. This is a SHA-256 hash of the exact `validacion_reglas` and `analisis_contexto` used to make the decision. 
When the human submits their decision, Guard 5 recalculates the hash of the current artifacts. If the hash differs from the one the human saw, the approval is rejected with a "Stale Data" error.

## Consequences
*   **Positive:** Prevents approvals based on outdated information. Guarantees that the human decision matches the exact state of the data at the time of approval.
*   **Negative:** The human might have to re-review the order if the data changes while they are reviewing it. This is a necessary trade-off for compliance.

---
*(Versión en Español)*
# ADR-006: Hash de Inputs para Evitar Aprobaciones Obsoletas

## Estado
Aceptado

## Contexto
En el mundo real, un oficial de compliance puede tardar horas en revisar una orden. Durante ese tiempo, el estado del cliente puede cambiar (ej. es añadido a una lista de sanciones). Si el oficial aprueba basándose en el análisis de hace horas, está aprobando datos obsoletos.

## Decisión
Cada artefacto de clasificación incluye un campo `hash_inputs`. Es un hash SHA-256 de los datos exactos usados para la decisión. Cuando el humano envía su decisión, la Guarda 5 recalcula el hash. Si difiere del que vio el humano, la aprobación se rechaza con un error de "Datos Obsoletos".

## Consecuencias
*   **Positivas:** Evita aprobaciones basadas en información desactualizada. Garantiza que la decisión humana coincide con el estado exacto de los datos.
*   **Negativas:** El humano podría tener que re-revisar la orden si los datos cambian mientras la revisa. Es un trade-off necesario en compliance.