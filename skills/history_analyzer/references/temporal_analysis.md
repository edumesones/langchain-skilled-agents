# Análisis de Patrones Temporales

## Métricas Temporales

### Frecuencia de Alertas
```
frecuencia = count(alertas) / período_meses
```

| Frecuencia | Clasificación |
|------------|---------------|
| < 0.1 alertas/mes | Normal |
| 0.1-0.3 alertas/mes | Elevada |
| > 0.3 alertas/mes | Alta (atención) |

### Tiempo Entre Alertas

```
mean_time_between = promedio(diferencia_fechas_consecutivas)
```

| MTBA | Interpretación |
|------|----------------|
| > 365 días | Alertas aisladas |
| 90-365 días | Patrón periódico |
| < 90 días | Comportamiento activo |

### Tendencia Temporal

```python
def calculate_trend(alerts):
    """
    Analiza si las alertas son cada vez más frecuentes/graves.
    """
    if len(alerts) < 3:
        return "INSUFFICIENT_DATA"

    # Frecuencia
    recent_freq = count_last_year / 1
    historical_freq = count_previous_years / years

    if recent_freq > historical_freq * 1.5:
        return "DETERIORATING"
    elif recent_freq < historical_freq * 0.5:
        return "IMPROVING"
    else:
        return "STABLE"
```

## Patrones Estacionales

### Meses de Mayor Actividad (general)
- Diciembre: +40% (Navidad, bonificaciones)
- Enero: +20% (Rebajas)
- Julio-Agosto: -30% (Vacaciones)

### Ajuste por Estacionalidad
```
alertas_ajustadas = alertas_brutas / factor_estacional
```

## Análisis de Clusters Temporales

### Burst Detection
```
SI count(alertas en 7 días) >= 3
ENTONCES flag TEMPORAL_BURST
```

### Periodicidad
Detectar si las alertas siguen un patrón regular:
- Mensual (nóminas, alquileres)
- Trimestral (impuestos)
- Anual (eventos recurrentes)

## Visualización Recomendada

### Timeline Plot
- Eje X: Tiempo
- Eje Y: Severidad de alerta
- Color: Tipo de alerta
- Tamaño: Monto involucrado

### Heatmap Semanal
- Filas: Semanas
- Columnas: Días
- Intensidad: Número de alertas
