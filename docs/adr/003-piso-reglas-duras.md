# ADR-003: Piso de Reglas Duras (Contención del No Determinismo)

## Estado
Aceptado

## Contexto
El sistema utiliza un agente de IA para clasificar el riesgo de una orden (LOW, MEDIUM, HIGH, CRITICAL) basándose en el contexto (ej. si el cliente está en una lista de observación o tiene un patrón de trading inusual). Sin embargo, los LLMs son probabilísticos y pueden ser persuadidos o fallar. Existe el riesgo de que una orden que viola una regla dura determinista (ej. excede el límite de posición) sea clasificada erróneamente como "LOW" por el agente, permitiendo que se salte el gate humano.

## Decisión
Hemos implementado una **Guarda de Piso de Reglas Duras**. Si el script determinista detecta que una o más reglas duras han fallado (`fallos_total > 0`), la clasificación de riesgo final **no puede ser menor a HIGH**. 

La guarda evalúa el output del agente. Si el agente intenta clasificar como LOW o MEDIUM una orden que tiene fallos en las reglas, la guarda rechaza la transición de estado y fuerza la clasificación a HIGH (o superior), derivando la orden obligatoriamente al gate humano.

## Consecuencias
*   **Positivas:** Contención estructural del no determinismo. La IA no puede anular la lógica de negocio dura. Esto garantiza que ninguna orden que viole políticas críticas sea auto-aprobada.
*   **Negativas:** Puede generar una tasa más alta de órdenes escaladas a revisión humana (falsos positivos), pero en compliance financiero, es preferible pecar de precavido.

---
*(English version)*
# ADR-003: Hard Rule Floor (Containment of Non-Determinism)

## Status
Accepted

## Context
The system uses an AI agent to classify the risk of an order (LOW, MEDIUM, HIGH, CRITICAL) based on context (e.g., whether the client is on a watchlist or has an unusual trading pattern). However, LLMs are probabilistic and can be persuaded or fail. There is a risk that an order violating a deterministic hard rule (e.g., exceeding the position limit) is mistakenly classified as "LOW" by the agent, allowing it to bypass the human gate.

## Decision
We have implemented a **Hard Rule Floor Guardrail**. If the deterministic script detects that one or more hard rules have failed (`total_failures > 0`), the final risk classification **cannot be lower than HIGH**. 

The guardrail evaluates the agent's output. If the agent attempts to classify an order with rule failures as LOW or MEDIUM, the guardrail rejects the state transition and forces the classification to HIGH (or higher), mandatorily routing the order to the human gate.

## Consequences
*   **Positive:** Structural containment of non-determinism. The AI cannot override hard business logic. This ensures that no order violating critical policies is auto-approved.
*   **Negative:** It may generate a higher rate of orders escalated to human review (false positives), but in financial compliance, it is better to err on the side of caution.