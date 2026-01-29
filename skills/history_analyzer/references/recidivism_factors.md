# Factores de Reincidencia

## Definición

Un cliente es considerado "reincidente" si tiene:
- 2+ alertas en 12 meses
- O 1 SAR previo + nueva alerta
- O 3+ alertas en toda la relación

## Factores de Peso

### Aumentan riesgo de reincidencia

| Factor | Peso | Justificación |
|--------|------|---------------|
| SAR previo | +3.0 | Indicador más fuerte |
| Alertas CRITICAL previas | +2.0 | Severidad alta |
| Tiempo corto entre alertas (<90d) | +1.5 | Patrón activo |
| Mismo tipo de alerta recurrente | +1.0 | Comportamiento sistemático |
| Alertas en escalada (cada vez más graves) | +1.5 | Tendencia negativa |
| Múltiples cuentas alertadas | +1.0 | Posible evasión |

### Mitigan riesgo

| Factor | Peso | Justificación |
|--------|------|---------------|
| Todas alertas cerradas FP | -1.5 | Reglas sensibles |
| Tiempo largo sin alertas (>2 años) | -1.0 | Comportamiento estabilizado |
| Cambio de perfil documentado | -0.5 | Contexto válido |
| EDD completada satisfactoriamente | -0.5 | Verificación reciente |

## Cálculo de Score de Reincidencia

```
score = suma(factores_riesgo) - suma(factores_mitigantes)

SI score > 3.0 ENTONCES "ALTO RIESGO REINCIDENCIA"
SI score 1.5-3.0 ENTONCES "RIESGO MODERADO"
SI score < 1.5 ENTONCES "RIESGO BAJO"
```

## Acciones por Nivel

### Alto Riesgo
- Monitorización mensual
- EDD obligatoria
- Aprobación de compliance para productos nuevos

### Riesgo Moderado
- Monitorización trimestral
- Revisión de umbrales de alerta

### Riesgo Bajo
- Monitorización estándar
