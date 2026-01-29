# Algoritmos de Análisis de Grafos

## Métricas de Nodos

### Centralidad de Grado (Degree Centrality)
Número de conexiones directas de un nodo.
- **Alto grado entrante:** Posible cuenta de recogida
- **Alto grado saliente:** Posible cuenta de distribución

### Centralidad de Intermediación (Betweenness)
Frecuencia con que un nodo aparece en caminos más cortos.
- **Alta intermediación:** Nodo crítico en la red, posible "puente"

### PageRank
Importancia del nodo basada en importancia de sus conexiones.
- **Alto PageRank:** Nodo conectado a otros nodos importantes

## Detección de Comunidades

### Algoritmo de Louvain
Detecta comunidades maximizando modularidad.
- Útil para identificar clusters naturales
- Complejidad: O(n log n)

### Label Propagation
Propaga etiquetas hasta convergencia.
- Rápido pero menos preciso
- Útil para grafos grandes

## Detección de Patrones

### Ciclos (Circular Transactions)
```python
def detect_cycles(graph, max_length=5):
    """Detecta ciclos de hasta max_length nodos."""
    cycles = []
    for node in graph.nodes():
        for path in dfs_paths(graph, node, node, max_length):
            if len(path) > 2:
                cycles.append(path)
    return cycles
```

### Hub Detection
```python
def detect_hubs(graph, threshold=5):
    """Identifica nodos con grado > threshold."""
    hubs = []
    for node in graph.nodes():
        if graph.degree(node) > threshold:
            hubs.append({
                'node': node,
                'in_degree': graph.in_degree(node),
                'out_degree': graph.out_degree(node)
            })
    return hubs
```

### Clique Detection
```python
def find_cliques(graph, min_size=3):
    """Encuentra subgrafos completamente conectados."""
    return [c for c in nx.find_cliques(graph) if len(c) >= min_size]
```

## Cálculo de Fuerza de Relación

```python
def calculate_strength(edge_data, days=365):
    """
    Calcula fuerza de relación entre 0 y 1.

    Factores:
    - Recencia (40%): Más reciente = más fuerte
    - Frecuencia (30%): Más interacciones = más fuerte
    - Volumen (30%): Mayor monto = más fuerte
    """
    recency_factor = max(0, 1 - (days_since_last / days))
    frequency_factor = min(1, interaction_count / 50)
    volume_factor = min(1, total_amount / 100000)

    strength = (
        recency_factor * 0.4 +
        frequency_factor * 0.3 +
        volume_factor * 0.3
    )
    return round(strength, 2)
```

## Score de Sospecha de Arista

| Factor | Score |
|--------|-------|
| Conexión con nodo HIGH risk | +20 |
| Volumen > 50K sin relación declarada | +25 |
| Transacciones solo en redondo | +15 |
| Conexión bidireccional rápida (<24h) | +20 |
| Parte de ciclo detectado | +30 |
| Nodos comparten dispositivo/IP | +35 |
