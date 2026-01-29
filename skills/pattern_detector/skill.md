---
skill_id: "pattern_detector"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Detecta patrones anómalos: structuring, velocity, geográficos"

category: "analysis"
domain: "fraud"
agents: ["orchestrator", "risk"]

dependencies:
  data_sources:
    - transactions
    - customers
  other_skills:
    - customer_360
  external_apis: []

capabilities:
  - Detectar patrones de structuring
  - Identificar anomalías de velocity
  - Detectar patrones geográficos sospechosos
  - Calcular scores de confianza por patrón

limitations:
  - Requiere histórico mínimo de 30 días
  - No detecta patrones cross-entity (usar relationship_mapper)
  - Umbrales configurables pueden generar FP

references:
  - id: "structuring_rules"
    path: "references/structuring_rules.md"
    description: "Reglas de detección de structuring"
  - id: "velocity_thresholds"
    path: "references/velocity_thresholds.md"
    description: "Umbrales de velocity por perfil"
  - id: "anomaly_baselines"
    path: "references/anomaly_baselines.md"
    description: "Baselines para detección de anomalías"
---

# Pattern Detector

## Propósito

Analiza transacciones de un cliente para **detectar patrones anómalos** indicativos de actividad sospechosa. Utiliza reglas configurables y comparación con baselines históricos.

## Cuándo Usar Este Skill

- Al investigar alertas de comportamiento
- Para análisis proactivo de clientes de alto riesgo
- Durante revisiones EDD periódicas
- Cuando se detectan desviaciones en customer_360

## Cuándo NO Usar Este Skill

- Para análisis de redes (usar relationship_mapper)
- Con clientes nuevos (<30 días histórico)
- Para decisiones finales (usar decision_explainer)

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| customer_id | string | Sí | ID del cliente a analizar |
| pattern_types | array[string] | No | Tipos: STRUCTURING, VELOCITY, GEOGRAPHIC, ALL |
| time_window_days | integer | No | Ventana de análisis (default: 90) |
| sensitivity | string | No | LOW, MEDIUM, HIGH (default: MEDIUM) |

## Output Esperado

```json
{
  "customer_id": "C-4821",
  "analysis_period": {
    "start": "2024-11-01",
    "end": "2025-01-29"
  },
  "patterns_detected": [
    {
      "pattern_type": "STRUCTURING",
      "confidence": 0.85,
      "severity": "HIGH",
      "details": {
        "description": "Múltiples depósitos en efectivo justo bajo umbral",
        "transaction_count": 12,
        "total_amount": 34500,
        "average_amount": 2875,
        "threshold_reference": 3000,
        "time_clustering": "4 días"
      },
      "transactions_involved": ["TX-001", "TX-002", "..."],
      "recommendation": "Investigar origen de fondos"
    }
  ],
  "patterns_not_detected": ["VELOCITY", "GEOGRAPHIC"],
  "baseline_comparison": {
    "monthly_average": {"baseline": 5000, "current": 12000, "deviation": "+140%"},
    "transaction_count": {"baseline": 20, "current": 45, "deviation": "+125%"}
  },
  "overall_risk_score": 72,
  "recommendation": "Requiere investigación - múltiples indicadores de structuring"
}
```

## Tipos de Patrones

### STRUCTURING
Transacciones fragmentadas para evitar umbrales.
- Depósitos/retiros justo bajo 3,000 EUR
- Transferencias justo bajo 10,000 EUR
- Múltiples operaciones en ventana corta

### VELOCITY
Cambios bruscos en frecuencia/volumen.
- Incremento >200% vs baseline
- Cuenta dormant reactivada
- Burst de actividad en <48h

### GEOGRAPHIC
Operativa en ubicaciones inusuales.
- Nuevo país de alto riesgo
- Cambio rápido de ubicación física
- Transacciones desde IP/países inconsistentes

## Consideraciones de Compliance

### Ley 10/2010 Art. 17
- Los patrones detectados pueden activar examen especial
- Documentar hallazgos independientemente de decisión final

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
