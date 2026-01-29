---
skill_id: "alert_prioritizer"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Prioriza alertas AML/fraude por severidad, SLA y contexto del cliente"

category: "compliance"
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
  - Calcular score de prioridad compuesto (0-100)
  - Ordenar cola de trabajo por urgencia
  - Identificar alertas críticas que requieren atención inmediata
  - Agrupar alertas relacionadas del mismo sujeto
  - Recomendar asignación a nivel L1/L2/L3

limitations:
  - No puede modificar el estado de las alertas
  - Requiere datos de cliente actualizados para contexto
  - Score es orientativo, decisión final es humana

references:
  - id: "severity_matrix"
    path: "references/severity_matrix.md"
    description: "Matriz de severidad por tipo de alerta y monto"
  - id: "escalation_rules"
    path: "references/escalation_rules.md"
    description: "Reglas de escalado automático y SLAs"
---

# Alert Prioritizer

## Propósito

Este skill analiza alertas pendientes y asigna una prioridad basada en múltiples factores:
- Severidad intrínseca del tipo de alerta
- Perfil de riesgo del cliente
- Proximidad al SLA
- Monto involucrado
- Patrones históricos

El objetivo es **optimizar el tiempo de los analistas** enfocándolos en casos de mayor impacto.

## Cuándo Usar Este Skill

- Al inicio del turno para ordenar la cola de trabajo
- Cuando llegan múltiples alertas simultáneamente
- Para re-priorizar ante alertas críticas nuevas
- Para identificar casos que requieren escalado inmediato
- Cuando un supervisor necesita visión general de la cola

## Cuándo NO Usar Este Skill

- Para tomar decisiones de cierre/SAR (usar `decision_explainer`)
- Para análisis profundo de una alerta específica (usar `customer_360`)
- Cuando hay una sola alerta pendiente
- Para generar reportes regulatorios (usar `case_report_generator`)

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| alert_ids | array[string] | Sí | Lista de IDs de alertas a priorizar (máx 50) |
| context | object | No | Contexto adicional (capacidad equipo, etc) |
| time_window_hours | integer | No | Ventana de SLA a considerar (default: 24) |
| include_closed | boolean | No | Incluir alertas cerradas para referencia (default: false) |

## Output Esperado

```json
{
  "prioritized_queue": [
    {
      "alert_id": "uuid",
      "priority_score": 95,
      "priority_tier": "CRITICAL",
      "recommended_assignee_level": "L2",
      "sla_remaining_hours": 2.5,
      "sla_status": "AT_RISK",
      "key_factors": [
        "PEP involucrado",
        "Monto > 50,000 EUR",
        "SLA < 4 horas"
      ],
      "related_alerts": ["uuid2", "uuid3"],
      "suggested_action": "Revisar inmediatamente - posible escalado a SEPBLAC"
    }
  ],
  "summary": {
    "total_alerts": 25,
    "critical": 2,
    "high": 5,
    "medium": 10,
    "low": 8,
    "sla_at_risk": 3,
    "sla_breached": 1
  },
  "recommendations": [
    "3 alertas del mismo cliente - considerar consolidar en un caso",
    "2 alertas críticas requieren L2 inmediato",
    "1 alerta con SLA vencido - requiere justificación"
  ]
}
```

## Flujo de Trabajo

1. **Recuperar datos** de cada alerta del sistema
2. **Enriquecer** con perfil de riesgo del cliente (via `customer_360`)
3. **Consultar historial** de alertas previas (via `history_analyzer`)
4. **Calcular score compuesto** para cada alerta usando la matriz de severidad
5. **Aplicar reglas de escalado** automático según umbrales
6. **Agrupar alertas** relacionadas (mismo cliente, misma tipología)
7. **Ordenar** por prioridad descendente
8. **Generar recomendaciones** de asignación y acciones

## Criterios de Decisión

### Matriz de Severidad Base

| Tipo Alerta | Monto < 10K | 10K-50K | 50K-150K | > 150K |
|-------------|-------------|---------|----------|--------|
| STRUCTURING | 40 | 55 | 70 | 85 |
| SANCTIONS | 80 | 90 | 95 | 100 |
| PEP | 50 | 65 | 80 | 90 |
| VELOCITY | 35 | 50 | 65 | 80 |
| GEOGRAPHIC | 45 | 60 | 75 | 85 |
| UNUSUAL_ACTIVITY | 30 | 45 | 60 | 75 |

