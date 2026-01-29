# Reglas de Detección de Structuring

## Umbrales Regulatorios España

| Umbral | Contexto | Acción Requerida |
|--------|----------|------------------|
| 1,000 EUR | Operaciones de cambio | Identificación |
| 3,000 EUR | Efectivo sin relación de negocio | Identificación reforzada |
| 10,000 EUR | Cualquier operación | Comunicación sistemática |
| 30,000 EUR | Medios de pago | Comunicación sistemática |

## Patrones de Structuring

### 1. Cash Structuring
**Regla:** Múltiples depósitos en efectivo < umbral en período corto

```
SI (suma(depositos_efectivo) en N días) > umbral
Y (max(deposito_individual) < umbral * 0.95)
Y (count(depositos) >= 3)
ENTONCES alerta STRUCTURING
```

**Parámetros:**
- N = 7 días (configurable)
- umbral = 3,000 EUR (efectivo) o 10,000 EUR (general)
- Tolerancia = 5% bajo umbral

### 2. Transfer Structuring
**Regla:** Transferencias fragmentadas a mismo destino

```
SI (suma(transferencias_mismo_beneficiario) en N días) > umbral
Y (count(transferencias) >= 2)
Y (max(transferencia) < umbral * 0.90)
ENTONCES alerta STRUCTURING
```

### 3. Temporal Clustering
**Regla:** Operaciones concentradas en ventana temporal corta

```
SI (count(operaciones) en 24h) > umbral_diario
O (count(operaciones) en 7d) > umbral_semanal * 2)
ENTONCES flag TEMPORAL_CLUSTERING
```

## Cálculo de Confianza

| Factor | Peso |
|--------|------|
| Proximidad al umbral (>90%) | +0.20 |
| Número de operaciones (>5) | +0.15 |
| Ventana temporal (<7 días) | +0.15 |
| Mismo canal/sucursal | +0.10 |
| Historial limpio previo | -0.10 |
| Cliente cash-intensive declarado | -0.15 |

**Confianza = base(0.5) + suma(factores)**

## Falsos Positivos Conocidos

- Negocios de hostelería (alta facturación efectivo)
- Mercados/mercadillos
- Pequeño comercio
- Pagos de alquiler recurrentes
- Trabajadores con propinas
