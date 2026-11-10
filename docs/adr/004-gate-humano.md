# ADR-004: Mandatory Human Gate and Conflict of Interest

## Status
Accepted

## Context
The system classifies risk and generates a recommendation. In financial compliance, an AI cannot legally or ethically approve an order. Furthermore, if the AI agent that analyzes the context could also "approve" the order, it would create a structural conflict of interest (the agent auditing its own work).

## Decision
We implemented a mandatory `REVISION_HUMANA` state (Human Gate) for any order with a risk of MEDIUM or higher. 
1.  **Human Signature:** The transition to `APROBADA` or `RECHAZADA` requires a digital signature and an official ID.
2.  **Guard 5 (Conflict of Interest):** The `oficial_id` must be different from the `agente_origen_id`. The system structurally rejects the approval if the agent tries to sign as a human.
3.  **Justification:** Rejecting an order requires a mandatory justification of at least 20 characters.

## Consequences
*   **Positive:** Legal and ethical compliance. The human has the final say, and the system prevents automated self-approval.
*   **Negative:** The process is not fully automated. It requires human availability, which can be a bottleneck (mitigated by only escalating MEDIUM+ risks).

---
*(Versión en Español)*
# ADR-004: Gate Humano Obligatorio y Conflicto de Interés

## Estado
Aceptado

## Contexto
El sistema clasifica el riesgo y genera una recomendación. En compliance financiero, una IA no puede aprobar una orden legal ni éticamente. Además, si el agente que analiza el contexto pudiera "aprobar", crearía un conflicto de interés estructural.

## Decisión
Implementamos un estado obligatorio de `REVISION_HUMANA` para cualquier orden con riesgo MEDIUM o superior.
1. **Firma Humana:** La transición a `APROBADA` o `RECHAZADA` requiere firma digital e ID de oficial.
2. **Guarda 5 (Conflicto de Interés):** El `oficial_id` debe ser distinto del `agente_origen_id`. El sistema rechaza estructuralmente la aprobación si el agente intenta firmar como humano.
3. **Justificación:** Rechazar una orden requiere justificación obligatoria de al menos 20 caracteres.

## Consecuencias
*   **Positivas:** Cumplimiento legal y ético. El humano tiene la última palabra y el sistema evita la auto-aprobación.
*   **Negativas:** El proceso no es 100% automático. Requiere disponibilidad humana (mitigado al escalar solo riesgos MEDIUM+).