# Principios GDPR para Acceso a Datos de Cliente

## Marco Legal

El Reglamento General de Protección de Datos (RGPD/GDPR) establece principios que deben respetarse al acceder y procesar datos personales de clientes.

## Principios Aplicables

### 1. Licitud, Lealtad y Transparencia (Art. 5.1.a)

El acceso a datos del cliente debe basarse en una base legal válida:

| Base Legal | Aplicación en AML/KYC |
|------------|----------------------|
| Obligación legal | Cumplimiento Ley 10/2010 |
| Interés legítimo | Prevención de fraude |
| Contrato | Gestión de la relación bancaria |

**Requisito:** Siempre documentar la base legal del acceso.

### 2. Limitación de Finalidad (Art. 5.1.b)

Los datos solo pueden usarse para fines específicos:

**Fines legítimos para Customer 360:**
- Cumplimiento normativo AML/CFT
- Gestión de riesgos
- Prevención de fraude
- Atención de requerimientos regulatorios

**Fines NO permitidos sin consentimiento adicional:**
- Marketing
- Perfilado comercial
- Cesión a terceros no autorizados

### 3. Minimización de Datos (Art. 5.1.c)

**Principio:** Acceder SOLO a los datos necesarios para el propósito específico.

**Implementación en Customer 360:**

| Propósito | Secciones Permitidas |
|-----------|---------------------|
| Revisión de alerta | Todas |
| Verificación KYC | identity, kyc_status |
| Análisis de riesgo | risk_profile, behavioral_metrics |
| Informe para autoridad | Todas (con orden/requerimiento) |

**El parámetro `sections` permite filtrar:**
```json
{
  "customer_id": "C-1234",
  "purpose": "Verificación KYC periódica",
  "sections": ["identity", "kyc_status"]
}
```

### 4. Exactitud (Art. 5.1.d)

- Los datos mostrados deben estar actualizados
- Indicar fecha de última actualización
- Marcar datos pendientes de verificación

### 5. Limitación del Plazo de Conservación (Art. 5.1.e)

| Tipo de Dato | Plazo de Conservación |
|--------------|----------------------|
| KYC básico | 10 años desde fin de relación |
| Transacciones | 10 años |
| Alertas | 10 años |
| Logs de acceso | 5 años |

**Nota:** El plazo de 10 años viene de la Ley 10/2010, que prevalece sobre plazos menores.

### 6. Integridad y Confidencialidad (Art. 5.1.f)

**Medidas requeridas:**
- Acceso autenticado
- Log de todos los accesos
- Cifrado en tránsito y reposo
- Principio de need-to-know

## Implementación de Minimización

### Matriz de Acceso por Rol

| Rol | Secciones Accesibles |
|-----|---------------------|
| Analista L1 | identity, kyc_status, alert_history, behavioral_metrics |
| Analista L2 | Todas excepto relationships completas |
| Compliance Officer | Todas |
| Auditor | Todas (solo lectura) |
| Sistema automatizado | Solo métricas agregadas |

### Campos Sensibles

Algunos campos requieren justificación adicional:

| Campo | Nivel de Sensibilidad | Requisito |
|-------|----------------------|-----------|
| Ingresos detallados | Alto | Propósito específico |
| Relaciones familiares | Alto | Solo si relevante para alerta |
| Historial médico | Muy alto | Solo con base legal específica |
| Orientación política | Prohibido | No recopilar |

## Registro de Accesos (Art. 30)

Cada acceso a Customer 360 debe registrar:

```json
{
  "timestamp": "2025-01-29T10:30:00Z",
  "user_id": "ANALYST-123",
  "user_role": "L2_ANALYST",
  "customer_id": "C-4821",
  "purpose": "Revisión alerta ALT-2847",
  "sections_accessed": ["identity", "risk_profile", "alert_history"],
  "legal_basis": "LEGAL_OBLIGATION",
  "reference": "ALT-2847"
}
```

## Derechos del Interesado

El Customer 360 puede usarse para atender derechos GDPR:

### Derecho de Acceso (Art. 15)

El cliente puede solicitar copia de sus datos:
- Usar Customer 360 con `sections: all`
- Formato exportable
- Excluir datos de terceros relacionados

### Derecho de Rectificación (Art. 16)

Si el cliente identifica datos incorrectos:
- Verificar y actualizar
- Registrar el cambio
- Notificar a terceros si se compartió

### Derecho de Supresión (Art. 17)

**Excepciones para AML:**
- Los datos de prevención de blanqueo están exentos de supresión
- Base legal: Art. 17.3.b (obligación legal)
- Informar al cliente de la excepción

## Transferencias Internacionales

Si el Customer 360 muestra datos que implican transferencias:

| Destino | Requisito |
|---------|-----------|
| UE/EEE | Ninguno adicional |
| Decisión de adecuación | Verificar vigencia |
| Sin adecuación | Cláusulas contractuales tipo |
| Autoridades extranjeras | Solo vía SEPBLAC/canales oficiales |

## Incidentes de Seguridad

Si se detecta acceso no autorizado a Customer 360:

1. **Notificación AEPD:** 72 horas si riesgo para derechos
2. **Notificación cliente:** Sin dilación indebida si alto riesgo
3. **Documentación:** Registro completo del incidente
4. **Medidas:** Acciones correctivas inmediatas

## Checklist de Cumplimiento

Antes de acceder a Customer 360:

- [ ] ¿Tengo un propósito legítimo documentado?
- [ ] ¿Estoy accediendo solo a las secciones necesarias?
- [ ] ¿Mi rol me autoriza este acceso?
- [ ] ¿He registrado el propósito del acceso?
- [ ] ¿Los datos se usarán solo para el fin declarado?
