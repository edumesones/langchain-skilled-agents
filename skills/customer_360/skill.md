---
skill_id: "customer_360"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Vista consolidada 360 del cliente: KYC, riesgo, transacciones y alertas"

category: "analysis"
domain: "kyc"
agents: ["orchestrator", "risk", "compliance"]

dependencies:
  data_sources:
    - customers
    - transactions
    - alerts
    - relationships
  other_skills: []
  external_apis: []

capabilities:
  - Consolidar toda la información disponible del cliente
  - Calcular métricas comportamentales vs esperadas
  - Identificar anomalías en perfil
  - Generar timeline de eventos relevantes
  - Mostrar red de relaciones de primer grado

limitations:
  - Solo muestra datos existentes, no genera conclusiones
  - No accede a fuentes externas (PEP lists, sanciones)
  - Datos sujetos a GDPR - solo mostrar lo necesario

references:
  - id: "kyc_requirements"
    path: "references/kyc_requirements.md"
    description: "Campos KYC requeridos por Ley 10/2010"
  - id: "risk_scoring_model"
    path: "references/risk_scoring_model.md"
    description: "Modelo de scoring de riesgo del cliente"
  - id: "gdpr_data_access"
    path: "references/gdpr_data_access.md"
    description: "Principio de minimización de datos GDPR"
---

# Customer 360

## Propósito

Proporciona una **visión completa y consolidada** de un cliente para soportar decisiones de riesgo y compliance. Agrega datos de múltiples fuentes en un formato estructurado, calcula desviaciones del comportamiento esperado y presenta una línea temporal de eventos relevantes.

## Cuándo Usar Este Skill

- Al iniciar la revisión de cualquier alerta
- Para entender el contexto de una transacción sospechosa
- Durante procesos de revisión periódica (EDD)
- Para identificar patrones de comportamiento
- Cuando se necesita documentar el conocimiento del cliente
- Para preparar informes regulatorios

## Cuándo NO Usar Este Skill

- Para consultas masivas de múltiples clientes
- Cuando solo se necesita un dato específico (usar query directo)
- Sin justificación de negocio (GDPR requiere propósito)
- Para clientes sin relación activa (datos archivados)

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| customer_id | string | Sí | ID único del cliente |
| sections | array[string] | No | Secciones a incluir (default: todas) |
| time_period_days | integer | No | Período para métricas transaccionales (default: 90) |
| purpose | string | Sí | Justificación de acceso (requerido GDPR) |
| include_relationships | boolean | No | Incluir grafo de relaciones (default: true) |

### Secciones Disponibles

- `identity`: Datos personales y documentos
- `kyc_status`: Estado de verificación KYC
- `risk_profile`: Perfil y score de riesgo
- `behavioral_metrics`: Métricas transaccionales
- `transaction_summary`: Resumen de transacciones
- `alert_history`: Historial de alertas
- `relationships`: Red de relaciones
- `timeline`: Eventos cronológicos

## Output Esperado

```json
{
  "customer_id": "uuid",
  "snapshot_timestamp": "2025-01-29T10:30:00Z",
  "purpose": "Revisión de alerta ALT-2847",

  "identity": {
    "full_name": "Juan García López",
    "age": 45,
    "nationality": "ESP",
    "residence_country": "ESP",
    "customer_since": "2020-03-15",
    "tenure_years": 4.8,
    "document_type": "DNI",
    "document_valid": true
  },

  "kyc_status": {
    "verification_level": "FULL",
    "last_kyc_review": "2024-06-01",
    "next_review_due": "2025-06-01",
    "documents_valid": true,
    "pep_status": "NOT_PEP",
    "sanctions_status": "CLEAR",
    "edd_required": false
  },

  "risk_profile": {
    "current_score": 45,
    "category": "MEDIUM",
    "trend": "STABLE",
    "factors": [
      "Sector de alto riesgo (inmobiliario)",
      "Transacciones internacionales frecuentes"
    ],
    "last_assessment": "2024-12-15"
  },

  "behavioral_metrics": {
    "period_days": 90,
    "comparison": {
      "monthly_income": {
        "expected": 5000,
        "actual": 4800,
        "deviation_pct": -4,
        "status": "NORMAL"
      },
      "monthly_expenses": {
        "expected": 3000,
        "actual": 3200,
        "deviation_pct": 6.7,
        "status": "NORMAL"
      },
      "transaction_count": {
        "expected": 50,
        "actual": 48,
        "deviation_pct": -4,
        "status": "NORMAL"
      }
    },
    "anomalies_detected": [],
    "new_countries": [],
    "new_counterparties": 3
  },

  "transaction_summary": {
    "period_days": 90,
    "total_inbound": 14400,
    "total_outbound": 9600,
    "net_flow": 4800,
    "largest_single_tx": 2500,
    "international_pct": 5,
    "cash_pct": 2,
    "top_categories": [
      {"category": "SALARY", "amount": 14400, "pct": 100}
    ]
  },

  "alert_history": {
    "total_alerts": 2,
    "open_alerts": 0,
    "closed_false_positive": 2,
    "closed_sar": 0,
    "last_alert_date": "2024-09-15",
    "alerts": [
      {
        "alert_id": "ALT-1234",
        "type": "VELOCITY",
        "date": "2024-09-15",
        "outcome": "CLOSED_FP"
      }
    ]
  },

  "relationships": {
    "first_degree_count": 5,
    "suspicious_connections": 0,
    "connections": [
      {
        "entity_name": "María García López",
        "relationship_type": "FAMILY",
        "strength": 0.8,
        "is_suspicious": false
      }
    ]
  },

  "timeline": [
    {
      "date": "2024-12-15",
      "event": "Revisión de riesgo completada",
      "type": "RISK_REVIEW"
    },
    {
      "date": "2024-09-15",
      "event": "Alerta cerrada como FP",
      "type": "ALERT"
    },
    {
      "date": "2024-06-01",
      "event": "Revisión KYC completada",
      "type": "KYC"
    }
  ]
}
```