### Modificadores

| Factor | Puntos |
|--------|--------|
| Cliente categoría HIGH risk | +15 |
| Cliente categoría PROHIBITED | +25 |
| SLA < 4 horas | +20 |
| SLA < 8 horas | +10 |
| SLA vencido | +30 |
| Alertas previas no resueltas | +10 |
| Primera alerta del cliente | -5 |
| Cliente > 5 años antigüedad | -5 |
| Alerta de modelo ML (no regla) | +5 |
| Múltiples transacciones (>5) | +10 |

### Niveles de Prioridad

| Score | Prioridad | SLA | Asignación |
|-------|-----------|-----|------------|
| 80-100 | CRITICAL | 4h | L2/Compliance Officer |
| 60-79 | HIGH | 24h | L2 |
| 40-59 | MEDIUM | 72h | L1 |
| 0-39 | LOW | 168h | L1 |

## Ejemplos de Uso

### Ejemplo 1: Priorización de Cola Matutina

**Input:**
```json
{
  "alert_ids": ["ALT-001", "ALT-002", "ALT-003", "ALT-004", "ALT-005"],
  "time_window_hours": 24
}
```

**Razonamiento:**
1. ALT-001: Tipo SANCTIONS, monto 85K, cliente HIGH risk → Score base 95 + 15 = 110 (cap 100) → CRITICAL
2. ALT-002: Tipo STRUCTURING, monto 8K, cliente MEDIUM → Score 40 → MEDIUM
3. ALT-003: Tipo PEP, monto 25K, SLA en 3h → Score 65 + 20 = 85 → CRITICAL
4. ALT-004: Tipo VELOCITY, monto 3K, cliente nuevo → Score 35 - 5 = 30 → LOW
5. ALT-005: Tipo GEOGRAPHIC, monto 12K, múltiples txs → Score 60 + 10 = 70 → HIGH

**Output:**
```json
{
  "prioritized_queue": [
    {"alert_id": "ALT-001", "priority_score": 100, "priority_tier": "CRITICAL"},
    {"alert_id": "ALT-003", "priority_score": 85, "priority_tier": "CRITICAL"},
    {"alert_id": "ALT-005", "priority_score": 70, "priority_tier": "HIGH"},
    {"alert_id": "ALT-002", "priority_score": 40, "priority_tier": "MEDIUM"},
    {"alert_id": "ALT-004", "priority_score": 30, "priority_tier": "LOW"}
  ]
}
```

### Ejemplo 2: Detección de Alertas Relacionadas

**Contexto:** 3 alertas del mismo cliente en las últimas 48 horas.

**Recomendación generada:**
```
"Las alertas ALT-010, ALT-011 y ALT-012 pertenecen al mismo cliente (C-4821).
Se recomienda:
1. Consolidar en un único caso de investigación
2. Asignar a un solo analista para visión completa
3. Considerar revisión EDD del cliente
4. Prioridad combinada: HIGH (score máximo de las 3: 72)"
```

## Consideraciones de Compliance

### GDPR (Art. 22)
- La priorización es **orientativa**, no constituye decisión automatizada
- El analista humano siempre tiene la decisión final
- Los scores deben ser explicables y auditables

### Ley 10/2010 (Art. 18)
- Los SLAs están basados en requisitos de comunicación al SEPBLAC
- Alertas de sanciones siempre son CRITICAL (comunicación en 24h)
- Mantener registro de tiempos de respuesta para auditoría

### SEPBLAC
- Comunicaciones por indicios deben realizarse "sin dilación"
- Alertas CRITICAL con tipología confirmada → preparar comunicación inmediata

## Troubleshooting

### Problema: Muchas alertas con mismo score
**Solución:** Usar timestamp de creación como desempate (FIFO)

### Problema: SLA ya vencido
**Acción:** Marcar como CRITICAL independientemente del score base. Requerir justificación del retraso.

### Problema: Cliente sin datos de riesgo
**Acción:** Asumir riesgo MEDIUM y agregar flag "MISSING_KYC_DATA" a la alerta.

## Métricas de Calidad

| Métrica | Umbral Aceptable |
|---------|------------------|
| % alertas CRITICAL atendidas en SLA | > 95% |
| % falsos positivos en CRITICAL | < 10% |
| Tiempo medio de priorización | < 2 segundos |
| Correlación score vs outcome | > 0.7 |

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
