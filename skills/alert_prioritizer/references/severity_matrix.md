# Matriz de Severidad de Alertas

## Scores Base por Tipo y Monto

Esta matriz define el score base de severidad para cada combinación de tipo de alerta y rango de monto. Los valores están calibrados según el riesgo inherente de cada tipología y los umbrales regulatorios aplicables en España.

### Tabla Principal

| Tipo de Alerta | < 3,000 EUR | 3,000 - 10,000 | 10,000 - 50,000 | 50,000 - 150,000 | > 150,000 |
|----------------|-------------|----------------|-----------------|------------------|-----------|
| SANCTIONS | 75 | 80 | 90 | 95 | 100 |
| PEP | 45 | 50 | 65 | 80 | 90 |
| STRUCTURING | 35 | 40 | 55 | 70 | 85 |
| GEOGRAPHIC | 40 | 45 | 60 | 75 | 85 |
| VELOCITY | 30 | 35 | 50 | 65 | 80 |
| UNUSUAL_ACTIVITY | 25 | 30 | 45 | 60 | 75 |

### Justificación de Scores

#### SANCTIONS (Máxima Severidad)
- Obligación legal de bloqueo inmediato
- Posibles sanciones regulatorias severas
- Riesgo reputacional extremo
- Comunicación SEPBLAC obligatoria en 24h

#### PEP (Alta Severidad)
- Requisito de Enhanced Due Diligence (EDD)
- Mayor escrutinio regulatorio
- Riesgo de corrupción/soborno
- Art. 14 Ley 10/2010

#### STRUCTURING (Severidad Media-Alta)
- Indicio clásico de blanqueo
- Patrón deliberado de evasión de umbrales
- Requiere análisis de intencionalidad
- Posible comunicación sistemática

#### GEOGRAPHIC (Severidad Media-Alta)
- Países en listas GAFI/UE
- Jurisdicciones opacas
- Riesgo de financiación del terrorismo
- Verificar legitimidad de operación

#### VELOCITY (Severidad Media)
- Cambio de comportamiento
- Posible cuenta comprometida
- Requiere contexto adicional
- Puede ser legítimo (eventos vitales)

#### UNUSUAL_ACTIVITY (Severidad Media-Baja)
- Desviación de perfil esperado
- Alta tasa de falsos positivos
- Requiere investigación detallada
- Contexto es clave

## Umbrales Monetarios

### Justificación de Rangos

| Rango | Justificación Regulatoria |
|-------|---------------------------|
| < 3,000 EUR | Por debajo de umbral de identificación Art. 4 |
| 3,000 - 10,000 EUR | Rango de structuring típico |
| 10,000 - 50,000 EUR | Umbral de comunicación sistemática |
| 50,000 - 150,000 EUR | Operaciones significativas |
| > 150,000 EUR | Operaciones de alto valor - EDD obligatorio |

### Umbrales Específicos

- **3,000 EUR**: Umbral de identificación para operaciones ocasionales
- **10,000 EUR**: Umbral de examen especial (Art. 17)
- **30,000 EUR**: Umbral para comunicación sistemática de ciertas operaciones
- **100,000 EUR**: Umbral para EDD reforzada
- **150,000 EUR**: Umbral de alto valor

## Combinaciones de Alto Riesgo

Cuando se detectan múltiples indicadores, aplicar el mayor score base más un bonus:

| Combinación | Bonus Adicional |
|-------------|-----------------|
| SANCTIONS + cualquier otro | +10 |
| PEP + GEOGRAPHIC | +15 |
| STRUCTURING + VELOCITY | +10 |
| GEOGRAPHIC + alto monto (>50K) | +10 |
| Cualquier tipo + cliente HIGH risk | +15 |

## Ajustes por Subtipo

### STRUCTURING Subtipos
| Subtipo | Ajuste |
|---------|--------|
| CASH_STRUCTURING | +10 |
| TRANSFER_STRUCTURING | +5 |
| DEPOSIT_STRUCTURING | +5 |

### VELOCITY Subtipos
| Subtipo | Ajuste |
|---------|--------|
| DORMANT_REACTIVATION | +15 |
| BURST_ACTIVITY | +10 |
| HIGH_FREQUENCY | +5 |

### GEOGRAPHIC Subtipos
| Subtipo | Ajuste |
|---------|--------|
| SANCTIONED_COUNTRY | +20 |
| FATF_GREY_LIST | +10 |
| TAX_HAVEN | +5 |

## Notas de Implementación

1. **Score mínimo**: 10 (ninguna alerta debe tener score 0)
2. **Score máximo**: 100 (cap absoluto)
3. **Redondeo**: Siempre hacia arriba para severidad
4. **Desempate**: Usar timestamp de creación (FIFO)
5. **Caché**: Scores base pueden cachearse, modificadores son dinámicos
