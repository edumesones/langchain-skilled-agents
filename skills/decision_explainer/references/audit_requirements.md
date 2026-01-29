# Requisitos de Auditoría Regulatoria

## Marco de Auditoría

### Auditoría Interna
- Frecuencia: Trimestral
- Muestra: 10% de decisiones
- Foco: Consistencia y completitud

### Auditoría Externa
- Frecuencia: Anual
- Alcance: Proceso completo
- Incluye: Revisión de casos

### Inspección SEPBLAC
- Sin aviso previo
- Acceso completo a expedientes
- Puede solicitar cualquier caso

## Documentación Requerida

### Por Cada Decisión

| Elemento | Obligatorio | Formato |
|----------|-------------|---------|
| ID único | Sí | Alfanumérico |
| Fecha/hora | Sí | ISO 8601 |
| Usuario decisor | Sí | ID + nombre |
| Alerta origen | Sí | ID |
| Outcome | Sí | Código estandarizado |
| Rationale | Sí | Texto estructurado |
| Evidencia | Sí | Referencias |
| Aprobaciones | Si aplica | Firmas/IDs |

### Conservación

| Tipo | Plazo | Base Legal |
|------|-------|------------|
| Decisiones AML | 10 años | Ley 10/2010 Art. 25 |
| Logs de acceso | 5 años | GDPR |
| Comunicaciones SEPBLAC | 10 años | Ley 10/2010 |

## Métricas de Auditoría

### KPIs Monitorizados

| Métrica | Umbral Aceptable |
|---------|------------------|
| % decisiones documentadas | 100% |
| % con rationale completo | > 95% |
| Tiempo medio de decisión | Según SLA |
| % revisadas por supervisor (HIGH) | 100% |
| Consistencia inter-analista | > 85% |

### Red Flags para Auditores

- Decisiones sin justificación
- Patrones de cierre rápido
- Desviaciones de procedimiento
- Falta de escalado cuando correspondía
- Documentación retroactiva
