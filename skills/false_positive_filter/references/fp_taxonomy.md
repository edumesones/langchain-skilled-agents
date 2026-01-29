# Taxonomía de Falsos Positivos

## Por Tipo de Alerta

### STRUCTURING FP

| Causa de FP | Frecuencia | Identificación |
|-------------|------------|----------------|
| Negocio cash-intensive | 35% | Verificar CNAE hostelería/retail |
| Hábito de retiro fijo | 20% | Patrón regular mensual |
| Límite de cajero | 15% | Coincide con máximo ATM |
| Pago alquiler efectivo | 10% | Mismo monto mensual |

**Indicadores de FP legítimo:**
- CNAE en sectores de efectivo
- Patrón regular >6 meses
- Documentación de actividad

### VELOCITY FP

| Causa de FP | Frecuencia | Identificación |
|-------------|------------|----------------|
| Cambio de empleo | 25% | Verificar fecha inicio nuevo trabajo |
| Evento vital | 20% | Herencia, venta inmueble |
| Estacionalidad | 15% | Diciembre, vacaciones |
| Nueva actividad declarada | 10% | Actualización KYC reciente |

**Indicadores de FP legítimo:**
- Evento vital documentado
- Actualización de perfil KYC
- Justificación económica clara

### GEOGRAPHIC FP

| Causa de FP | Frecuencia | Identificación |
|-------------|------------|----------------|
| Viaje turístico | 40% | Uso de tarjeta en destino |
| Familia en país | 20% | Remesas regulares |
| E-commerce internacional | 15% | Compras online |
| Trabajo remoto | 10% | IP de otro país |

**Indicadores de FP legítimo:**
- Historial de viajes previos
- Remesas de monto consistente
- Coincide con patrones de ocio

### UNUSUAL_ACTIVITY FP

| Causa de FP | Frecuencia | Identificación |
|-------------|------------|----------------|
| Regla muy sensible | 30% | Muchos FP del mismo tipo |
| Perfil desactualizado | 25% | KYC no actualizado |
| Evento aislado | 20% | Sin repetición |
| Error de datos | 5% | Inconsistencia en sistemas |

## Por Perfil de Cliente

### Baja propensión FP
- Clientes con SAR previo
- PEPs
- Clientes HIGH risk
- Nuevos clientes (<1 año)

### Alta propensión FP
- Clientes >5 años sin alertas
- Perfiles completos y actualizados
- Sectores conocidos (nómina estable)
- Bajo volumen transaccional

## Métricas de Calibración

### Por Regla de Detección
```
tasa_fp_regla = count(FP) / count(alertas_regla)

SI tasa_fp_regla > 0.7 ENTONCES revisar umbral
```

### Por Segmento
```
tasa_fp_segmento = count(FP_segmento) / count(alertas_segmento)
```

## Uso para Mejora Continua

1. Registrar causa raíz de cada FP
2. Agrupar por taxonomía
3. Identificar reglas con alta tasa FP
4. Proponer ajustes a Risk Analytics
