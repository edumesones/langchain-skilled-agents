---
skill_id: "history_analyzer"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Analiza historial de alertas y decisiones previas del cliente"

category: "analysis"
domain: "aml"
agents: ["orchestrator", "risk", "compliance"]

dependencies:
  data_sources:
    - alerts
    - customers
  other_skills: []
  external_apis: []

capabilities:
  - Recuperar historial completo de alertas
  - Analizar patrones de recurrencia
  - Calcular métricas de reincidencia
  - Identificar evolución del riesgo

limitations:
  - Solo datos internos (no bases externas)
  - Histórico limitado a 10 años
  - No predice futuras alertas

references:
  - id: "recidivism_factors"
    path: "references/recidivism_factors.md"
    description: "Factores de reincidencia y su peso"
  - id: "temporal_analysis"
    path: "references/temporal_analysis.md"
    description: "Análisis de patrones temporales"
---

# History Analyzer

## Propósito

Analiza el **historial de alertas y decisiones** de un cliente para entender su trayectoria de riesgo, identificar patrones de recurrencia y contextualizar alertas actuales.

## Cuándo Usar Este Skill

- Antes de tomar decisiones en alertas actuales
- Para contextualizar el riesgo de un cliente
- Durante revisiones EDD
- Para identificar clientes con alertas recurrentes

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| customer_id | string | Sí | ID del cliente |
| include_related | boolean | No | Incluir alertas de entidades relacionadas |
| time_range_years | integer | No | Años hacia atrás (default: 5, max: 10) |

## Output Esperado

```json
{
  "customer_id": "C-4821",
  "analysis_period": "2020-01-29 to 2025-01-29",

  "summary": {
    "total_alerts": 5,
    "by_outcome": {
      "CLOSED_FP": 3,
      "CLOSED_NO_ACTION": 1,
      "SAR_FILED": 1
    },
    "by_type": {
      "STRUCTURING": 2,
      "VELOCITY": 2,
      "PEP": 1
    }
  },

  "recurrence_analysis": {
    "recurrence_rate": 0.4,
    "average_time_between_alerts_days": 180,
    "is_recurring_offender": true,
    "escalation_trend": "STABLE"
  },

  "risk_evolution": {
    "initial_risk_category": "LOW",
    "current_risk_category": "MEDIUM",
    "trajectory": "INCREASING",
    "key_events": [
      {"date": "2023-09-20", "event": "SAR filed", "impact": "+15 risk score"}
    ]
  },

  "timeline": [
    {
      "date": "2023-09-15",
      "alert_id": "ALT-1001",
      "type": "STRUCTURING",
      "outcome": "SAR_FILED",
      "amount": 45000
    }
  ],

  "recommendations": [
    "Cliente con SAR previo - aplicar escrutinio reforzado",
    "Patrón de alertas STRUCTURING recurrente"
  ]
}
```

## Métricas Clave

### Tasa de Recurrencia
```
recurrence_rate = alertas_en_periodo / años_como_cliente
```

### Escalation Trend
- **IMPROVING:** Cada vez menos alertas y/o menor severidad
- **STABLE:** Sin cambio significativo
- **DETERIORATING:** Más alertas y/o mayor severidad

## Consideraciones de Compliance

### Art. 11 Ley 10/2010
- El historial de alertas es factor para EDD
- Clientes con SAR previo requieren monitorización reforzada

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
