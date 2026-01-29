---
skill_id: "relationship_mapper"
version: "1.0.0"
last_updated: "2025-01-29"
author: "fintech-team"

brief: "Visualiza y analiza grafo de relaciones sospechosas entre entidades"

category: "analysis"
domain: "aml"
agents: ["orchestrator", "risk"]

dependencies:
  data_sources:
    - customers
    - transactions
    - relationships
  other_skills:
    - customer_360
  external_apis: []

capabilities:
  - Mapear relaciones entre clientes, cuentas y entidades
  - Identificar clusters sospechosos
  - Detectar patrones de red (circular, hub-spoke)
  - Calcular scores de sospecha por conexión
  - Visualizar grafo de relaciones

limitations:
  - Máximo 100 nodos por consulta
  - Solo relaciones de primer y segundo grado
  - No accede a datos externos de empresas

references:
  - id: "graph_algorithms"
    path: "references/graph_algorithms.md"
    description: "Algoritmos de detección de patrones en grafos"
  - id: "suspicious_patterns"
    path: "references/suspicious_patterns.md"
    description: "Patrones de red sospechosos conocidos"
---

# Relationship Mapper

## Propósito

Analiza y visualiza la **red de relaciones** de un cliente o grupo de clientes para identificar conexiones sospechosas, patrones de red anómalos y clusters de actividad potencialmente coordinada.

## Cuándo Usar Este Skill

- Al investigar alertas de structuring/smurfing
- Para detectar redes de blanqueo organizadas
- Cuando se identifican múltiples alertas relacionadas
- Para análisis de titularidad real compleja
- En investigaciones de fraude organizado

## Cuándo NO Usar Este Skill

- Para análisis de cliente individual sin conexiones
- Cuando solo se necesita información básica (usar `customer_360`)
- Para visualizaciones con >100 entidades (usar herramienta especializada)

## Inputs Requeridos

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| entity_id | string | Sí | ID de la entidad central |
| entity_type | string | No | Tipo: CUSTOMER, ACCOUNT, COMPANY (default: CUSTOMER) |
| depth | integer | No | Niveles de profundidad (1 o 2, default: 1) |
| include_transactions | boolean | No | Incluir aristas de transacciones (default: true) |
| min_strength | float | No | Fuerza mínima de relación (0-1, default: 0.1) |
| time_period_days | integer | No | Período para calcular relaciones (default: 365) |

## Output Esperado

```json
{
  "graph": {
    "center_entity": {
      "id": "C-4821",
      "type": "CUSTOMER",
      "name": "Juan García López",
      "risk_category": "MEDIUM"
    },
    "nodes": [
      {
        "id": "C-1234",
        "type": "CUSTOMER",
        "name": "María García López",
        "risk_category": "LOW",
        "is_suspicious": false,
        "alerts_count": 0
      },
      {
        "id": "C-5678",
        "type": "CUSTOMER",
        "name": "Pedro Martínez",
        "risk_category": "HIGH",
        "is_suspicious": true,
        "alerts_count": 3
      }
    ],
    "edges": [
      {
        "source": "C-4821",
        "target": "C-1234",
        "relationship_type": "FAMILY",
        "strength": 0.85,
        "is_suspicious": false,
        "transaction_count": 12,
        "total_amount": 3500
      },
      {
        "source": "C-4821",
        "target": "C-5678",
        "relationship_type": "TRANSFER",
        "strength": 0.65,
        "is_suspicious": true,
        "suspicion_reason": "Transferencias frecuentes a cliente HIGH risk",
        "transaction_count": 45,
        "total_amount": 125000
      }
    ]
  },
  "analysis": {
    "total_nodes": 8,
    "total_edges": 12,
    "suspicious_nodes": 2,
    "suspicious_edges": 3,
    "clusters_detected": 1,
    "patterns_detected": ["HUB_SPOKE"]
  },
  "clusters": [
    {
      "cluster_id": "CLUSTER-001",
      "node_ids": ["C-4821", "C-5678", "C-9999"],
      "pattern": "HUB_SPOKE",
      "hub_entity": "C-4821",
      "total_flow": 250000,
      "suspicion_score": 72,
      "description": "Cliente central recibe de múltiples fuentes y distribuye"
    }
  ],
  "recommendations": [
    "Investigar relación C-4821 ↔ C-5678: alto volumen con cliente HIGH risk",
    "Cluster detectado sugiere posible coordinación",
    "Considerar revisión EDD del grupo completo"
  ]
}
```

## Patrones de Red Sospechosos

### 1. Hub-Spoke (Estrella)
Un nodo central recibe/envía a múltiples nodos periféricos.
- **Indicador de:** Smurfing, cuenta de recogida
- **Score de sospecha:** +30 si >5 conexiones activas

### 2. Circular (Round-Trip)
Fondos que regresan al origen pasando por intermediarios.
- **Indicador de:** Layering, auto-préstamos ficticios
- **Score de sospecha:** +40

### 3. Cadena (Chain)
Fondos que fluyen en una dirección a través de múltiples nodos.
- **Indicador de:** Layering tradicional
- **Score de sospecha:** +25

### 4. Clique (Grupo Cerrado)
Múltiples nodos con conexiones bidireccionales entre todos.
- **Indicador de:** Red organizada
- **Score de sospecha:** +35

## Flujo de Trabajo

1. **Identificar entidad central** del análisis
2. **Recuperar relaciones** de primer grado
3. **Expandir a segundo grado** si depth=2
4. **Calcular métricas** de cada arista (fuerza, volumen)
5. **Detectar patrones** de red conocidos
6. **Identificar clusters** sospechosos
7. **Generar visualización** y recomendaciones

## Consideraciones de Compliance

### GDPR
- Solo incluir datos necesarios para la investigación
- Justificar acceso a datos de terceros relacionados
- Registrar propósito del análisis de red

### Ley 10/2010
- El análisis de redes soporta la detección de organizaciones criminales
- Documentar hallazgos para posible comunicación

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-01-29 | Versión inicial |
