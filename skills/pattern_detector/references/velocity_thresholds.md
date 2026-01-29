# Umbrales de Velocity por Perfil

## Concepto

Velocity = Tasa de cambio en métricas transaccionales respecto a baseline histórico.

## Baselines por Segmento

### Particulares - Asalariados
| Métrica | Baseline Mensual | Desviación Normal |
|---------|------------------|-------------------|
| Ingresos | 1x salario declarado | ±20% |
| Gastos | 0.7x ingresos | ±25% |
| Transacciones | 30-50 | ±30% |
| Max individual | 0.3x ingresos | ±50% |

### Particulares - Autónomos
| Métrica | Baseline Mensual | Desviación Normal |
|---------|------------------|-------------------|
| Ingresos | Variable según sector | ±40% |
| Gastos | 0.6x ingresos | ±35% |
| Transacciones | 50-100 | ±40% |

### Empresas - PYME
| Métrica | Baseline Mensual | Desviación Normal |
|---------|------------------|-------------------|
| Ingresos | Según facturación | ±30% |
| Transacciones | 100-500 | ±35% |

## Alertas de Velocity

### Nivel 1: Atención
- Desviación 50-100% del baseline
- Acción: Monitorización reforzada

### Nivel 2: Investigación
- Desviación 100-200% del baseline
- Acción: Revisión L1

### Nivel 3: Urgente
- Desviación >200% del baseline
- Acción: Revisión L2 inmediata

## Casos Especiales

### Reactivación de Cuenta Dormant
```
SI (días_sin_actividad > 180)
Y (nueva_actividad > 1000 EUR)
ENTONCES alerta VELOCITY_DORMANT
```

### Burst Activity
```
SI (transacciones_24h > 10)
Y (transacciones_24h > 5x promedio_diario)
ENTONCES alerta VELOCITY_BURST
```

## Ajustes Estacionales

| Período | Factor |
|---------|--------|
| Navidad (Dic) | 1.5x |
| Rebajas (Ene, Jul) | 1.3x |
| Vacaciones (Ago) | 0.7x |
| Black Friday | 2.0x (solo ese día) |
