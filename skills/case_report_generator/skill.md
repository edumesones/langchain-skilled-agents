---
skill_id: "case_report_generator"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Genera informes SAR/STR estructurados en formato SEPBLAC"

category: "reporting"
domain: "aml"
agents: ["orchestrator", "compliance"]

dependencies:
  data_sources:
    - alerts
    - customers
    - transactions
  other_skills:
    - customer_360
    - decision_explainer
  external_apis: []

capabilities:
  - Generar informes SAR en formato SEPBLAC
  - Estructurar evidencia de forma auditable
  - Incluir cronología de eventos
  - Exportar en formato descargable

limitations:
  - No envía comunicaciones automáticamente
  - Requiere revisión humana antes de envío
  - No accede al portal SEPBLAC

references:
  - id: "sar_template"
    path: "references/sar_template.md"
    description: "Estructura del informe SAR"
  - id: "sepblac_format"
    path: "references/sepblac_format.md"
    description: "Requisitos de formato SEPBLAC"
  - id: "evidence_requirements"
    path: "references/evidence_requirements.md"
    description: "Requisitos de evidencia por tipología"

forms:
  - id: "sar_report"
    path: "forms.md"
    description: "Template de informe SAR descargable"
---

# Case Report Generator

## Propósito

Genera informes estructurados para **Comunicación por Indicio (SAR/STR)** al SEPBLAC, compilando toda la evidencia relevante en el formato requerido por el regulador.

## Cuándo Usar Este Skill

- Cuando se decide comunicar una operación sospechosa
- Para documentar investigaciones complejas
- Al preparar respuestas a requerimientos regulatorios
- Para generar informes internos de casos cerrados

## Cuándo NO Usar Este Skill

- Para análisis preliminar de alertas (usar otros skills)
- Si no hay decisión de comunicar
- Para comunicaciones sistemáticas (proceso diferente)

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| case_id | string | Sí | ID del caso a reportar |
| alert_ids | array[string] | Sí | Alertas incluidas en el caso |
| report_type | string | No | INITIAL, CONTINUING, JOINT (default: INITIAL) |
| include_evidence | boolean | No | Incluir detalle de evidencia (default: true) |
| format | string | No | SEPBLAC, INTERNAL (default: SEPBLAC) |

## Output Esperado

```json
{
  "report": {
    "header": {
      "report_id": "SAR-2025-00123",
      "report_type": "INITIAL",
      "generation_date": "2025-01-29T10:30:00Z",
      "prepared_by": "ANALYST-123",
      "reviewed_by": null,
      "status": "DRAFT"
    },
    "subject": {
      "customer_id": "C-4821",
      "name": "Juan García López",
      "document": "12345678A",
      "risk_category": "HIGH",
      "pep_status": "NOT_PEP"
    },
    "summary": {
      "typology": "STRUCTURING",
      "period": "2024-10-01 a 2025-01-15",
      "total_amount": 145000,
      "transaction_count": 52,
      "brief_description": "Patrón de depósitos en efectivo fragmentados..."
    },
    "narrative": "...",
    "evidence": [...],
    "timeline": [...],
    "recommendation": "Comunicar al SEPBLAC"
  }
}
```

## Secciones del Informe

1. **Cabecera:** Metadatos del informe
2. **Sujeto:** Datos del cliente investigado
3. **Resumen Ejecutivo:** Tipología, período, montos
4. **Narrativa:** Descripción detallada del caso
5. **Evidencia:** Transacciones, documentos, capturas
6. **Cronología:** Timeline de eventos
7. **Análisis:** Patrones detectados
8. **Conclusión:** Recomendación fundamentada

## Consideraciones de Compliance

### Ley 10/2010 Art. 18
- Comunicación "sin dilación" de operaciones sospechosas
- No informar al cliente (deber de confidencialidad)
- Conservar durante 10 años

### SEPBLAC
- Formato estructurado requerido
- Incluir toda la información relevante
- No omitir datos aunque parezcan menores

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
