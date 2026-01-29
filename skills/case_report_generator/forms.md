# INFORME DE COMUNICACIÓN POR INDICIO (SAR)

---

## DATOS DEL INFORME

| Campo | Valor |
|-------|-------|
| **Número de Referencia** | SAR-{{YEAR}}-{{SEQUENCE}} |
| **Tipo de Comunicación** | {{REPORT_TYPE}} |
| **Fecha de Generación** | {{GENERATION_DATE}} |
| **Preparado por** | {{ANALYST_NAME}} ({{ANALYST_ID}}) |
| **Revisado por** | {{REVIEWER_NAME}} |
| **Estado** | {{STATUS}} |

---

## 1. DATOS DEL SUJETO

### 1.1 Identificación

| Campo | Valor |
|-------|-------|
| **Nombre Completo** | {{SUBJECT_NAME}} |
| **Tipo de Documento** | {{DOCUMENT_TYPE}} |
| **Número de Documento** | {{DOCUMENT_NUMBER}} |
| **Fecha de Nacimiento** | {{DATE_OF_BIRTH}} |
| **Nacionalidad** | {{NATIONALITY}} |
| **País de Residencia** | {{RESIDENCE_COUNTRY}} |

### 1.2 Datos de Contacto

| Campo | Valor |
|-------|-------|
| **Dirección** | {{ADDRESS}} |
| **Teléfono** | {{PHONE}} |
| **Email** | {{EMAIL}} |

### 1.3 Relación con la Entidad

| Campo | Valor |
|-------|-------|
| **Fecha de Alta** | {{CUSTOMER_SINCE}} |
| **Productos Contratados** | {{PRODUCTS}} |
| **Categoría de Riesgo** | {{RISK_CATEGORY}} |
| **Estado PEP** | {{PEP_STATUS}} |

---

## 2. RESUMEN EJECUTIVO

### 2.1 Tipología Detectada

**{{TYPOLOGY}}**

### 2.2 Período de Análisis

Del **{{PERIOD_START}}** al **{{PERIOD_END}}**

### 2.3 Cuantificación

| Métrica | Valor |
|---------|-------|
| **Monto Total Involucrado** | {{TOTAL_AMOUNT}} EUR |
| **Número de Transacciones** | {{TRANSACTION_COUNT}} |
| **Número de Contrapartes** | {{COUNTERPARTY_COUNT}} |

### 2.4 Descripción Breve

{{BRIEF_DESCRIPTION}}

---

## 3. NARRATIVA DEL CASO

### 3.1 Antecedentes

{{BACKGROUND}}

### 3.2 Detección Inicial

{{INITIAL_DETECTION}}

### 3.3 Investigación Realizada

{{INVESTIGATION_SUMMARY}}

### 3.4 Hallazgos Principales

{{KEY_FINDINGS}}

---

## 4. DETALLE DE OPERACIONES

### 4.1 Transacciones Sospechosas

| Fecha | Tipo | Monto | Origen/Destino | Concepto | Indicadores |
|-------|------|-------|----------------|----------|-------------|
{{#TRANSACTIONS}}
| {{DATE}} | {{TYPE}} | {{AMOUNT}} EUR | {{COUNTERPARTY}} | {{CONCEPT}} | {{INDICATORS}} |
{{/TRANSACTIONS}}

### 4.2 Análisis de Patrones

{{PATTERN_ANALYSIS}}

---

## 5. CRONOLOGÍA DE EVENTOS

| Fecha | Evento | Descripción |
|-------|--------|-------------|
{{#TIMELINE}}
| {{DATE}} | {{EVENT_TYPE}} | {{DESCRIPTION}} |
{{/TIMELINE}}

---

## 6. EVIDENCIA ADJUNTA

### 6.1 Documentos

| ID | Tipo | Descripción | Fecha |
|----|------|-------------|-------|
{{#DOCUMENTS}}
| {{DOC_ID}} | {{DOC_TYPE}} | {{DOC_DESCRIPTION}} | {{DOC_DATE}} |
{{/DOCUMENTS}}

### 6.2 Capturas de Pantalla

{{SCREENSHOTS_REFERENCE}}

---

## 7. ANÁLISIS Y CONCLUSIONES

### 7.1 Indicadores de Sospecha

{{#SUSPICION_INDICATORS}}
- {{INDICATOR}}
{{/SUSPICION_INDICATORS}}

### 7.2 Evaluación de Riesgo

{{RISK_EVALUATION}}

### 7.3 Conclusión

{{CONCLUSION}}

---

## 8. RECOMENDACIÓN

**{{RECOMMENDATION}}**

### 8.1 Acciones Sugeridas

{{#SUGGESTED_ACTIONS}}
- {{ACTION}}
{{/SUGGESTED_ACTIONS}}

---

## 9. FIRMAS Y APROBACIONES

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Analista | {{ANALYST_NAME}} | {{ANALYST_DATE}} | ________________ |
| Supervisor | {{SUPERVISOR_NAME}} | {{SUPERVISOR_DATE}} | ________________ |
| MLRO | {{MLRO_NAME}} | {{MLRO_DATE}} | ________________ |

---

## ANEXOS

- Anexo A: Extracto de transacciones completo
- Anexo B: Perfil KYC del cliente
- Anexo C: Documentación de soporte
- Anexo D: Grafo de relaciones (si aplica)

---

*Este documento es confidencial y está destinado exclusivamente para comunicación al SEPBLAC conforme a la Ley 10/2010. Queda prohibida su divulgación al sujeto investigado o a terceros no autorizados.*

**Referencia interna:** {{INTERNAL_REFERENCE}}

**Código de verificación:** {{VERIFICATION_CODE}}
