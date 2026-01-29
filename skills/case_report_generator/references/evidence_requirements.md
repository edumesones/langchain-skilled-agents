# Requisitos de Evidencia por Tipología

## Principios Generales

### Cadena de Custodia
- Documentar origen de cada evidencia
- Timestamp de captura
- Usuario que recopiló
- Sin alteraciones

### Suficiencia
- Evidencia debe soportar la conclusión
- Incluir contexto, no solo datos aislados
- Documentar lo que NO se encontró también

## Por Tipología

### STRUCTURING

**Evidencia Mínima:**
- Listado de todas las operaciones del patrón
- Fechas, montos, canal de cada una
- Visualización del patrón temporal

**Evidencia Adicional:**
- Comparación con umbral regulatorio
- Historial de operaciones previas (patrón nuevo vs recurrente)
- Declaración del cliente si se solicitó

**Visualización:**
- Gráfico temporal mostrando fragmentación
- Tabla comparativa pre/post detección

---

### LAYERING

**Evidencia Mínima:**
- Diagrama de flujo de fondos
- Todas las cuentas intermediarias
- Timestamps que muestren rapidez

**Evidencia Adicional:**
- Relación entre titulares de cuentas
- Justificaciones económicas (o ausencia)
- Destino final de fondos

**Visualización:**
- Grafo de flujo con montos
- Timeline de movimientos

---

### SMURFING

**Evidencia Mínima:**
- Identificación de todos los "smurfs"
- Relación (o aparente no-relación) entre ellos
- Cuenta destino común

**Evidencia Adicional:**
- Origen de fondos de cada smurf
- Coordiación temporal
- Canal utilizado (mismo punto de servicio, etc)

**Visualización:**
- Grafo hub-spoke
- Mapa geográfico si aplica

---

### PEP

**Evidencia Mínima:**
- Documentación del estatus PEP
- Operación(es) que generaron alerta
- Comparación con perfil esperado

**Evidencia Adicional:**
- Fuente de verificación PEP
- Historial de operaciones
- Declaración de origen de fondos

**Documentación específica:**
- Captura de base de datos PEP
- Fecha de última verificación

---

### SANCTIONS

**Evidencia Mínima:**
- Match de screening
- Lista en la que aparece
- Nivel de coincidencia (exacto/parcial)

**Evidencia Adicional:**
- Verificación de identidad
- Análisis de falso positivo (si se descarta)
- Operaciones bloqueadas/ejecutadas

**Documentación específica:**
- Captura del screening
- Fecha y versión de listas

---

### GEOGRAPHIC

**Evidencia Mínima:**
- Listado de operaciones con país de riesgo
- Clasificación del país (GAFI, UE, etc)
- Monto total y frecuencia

**Evidencia Adicional:**
- Justificación del cliente
- Relación declarada con el país
- Historial de operaciones con ese país

**Documentación específica:**
- Clasificación oficial del país
- Evolución si cambió recientemente

---

### UNUSUAL_ACTIVITY

**Evidencia Mínima:**
- Descripción del comportamiento anómalo
- Comparación con baseline del cliente
- Cuantificación de la desviación

**Evidencia Adicional:**
- Perfil esperado documentado
- Intentos de contacto con cliente
- Eventos vitales conocidos

**Visualización:**
- Gráfico comparativo esperado vs real
- Evolución temporal

---

## Formato de Documentación

### Extracto de Transacciones

| Campo | Obligatorio |
|-------|-------------|
| Fecha/hora | Sí |
| Referencia | Sí |
| Tipo | Sí |
| Importe | Sí |
| Divisa | Sí |
| Ordenante | Sí |
| Beneficiario | Sí |
| Concepto | Sí |
| País destino | Si internacional |
| Canal | Recomendado |

### Captura de Pantalla

- Incluir fecha y hora visible
- Mostrar contexto suficiente
- Anonimizar datos de terceros no relevantes
- Formato PNG o PDF

### Notas de Investigación

- Fecha y autor
- Acciones realizadas
- Resultados obtenidos
- Siguientes pasos