## Flujo de Trabajo

1. **Validar acceso**: Verificar que el propósito es legítimo (GDPR)
2. **Recuperar datos base**: Obtener registro del cliente
3. **Calcular métricas**: Agregar transacciones del período
4. **Comparar comportamiento**: Calcular desviaciones vs esperado
5. **Obtener historial**: Recuperar alertas y decisiones previas
6. **Mapear relaciones**: Identificar conexiones de primer grado
7. **Generar timeline**: Ordenar eventos cronológicamente
8. **Aplicar minimización**: Filtrar campos según propósito

## Interpretación de Desviaciones

### Umbrales de Normalidad

| Métrica | Normal | Atención | Alerta |
|---------|--------|----------|--------|
| Ingresos mensuales | ±15% | 15-30% | >30% |
| Gastos mensuales | ±20% | 20-40% | >40% |
| Número de transacciones | ±25% | 25-50% | >50% |
| Monto máximo individual | ±30% | 30-100% | >100% |

### Códigos de Estado

- `NORMAL`: Dentro de comportamiento esperado
- `ATTENTION`: Desviación moderada, monitorear
- `ANOMALY`: Desviación significativa, investigar
- `CRITICAL`: Desviación extrema, acción inmediata

## Consideraciones de Compliance

### GDPR

**Art. 5.1(c) - Minimización de datos**
- Solo recuperar campos necesarios para el propósito declarado
- El parámetro `purpose` es obligatorio
- Registrar cada acceso en log de auditoría

**Art. 5.1(e) - Limitación de conservación**
- Datos de clientes inactivos >10 años requieren justificación especial
- Marcar datos archivados claramente

**Art. 15 - Derecho de acceso**
- Este skill puede usarse para generar informe de datos del titular

### Ley 10/2010

**Art. 25 - Conservación**
- Mantener datos 10 años desde fin de relación
- El campo `data_retention_until` indica fecha límite

**Art. 6 - Deber de diligencia debida**
- La información del customer_360 soporta el cumplimiento de diligencia

## Ejemplos de Uso

### Ejemplo 1: Contexto para Alerta

**Input:**
```json
{
  "customer_id": "C-4821",
  "purpose": "Revisión de alerta ALT-2847 - SANCTIONS",
  "time_period_days": 90
}
```

**Uso:** El analista carga el perfil completo antes de revisar una alerta de sanciones para entender el contexto del cliente.

### Ejemplo 2: Revisión EDD

**Input:**
```json
{
  "customer_id": "C-0099",
  "purpose": "Enhanced Due Diligence - PEP trimestral",
  "sections": ["identity", "kyc_status", "risk_profile", "behavioral_metrics"],
  "time_period_days": 180
}
```

**Uso:** Durante la revisión periódica de un PEP, se solicitan solo las secciones relevantes con un período más amplio.

## Troubleshooting

### Datos Incompletos
**Síntoma:** Campos vacíos o null
**Acción:** Verificar si requiere actualización KYC. Marcar para revisión.

### Cliente No Encontrado
**Síntoma:** Error "customer not found"
**Acción:** Verificar ID. Puede ser cliente archivado o ID incorrecto.

### Desviación Extrema
**Síntoma:** Métricas >100% de desviación
**Acción:** Verificar si hubo evento vital (herencia, venta inmueble, etc).

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
