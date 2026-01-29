# Reglas Aprendidas de Histórico

## Metodología

Las reglas se derivan del análisis de decisiones históricas:
- Mínimo 100 casos por regla
- Confianza >80% de clasificación correcta
- Revisión trimestral de vigencia

## Reglas Activas

### FP-RULE-001: Hostelería + Efectivo
```
SI cliente.cnae IN [5610, 5630, 5621]  # Restaurantes, bares
Y alerta.tipo = "STRUCTURING"
Y alerta.subtipo = "CASH"
Y cliente.tenure > 2 años
Y cliente.alertas_previas_sar = 0
ENTONCES fp_probability += 0.3
```
**Base:** 847 casos, 78% cerrados FP

### FP-RULE-002: Evento Vital Documentado
```
SI cliente.evento_vital_reciente = TRUE  # <90 días
Y alerta.tipo IN ["VELOCITY", "UNUSUAL_ACTIVITY"]
Y evento.documentado = TRUE
ENTONCES fp_probability += 0.4
```
**Base:** 234 casos, 89% cerrados FP

### FP-RULE-003: Viaje Documentado
```
SI alerta.tipo = "GEOGRAPHIC"
Y cliente.uso_tarjeta_destino = TRUE
Y cliente.viajes_previos_destino > 0
ENTONCES fp_probability += 0.35
```
**Base:** 412 casos, 82% cerrados FP

### FP-RULE-004: Cliente Veterano Sin Historial
```
SI cliente.tenure > 5 años
Y cliente.alertas_historicas = 0
Y alerta.severity < "HIGH"
ENTONCES fp_probability += 0.25
```
**Base:** 1,203 casos, 71% cerrados FP

### FP-RULE-005: Patrón Regular Establecido
```
SI transaccion.similar_a_patron_6m = TRUE
Y patron.monto_desviacion < 10%
Y patron.frecuencia_desviacion < 20%
ENTONCES fp_probability += 0.2
```
**Base:** 567 casos, 75% cerrados FP

## Reglas de Exclusión (No aplicar FP rules)

### EXCL-001: SAR Previo
```
SI cliente.sar_previo = TRUE
ENTONCES NO aplicar reglas FP
SIEMPRE investigación completa
```

### EXCL-002: PEP
```
SI cliente.pep_status != "NOT_PEP"
ENTONCES NO aplicar reglas FP
SIEMPRE revisión L2
```

### EXCL-003: Alertas CRITICAL/SANCTIONS
```
SI alerta.tipo = "SANCTIONS"
O alerta.priority = "CRITICAL"
ENTONCES NO aplicar reglas FP
```

## Actualización de Reglas

### Proceso Trimestral
1. Extraer decisiones de últimos 90 días
2. Recalcular precisión de cada regla
3. Ajustar umbrales si precisión <70%
4. Proponer nuevas reglas si patrón >100 casos

### Gobernanza
- Aprobación: Risk Analytics Manager
- Revisión: Comité de Modelos
- Documentación: Registro de cambios
