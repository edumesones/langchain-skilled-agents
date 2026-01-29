---
skill_id: "false_positive_filter"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Identifica alertas con alta probabilidad de ser falsos positivos"

category: "analysis"
domain: "aml"
agents: ["orchestrator", "compliance"]

dependencies:
  data_sources:
    - alerts
    - customers
    - transactions
  other_skills:
    - customer_360
    - history_analyzer
  external_apis: []

capabilities:
  - Clasificar probabilidad de FP
  - Identificar patrones conocidos de FP
  - Sugerir alertas para revisión rápida
  - Aprender de decisiones históricas

limitations:
  - No toma decisiones automáticas
  - Requiere histórico de decisiones
  - Puede sugerir FP incorrectamente (siempre revisar)

references:
  - id: "fp_taxonomy"
    path: "references/fp_taxonomy.md"
    description: "Taxonomía de falsos positivos por tipo"
  - id: "learning_rules"
    path: "references/learning_rules.md"
    description: "Reglas aprendidas de histórico"
---

# False Positive Filter

## Propósito

Identifica alertas que tienen **alta probabilidad de ser falsos positivos** basándose en patrones históricos, perfil del cliente y características de la alerta. Ayuda a priorizar el trabajo del analista.

## Cuándo Usar Este Skill

- Al recibir nuevas alertas para triaje rápido
- Para identificar alertas de bajo riesgo
- En revisión de cola para optimizar recursos
- Para calibrar reglas de detección

## Cuándo NO Usar Este Skill

- Como único criterio de decisión
- Para alertas CRITICAL o SANCTIONS
- Sin revisión humana posterior

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| alert_ids | array[string] | Sí | IDs de alertas a evaluar |
| confidence_threshold | float | No | Umbral de confianza FP (default: 0.7) |

## Output Esperado

```json
{
  "results": [
    {
      "alert_id": "ALT-2850",
      "fp_probability": 0.85,
      "fp_classification": "LIKELY_FP",
      "reasons": [
        "Cliente con 5+ años sin alertas previas",
        "Monto dentro de rango normal para perfil",
        "Patrón similar a 15 FP cerrados en este segmento"
      ],
      "similar_cases_fp": 15,
      "similar_cases_sar": 1,
      "recommendation": "Revisión rápida - probable FP",
      "caveats": ["Verificar que no haya cambio reciente de comportamiento"]
    }
  ],
  "summary": {
    "total_evaluated": 10,
    "likely_fp": 6,
    "uncertain": 3,
    "likely_genuine": 1
  },
  "queue_optimization": {
    "suggested_order": ["ALT-2851", "ALT-2852", "ALT-2850"],
    "estimated_time_saved_minutes": 45
  }
}
```

## Clasificaciones

| Probabilidad FP | Clasificación | Acción Sugerida |
|-----------------|---------------|-----------------|
| > 0.8 | LIKELY_FP | Revisión rápida |
| 0.6-0.8 | POSSIBLE_FP | Revisión estándar |
| 0.4-0.6 | UNCERTAIN | Revisión detallada |
| < 0.4 | LIKELY_GENUINE | Investigación completa |

## Factores de FP

### Aumentan probabilidad FP
- Cliente con historial limpio
- Perfil justifica la actividad
- Patrón similar a FP previos del segmento
- Evento vital reciente documentado
- Actividad consistente con declaración KYC

### Reducen probabilidad FP
- Cliente con alertas previas
- SAR previo comunicado
- Perfil no justifica actividad
- País de alto riesgo involucrado
- PEP

## IMPORTANTE

**Esta herramienta es de soporte, NO de decisión.**

- Siempre revisar alertas marcadas como FP
- No cerrar automáticamente
- Usar como priorización, no como veredicto

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
