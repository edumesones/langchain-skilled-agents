---
skill_id: "decision_explainer"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Documenta razonamiento de decisión con cadena de evidencia auditable"

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
    - alert_prioritizer
  external_apis: []

capabilities:
  - Documentar decisiones de forma estructurada
  - Crear cadena de evidencia auditable
  - Generar explicaciones para auditoría
  - Soportar diferentes outcomes (SAR, FP, escalado)

limitations:
  - No toma decisiones, solo documenta
  - Requiere input del analista
  - No sustituye juicio humano

references:
  - id: "explainability_standards"
    path: "references/explainability_standards.md"
    description: "Estándares de explicabilidad para auditoría"
  - id: "audit_requirements"
    path: "references/audit_requirements.md"
    description: "Requisitos de auditoría regulatoria"

forms:
  - id: "decision_form"
    path: "forms.md"
    description: "Template de documentación de decisión"
---

# Decision Explainer

## Propósito

Documenta el **razonamiento detrás de cada decisión** de compliance de forma estructurada y auditable. Crea una cadena de evidencia que soporta la decisión tomada, facilitando revisiones internas y auditorías regulatorias.

## Cuándo Usar Este Skill

- Al cerrar una alerta (cualquier outcome)
- Para documentar escalados
- Cuando se requiere justificación detallada
- Para preparar respuestas a auditoría
- Al documentar decisiones de bloqueo

## Cuándo NO Usar Este Skill

- Durante el análisis (usar otros skills)
- Para alertas aún en investigación
- Sin decisión tomada

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| alert_id | string | Sí | ID de la alerta |
| decision | string | Sí | Outcome: SAR_FILED, CLOSED_FP, CLOSED_NO_ACTION, ESCALATED |
| rationale | string | Sí | Razonamiento del analista |
| evidence_ids | array[string] | No | IDs de evidencia consultada |
| regulatory_basis | string | No | Base regulatoria de la decisión |

## Output Esperado

```json
{
  "decision_record": {
    "decision_id": "DEC-2025-00456",
    "alert_id": "ALT-2847",
    "decision": "CLOSED_FP",
    "decision_date": "2025-01-29T14:30:00Z",
    "decided_by": "ANALYST-123",

    "structured_rationale": {
      "summary": "Falso positivo - actividad consistente con perfil",
      "key_factors": [
        "Cliente con 5+ años de antigüedad",
        "Patrón explicado por actividad estacional",
        "Documentación de soporte válida"
      ],
      "evidence_reviewed": [
        {"type": "TRANSACTION_LIST", "count": 15},
        {"type": "CUSTOMER_PROFILE", "version": "2024-12-01"},
        {"type": "CUSTOMER_STATEMENT", "date": "2025-01-28"}
      ],
      "alternatives_considered": [
        {
          "decision": "SAR_FILED",
          "rejected_because": "No hay indicios suficientes de actividad sospechosa"
        }
      ]
    },

    "compliance_checklist": {
      "customer_profile_reviewed": true,
      "transaction_analysis_completed": true,
      "documentation_requested": true,
      "documentation_received": true,
      "supervisor_consulted": false,
      "edd_applied": false
    },

    "audit_trail": [
      {"timestamp": "2025-01-28T10:00:00Z", "action": "Alert assigned", "user": "SYSTEM"},
      {"timestamp": "2025-01-28T10:30:00Z", "action": "Customer profile reviewed", "user": "ANALYST-123"},
      {"timestamp": "2025-01-28T11:00:00Z", "action": "Documentation requested", "user": "ANALYST-123"},
      {"timestamp": "2025-01-29T09:00:00Z", "action": "Documentation received", "user": "SYSTEM"},
      {"timestamp": "2025-01-29T14:30:00Z", "action": "Decision: CLOSED_FP", "user": "ANALYST-123"}
    ]
  }
}
```

## Estructura de la Documentación

### 1. Resumen Ejecutivo
- Decisión tomada en una línea
- Factores clave (3-5 puntos)

### 2. Análisis Realizado
- Qué se revisó
- Qué se encontró
- Qué no se encontró

### 3. Alternativas Consideradas
- Qué otras decisiones se evaluaron
- Por qué se descartaron

### 4. Base Regulatoria
- Artículos aplicables
- Estándares internos cumplidos

### 5. Evidencia de Soporte
- Lista de documentos/datos consultados
- Referencias a sistemas

## Consideraciones de Compliance

### Art. 25 Ley 10/2010
- Conservar documentación 10 años
- Trazabilidad completa de decisiones

### GDPR Art. 22
- Explicar decisiones que afectan al cliente
- Base legal para el procesamiento

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
