# Patrones de Red Sospechosos

## 1. Patrón Hub-Spoke (Estrella)

### Descripción
Un nodo central actúa como punto de agregación o distribución de fondos.

### Visualización
```
        [A]
         |
    [B]--[X]--[C]
        / \
      [D] [E]
```

### Indicadores
- Nodo central con >5 conexiones activas
- Flujo predominantemente en una dirección (entrante o saliente)
- Nodos periféricos sin conexión entre sí
- Montos similares desde/hacia periféricos

### Tipologías Asociadas
- **Smurfing:** Múltiples depositantes hacia cuenta central
- **Distribución:** Cuenta central hacia múltiples beneficiarios
- **Cuenta de recogida:** Agente que consolida fondos

### Score de Sospecha
- Base: +30
- +5 por cada conexión periférica adicional (>5)
- +10 si periféricos son de diferentes países
- +15 si nodos periféricos son todos nuevos (<6 meses)

---

## 2. Patrón Circular (Round-Trip)

### Descripción
Fondos que retornan al origen a través de intermediarios.

### Visualización
```
    [A] ──→ [B]
     ↑       |
     |       ↓
    [D] ←── [C]
```

### Indicadores
- Camino cerrado de transacciones
- Tiempo total del ciclo < 30 días
- Montos similares (con pequeñas variaciones por comisiones)
- Sin propósito económico aparente

### Tipologías Asociadas
- **Layering:** Obscurecer origen de fondos
- **Préstamo ficticio:** Simular deuda/pago
- **Inflación de facturación:** Justificar ingresos

### Score de Sospecha
- Base: +40
- +10 si ciclo completado en <7 días
- +15 si involucra jurisdicción de alto riesgo
- +5 por cada nodo adicional en el ciclo

---

## 3. Patrón Cadena (Layering Chain)

### Descripción
Flujo unidireccional a través de múltiples intermediarios.

### Visualización
```
[A] ──→ [B] ──→ [C] ──→ [D] ──→ [E]
```

### Indicadores
- Transferencias secuenciales en <48h
- Cada nodo retiene fondos brevemente
- Montos decrecientes (por comisiones)
- Destino final en jurisdicción diferente

### Tipologías Asociadas
- **Layering clásico:** Múltiples capas de transacciones
- **Transferencias en cascada:** Obscurecer beneficiario final

### Score de Sospecha
- Base: +25
- +5 por cada nodo adicional (>3)
- +15 si termina en país de alto riesgo
- +10 si nodos intermedios son shell companies

---

## 4. Patrón Clique (Grupo Cerrado)

### Descripción
Grupo de nodos con conexiones bidireccionales entre todos los miembros.

### Visualización
```
    [A] ←──→ [B]
     ↑↓  ╲╱  ↑↓
    [D] ←──→ [C]
```

### Indicadores
- Todos los nodos conectados entre sí
- Flujos bidireccionales frecuentes
- Patrones de transacción coordinados
- Comparten características (sector, ubicación)

### Tipologías Asociadas
- **Red organizada:** Grupo criminal coordinado
- **Trade-based laundering:** Facturas cruzadas
- **Control de empresas:** Grupo empresarial opaco

### Score de Sospecha
- Base: +35
- +5 por cada miembro adicional (>3)
- +20 si miembros comparten dirección
- +10 si montos son sospechosamente similares

---

## 5. Patrón Funnel (Embudo)

### Descripción
Múltiples fuentes convergen hacia un destino común.

### Visualización
```
[A] ──┐
[B] ──┼──→ [X] ──→ [Y]
[C] ──┘
```

### Indicadores
- Múltiples orígenes, un destino
- Transferencias en ventana temporal corta
- Destino realiza una gran transferencia posterior
- Sin relación declarada entre orígenes

### Tipologías Asociadas
- **Consolidación para transferencia internacional**
- **Evasión de umbrales de reporte**
- **Preparación para extracción**

### Score de Sospecha
- Base: +30
- +10 si consolidación >50K EUR
- +15 si transferencia posterior es internacional
- +5 por cada origen adicional (>3)

---

## Matriz de Combinación de Patrones

Cuando se detectan múltiples patrones, combinar scores:

| Combinación | Score Adicional |
|-------------|-----------------|
| Hub + Circular | +20 |
| Cadena + Funnel | +15 |
| Clique + cualquiera | +25 |
| 3+ patrones | +30 |

## Umbrales de Acción

| Score Total | Acción |
|-------------|--------|
| < 30 | Monitoreo normal |
| 30-50 | Revisión L1 |
| 51-70 | Investigación L2 |
| > 70 | Escalado inmediato + posible SAR |
