# Modelo de Scoring de Riesgo del Cliente

## Descripción General

El modelo de scoring asigna una puntuación de riesgo de 0 a 100 a cada cliente basándose en múltiples factores. Esta puntuación determina:
- Nivel de diligencia debida aplicable
- Frecuencia de monitorización
- Umbrales de alerta personalizados
- Requisitos de aprobación

## Componentes del Score

El score final se calcula como suma ponderada de 5 componentes:

| Componente | Peso | Descripción |
|------------|------|-------------|
| Riesgo Geográfico | 25% | País de nacionalidad/residencia/operativa |
| Riesgo de Cliente | 25% | Tipo de cliente, PEP, profesión |
| Riesgo de Producto | 15% | Productos contratados |
| Riesgo de Canal | 10% | Canal de captación y operativa |
| Riesgo de Comportamiento | 25% | Patrón transaccional |

## 1. Riesgo Geográfico (0-100)

### Por Nacionalidad

| Clasificación | Score | Países |
|---------------|-------|--------|
| Bajo riesgo | 10 | UE, EEE, equivalentes GAFI |
| Riesgo medio | 40 | OCDE resto, países emergentes estables |
| Riesgo alto | 70 | Lista gris GAFI, paraísos fiscales |
| Riesgo muy alto | 100 | Lista negra GAFI, sancionados |

### Por Residencia (adicional)

Si residencia ≠ nacionalidad y es de mayor riesgo: +20

### Por Países de Operativa

- Cada país de alto riesgo en operativa habitual: +10 (máx +30)

## 2. Riesgo de Cliente (0-100)

### Por Tipo de Cliente

| Tipo | Score Base |
|------|------------|
| Asalariado | 10 |
| Autónomo | 20 |
| Empresario | 30 |
| Jubilado | 15 |
| Estudiante | 15 |
| Desempleado | 25 |
| Sin información | 40 |

### Modificadores PEP

| Condición | Ajuste |
|-----------|--------|
| PEP Nacional activo | +50 |
| PEP Extranjero activo | +40 |
| PEP Organismo Internacional | +45 |
| Ex-PEP (<2 años) | +25 |
| Familiar PEP 1er grado | +30 |
| Asociado cercano PEP | +25 |

### Por Sector Económico

| Sector | Ajuste |
|--------|--------|
| Inmobiliario | +15 |
| Joyería/metales preciosos | +20 |
| Juego/apuestas | +25 |
| Criptoactivos | +25 |
| Arte/antigüedades | +15 |
| Efectivo intensivo | +20 |
| Servicios financieros no regulados | +30 |

## 3. Riesgo de Producto (0-100)

| Producto | Score |
|----------|-------|
| Cuenta corriente básica | 10 |
| Cuenta de ahorro | 10 |
| Tarjeta de débito | 10 |
| Tarjeta de crédito | 20 |
| Préstamo personal | 25 |
| Hipoteca | 15 |
| Inversiones | 30 |
| Banca privada | 40 |
| Transferencias internacionales frecuentes | +20 |
| Efectivo frecuente | +25 |

Score del producto = máximo de productos contratados + suma de modificadores

## 4. Riesgo de Canal (0-100)

| Canal de Captación | Score |
|--------------------|-------|
| Sucursal presencial | 15 |
| Online con videoID | 25 |
| Online solo documental | 35 |
| App móvil | 30 |
| Agente/intermediario | 40 |
| Referido (sin verificación) | 45 |

### Canal de Operativa Habitual

| Canal | Modificador |
|-------|-------------|
| Predominantemente digital | 0 |
| Mixto digital/presencial | +5 |
| Predominantemente efectivo | +20 |
| Exclusivamente efectivo | +35 |

## 5. Riesgo de Comportamiento (0-100)

Calculado dinámicamente basado en:

### Desviación de Perfil Esperado

| Desviación | Score |
|------------|-------|
| < 15% | 10 |
| 15-30% | 25 |
| 30-50% | 45 |
| 50-100% | 65 |
| > 100% | 85 |

### Historial de Alertas

| Condición | Ajuste |
|-----------|--------|
| Sin alertas previas | 0 |
| 1 alerta cerrada FP | +5 |
| 2-3 alertas cerradas FP | +10 |
| Alerta con SAR | +40 |
| Alerta abierta actual | +20 |

### Patrones Sospechosos

| Patrón | Ajuste |
|--------|--------|
| Transacciones redondas frecuentes | +10 |
| Operaciones justo bajo umbral | +15 |
| Rapidez inusual de movimientos | +15 |
| Nuevos beneficiarios de alto riesgo | +20 |

## Cálculo Final

```
Score = (Geo × 0.25) + (Cliente × 0.25) + (Producto × 0.15) +
        (Canal × 0.10) + (Comportamiento × 0.25)

Score final = min(100, max(0, Score))
```

## Categorías de Riesgo

| Score | Categoría | Diligencia | Frecuencia Review |
|-------|-----------|------------|-------------------|
| 0-25 | LOW | Simplificada | 5 años |
| 26-50 | MEDIUM | Estándar | 2 años |
| 51-75 | HIGH | Reforzada | 1 año |
| 76-100 | PROHIBITED | No operar | N/A |

## Triggers de Recálculo

El score debe recalcularse cuando:
- Actualización de datos KYC
- Nueva alerta generada
- Cambio de productos
- Operativa en nuevo país
- Cada 90 días automáticamente
- Solicitud de compliance

## Gobernanza

- **Modelo propietario**: Equipo de Risk Analytics
- **Validación**: Auditoría interna anual
- **Aprobación**: Comité de Riesgos
- **Override manual**: Solo con aprobación MLRO (documentar)
