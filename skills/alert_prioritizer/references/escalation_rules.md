# Reglas de Escalado y SLAs

## Niveles de Escalado

### Nivel 1 (L1) - Revisión Inicial
- **Responsable**: Analista Junior
- **Capacidad**: 15-20 alertas/día
- **Acciones permitidas**:
  - Cerrar como falso positivo (con justificación)
  - Cerrar como actividad legítima (con documentación)
  - Escalar a L2
  - Solicitar información adicional

### Nivel 2 (L2) - Investigación
- **Responsable**: Analista Senior
- **Capacidad**: 8-12 casos/día
- **Acciones permitidas**:
  - Todas las de L1
  - Consolidar múltiples alertas en caso
  - Recomendar SAR
  - Escalar a Compliance Officer

### Nivel 3 (L3) - Compliance Officer
- **Responsable**: MLRO / Compliance Officer
- **Capacidad**: 3-5 casos/día
- **Acciones permitidas**:
  - Todas las anteriores
  - Aprobar comunicación SEPBLAC
  - Ordenar bloqueo de cuenta
  - Reportar a Comité

## SLAs por Prioridad

| Prioridad | Tiempo Máximo | Escalado Automático |
|-----------|---------------|---------------------|
| CRITICAL | 4 horas | A las 2 horas sin asignar |
| HIGH | 24 horas | A las 12 horas sin progreso |
| MEDIUM | 72 horas | A las 48 horas sin progreso |
| LOW | 168 horas (7 días) | A los 5 días sin progreso |

### SLAs Especiales

| Tipo de Alerta | SLA Específico | Justificación |
|----------------|----------------|---------------|
| SANCTIONS match confirmado | 2 horas | Bloqueo inmediato requerido |
| PEP nuevo > 50K EUR | 8 horas | EDD urgente |
| Comunicación SEPBLAC pendiente | 24 horas | Requisito legal |

## Criterios de Escalado Automático

### De L1 a L2

Escalar automáticamente cuando:

1. **Por Score**: Score >= 70
2. **Por Monto**: Monto total > 50,000 EUR
3. **Por Cliente**: Cliente categoría HIGH o PROHIBITED
4. **Por PEP**: Cualquier alerta que involucre PEP
5. **Por Historial**: Cliente con > 3 alertas en 12 meses
6. **Por Complejidad**: > 10 transacciones relacionadas
7. **Por Tiempo**: Sin progreso en 50% del SLA

### De L2 a L3 (Compliance Officer)

Escalar automáticamente cuando:

1. **Por Score**: Score >= 90
2. **Por Tipo**: SANCTIONS con match potencial confirmado
3. **Por Decisión**: Recomendación de SAR
4. **Por Monto**: Monto > 150,000 EUR
5. **Por Bloqueo**: Se requiere bloqueo de cuenta
6. **Por Regulatorio**: Posible incumplimiento normativo
7. **Por Reputacional**: Cliente de alto perfil público

## Reglas de Re-priorización

### Eventos que Aumentan Prioridad

| Evento | Ajuste de Score |
|--------|-----------------|
| Nueva transacción sospechosa del mismo cliente | +15 |
| Match de sanciones posterior | Automático a CRITICAL |
| Solicitud de información de autoridad | Automático a CRITICAL |
| Cliente intenta cerrar cuenta | +20 |
| Detección de relación con caso existente | +10 |

### Eventos que Pueden Reducir Prioridad

| Evento | Ajuste de Score |
|--------|-----------------|
| Documentación satisfactoria recibida | -10 |
| Verificación positiva de origen de fondos | -15 |
| Confirmación de falso positivo por L2 | Cerrar |

## Notificaciones

### Alertas Automáticas

| Condición | Destinatario | Canal |
|-----------|--------------|-------|
| Nueva alerta CRITICAL | L2 + MLRO | Email + SMS |
| SLA al 75% | Analista asignado | Email |
| SLA al 90% | Analista + Supervisor | Email + Dashboard |
| SLA vencido | Supervisor + MLRO | Email + SMS + Alerta |
| Bloqueo requerido | MLRO | SMS inmediato |

### Reportes Automáticos

| Reporte | Frecuencia | Destinatarios |
|---------|------------|---------------|
| Estado de cola | Cada 4 horas | Supervisores |
| SLAs en riesgo | Cada hora | L2 + MLRO |
| Resumen diario | 08:00 y 18:00 | Todo el equipo |
| Métricas semanales | Lunes 09:00 | Management |

## Gestión de Excepciones

### Extensión de SLA

Permitida solo con:
1. Aprobación del supervisor
2. Justificación documentada
3. Nuevo deadline asignado
4. Máximo 1 extensión por alerta

### Bypass de Escalado

Permitido solo para:
1. Falsos positivos evidentes (con 2 revisiones)
2. Alertas de prueba/test
3. Duplicados confirmados
4. Con aprobación de L2

## Auditoría

### Registro Obligatorio

Cada cambio de estado debe registrar:
- Timestamp
- Usuario
- Estado anterior y nuevo
- Justificación (mínimo 50 caracteres)
- Tiempo en estado anterior

### Métricas de Cumplimiento

| Métrica | Objetivo | Crítico |
|---------|----------|---------|
| % CRITICAL en SLA | > 98% | < 90% |
| % HIGH en SLA | > 95% | < 85% |
| % Escalados correctamente | > 90% | < 80% |
| Tiempo medio de primera respuesta | < 2h | > 4h |
