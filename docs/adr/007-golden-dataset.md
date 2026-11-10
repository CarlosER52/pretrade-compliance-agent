# ADR-007: Idempotency and Golden Dataset for Evals

## Status
Accepted

## Context
We need to ensure two things:
1.  **Idempotency:** If the archiving process fails and retries, we must not create duplicate audit records.
2.  **Quality Control:** We need a way to measure if our AI agent and rules engine are working correctly, especially as we change prompts or rules.

## Decision
1.  **Idempotency:** The `audit_trail.json` includes an `idempotency_key` generated from the `orden_id` and `timestamp_decision`. The archive script checks this key before writing.
2.  **Golden Dataset:** We created `evals/golden_dataset/casos.json` with 10 synthetic test cases (covering edge cases like watchlists, multiple rule failures, and restricted instruments). The `run_evals.py` script runs the orchestrator against these cases and calculates Accuracy, False Positives, and False Negatives.

## Consequences
*   **Positive:** We can mathematically prove the system's quality (currently 100% accuracy on the golden dataset). We prevent duplicate audit records.
*   **Negative:** The golden dataset is synthetic and limited to 10 cases. It does not cover every possible market scenario, but it serves as a baseline regression test.

---
*(Versión en Español)*
# ADR-007: Idempotencia y Golden Dataset para Evals

## Estado
Aceptado

## Contexto
Necesitamos asegurar dos cosas:
1. **Idempotencia:** Si el proceso de archivado falla y se reintenta, no debemos crear registros duplicados.
2. **Control de Calidad:** Necesitamos medir si nuestro agente y motor de reglas funcionan correctamente.

## Decisión
1. **Idempotencia:** El `audit_trail.json` incluye una `idempotency_key` generada desde el `orden_id` y el `timestamp_decision`. El script de archivo verifica esta clave antes de escribir.
2. **Golden Dataset:** Creamos `evals/golden_dataset/casos.json` con 10 casos de prueba sintéticos. El script `run_evals.py` corre el orquestador contra estos casos y calcula Accuracy, Falsos Positivos y Falsos Negativos.

## Consecuencias
*   **Positivas:** Podemos probar matemáticamente la calidad del sistema (actualmente 100% de accuracy). Evitamos registros de auditoría duplicados.
*   **Negativas:** El golden dataset es sintético y limitado a 10 casos. No cubre todos los escenarios posibles, pero sirve como test de regresión base.