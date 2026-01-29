# DOCUMENTACIÓN DE DECISIÓN

---

## DATOS DE LA DECISIÓN

| Campo | Valor |
|-------|-------|
| **ID de Decisión** | DEC-{{YEAR}}-{{SEQUENCE}} |
| **Alerta Relacionada** | {{ALERT_ID}} |
| **Caso Relacionado** | {{CASE_ID}} |
| **Fecha de Decisión** | {{DECISION_DATE}} |
| **Decidido por** | {{ANALYST_NAME}} ({{ANALYST_ID}}) |
| **Nivel del Analista** | {{ANALYST_LEVEL}} |

---

## 1. DECISIÓN

### Outcome Seleccionado

**{{DECISION_OUTCOME}}**

- [ ] SAR_FILED - Comunicación al SEPBLAC
- [ ] CLOSED_FP - Cerrado como Falso Positivo
- [ ] CLOSED_NO_ACTION - Cerrado sin Acción
- [ ] CLOSED_LEGITIMATE - Actividad Legítima Verificada
- [ ] ESCALATED - Escalado a Nivel Superior
- [ ] BLOCKED - Cuenta/Operación Bloqueada

---

## 2. RESUMEN EJECUTIVO

### Descripción de la Decisión (1-2 oraciones)

{{DECISION_SUMMARY}}

### Factores Clave

1. {{KEY_FACTOR_1}}
2. {{KEY_FACTOR_2}}
3. {{KEY_FACTOR_3}}

---

## 3. ANÁLISIS REALIZADO

### 3.1 Información Revisada

| Tipo de Información | Revisado | Notas |
|---------------------|----------|-------|
| Perfil del cliente (KYC) | [ ] Sí / [ ] No | {{KYC_NOTES}} |
| Historial de transacciones | [ ] Sí / [ ] No | {{TX_NOTES}} |
| Alertas previas | [ ] Sí / [ ] No | {{ALERTS_NOTES}} |
| Documentación del cliente | [ ] Sí / [ ] No | {{DOCS_NOTES}} |
| Fuentes externas | [ ] Sí / [ ] No | {{EXTERNAL_NOTES}} |

### 3.2 Hallazgos del Análisis

**Indicadores de sospecha encontrados:**
{{SUSPICION_INDICATORS_FOUND}}

**Factores mitigantes identificados:**
{{MITIGATING_FACTORS}}

### 3.3 Información Faltante o Limitaciones

{{LIMITATIONS}}

---

## 4. RAZONAMIENTO DETALLADO

### 4.1 Argumentos a Favor de la Decisión

{{ARGUMENTS_FOR}}

### 4.2 Argumentos en Contra Considerados

{{ARGUMENTS_AGAINST}}

### 4.3 Alternativas Evaluadas

| Alternativa | Motivo de Descarte |
|-------------|-------------------|
| {{ALT_1}} | {{ALT_1_REASON}} |
| {{ALT_2}} | {{ALT_2_REASON}} |

---

## 5. BASE REGULATORIA

### Normativa Aplicable

- [ ] Ley 10/2010 de PBC/FT
- [ ] RD 304/2014 (Reglamento)
- [ ] Directiva UE 2015/849 (4AMLD)
- [ ] Directiva UE 2018/843 (5AMLD)
- [ ] GDPR
- [ ] Políticas internas

### Artículos Específicos

| Norma | Artículo | Aplicación |
|-------|----------|------------|
| {{NORM_1}} | Art. {{ART_1}} | {{APPLICATION_1}} |

---

## 6. EVIDENCIA DE SOPORTE

### Documentos Consultados

| ID | Tipo | Descripción | Fecha |
|----|------|-------------|-------|
| {{DOC_ID_1}} | {{DOC_TYPE_1}} | {{DOC_DESC_1}} | {{DOC_DATE_1}} |

### Sistemas Consultados

- [ ] Core bancario
- [ ] Sistema de alertas
- [ ] CRM
- [ ] Screening de sanciones
- [ ] Bases de datos PEP
- [ ] Otros: {{OTHER_SYSTEMS}}

---

## 7. CHECKLIST DE CUMPLIMIENTO

| Requisito | Cumplido | Comentario |
|-----------|----------|------------|
| Revisión de perfil KYC | [ ] Sí / [ ] No / [ ] N/A | |
| Análisis de transacciones completo | [ ] Sí / [ ] No / [ ] N/A | |
| Verificación de sanciones actualizada | [ ] Sí / [ ] No / [ ] N/A | |
| Documentación solicitada (si aplica) | [ ] Sí / [ ] No / [ ] N/A | |
| Documentación recibida y revisada | [ ] Sí / [ ] No / [ ] N/A | |
| Consulta con supervisor (si requerido) | [ ] Sí / [ ] No / [ ] N/A | |
| EDD aplicada (si requerido) | [ ] Sí / [ ] No / [ ] N/A | |

---

## 8. SEGUIMIENTO (si aplica)

### Acciones de Seguimiento

| Acción | Responsable | Fecha Límite | Estado |
|--------|-------------|--------------|--------|
| {{ACTION_1}} | {{RESPONSIBLE_1}} | {{DEADLINE_1}} | [ ] Pendiente |

### Próxima Revisión

**Fecha:** {{NEXT_REVIEW_DATE}}
**Motivo:** {{NEXT_REVIEW_REASON}}

---

## 9. APROBACIONES

### Analista

| Campo | Valor |
|-------|-------|
| Nombre | {{ANALYST_NAME}} |
| Fecha | {{ANALYST_DATE}} |
| Firma | ________________ |

### Supervisor (si requerido)

| Campo | Valor |
|-------|-------|
| Nombre | {{SUPERVISOR_NAME}} |
| Fecha | {{SUPERVISOR_DATE}} |
| Firma | ________________ |
| Comentarios | {{SUPERVISOR_COMMENTS}} |

---

## 10. HISTORIAL DE AUDITORÍA

| Fecha/Hora | Usuario | Acción | Detalle |
|------------|---------|--------|---------|
| {{TIMESTAMP_1}} | {{USER_1}} | {{ACTION_1}} | {{DETAIL_1}} |

---

*Este documento forma parte del expediente de compliance y debe conservarse durante 10 años conforme al Art. 25 de la Ley 10/2010.*

**Hash de integridad:** {{INTEGRITY_HASH}}
