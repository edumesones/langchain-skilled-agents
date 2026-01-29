# Baselines para Detección de Anomalías

## Metodología

### Cálculo de Baseline Individual
```
baseline_cliente = promedio(últimos_12_meses)
                   excluyendo(outliers > 3σ)
```

### Cálculo de Baseline de Peer Group
```
baseline_peer = promedio(clientes_mismo_segmento)
                filtrado_por(edad, ingresos, productos)
```

### Detección de Anomalía
```
anomaly_score = |valor_actual - baseline| / std_dev
SI anomaly_score > umbral ENTONCES anomalía
```

## Umbrales por Tipo de Anomalía

| Tipo | Z-Score Umbral | Sensibilidad |
|------|----------------|--------------|
| Monto total mensual | 2.5 | Media |
| Transacción individual | 3.0 | Baja |
| Frecuencia diaria | 2.0 | Alta |
| Nuevo país | 1.0 (binario) | Alta |
| Nuevo beneficiario | 2.0 | Media |

## Factores Contextuales

### Aumentan sensibilidad
- Cliente nuevo (<6 meses): +0.5 al z-score
- Historial de alertas: +0.3 por alerta previa
- Cliente HIGH risk: +0.5

### Reducen sensibilidad
- Cliente >5 años: -0.3
- Sin alertas previas: -0.2
- Evento vital documentado: -1.0

## Eventos Vitales Conocidos

| Evento | Impacto Esperado | Duración |
|--------|------------------|----------|
| Herencia | +200-500% ingresos | 1-3 meses |
| Venta inmueble | +300-1000% | 1 mes |
| Jubilación | Cambio de patrón | Permanente |
| Matrimonio | +50-100% gastos | 2-3 meses |
| Nuevo empleo | Cambio de ingresos | Permanente |

## Actualización de Baselines

- **Frecuencia:** Mensual automático
- **Ventana:** 12 meses rolling
- **Exclusiones:** Meses con alertas en investigación
