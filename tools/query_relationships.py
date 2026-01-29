"""Relationship data query tools."""

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from langchain_core.tools import tool

from config.settings import get_settings

settings = get_settings()
DATA_DIR = Path(settings.data_dir)


def _load_relationships() -> pd.DataFrame:
    """Load relationships from parquet file."""
    path = DATA_DIR / "synthetic" / "relationships.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def _load_customers() -> pd.DataFrame:
    """Load customers for enrichment."""
    path = DATA_DIR / "synthetic" / "customers.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@tool
def get_customer_relationships(
    customer_id: str,
    relationship_type: str | None = None,
    include_indirect: bool = False,
) -> str:
    """
    Obtener las relaciones de un cliente específico.

    Args:
        customer_id: ID del cliente
        relationship_type: Filtrar por tipo (FAMILY, BUSINESS, BENEFICIARY, AUTHORIZED, SHARED_ADDRESS, FREQUENT_COUNTERPARTY)
        include_indirect: Incluir relaciones de segundo grado (default: False)

    Returns:
        Lista de entidades relacionadas con el cliente
    """
    df = _load_relationships()
    if df.empty:
        return json.dumps({"error": "No hay datos de relaciones disponibles"})

    # Find direct relationships (as source or target)
    direct = df[
        (df["source_id"] == customer_id) | (df["target_id"] == customer_id)
    ]

    if direct.empty:
        return json.dumps({
            "customer_id": customer_id,
            "relationships": [],
            "count": 0,
            "message": "No se encontraron relaciones para este cliente",
        })

    # Apply type filter
    if relationship_type:
        direct = direct[direct["relationship_type"] == relationship_type.upper()]

    # Process relationships
    relationships = []
    connected_ids = set()

    for _, row in direct.iterrows():
        # Determine the related entity
        if row["source_id"] == customer_id:
            related_id = row["target_id"]
            direction = "outgoing"
        else:
            related_id = row["source_id"]
            direction = "incoming"

        connected_ids.add(related_id)

        rel = {
            "related_entity": related_id,
            "relationship_type": row.get("relationship_type", "UNKNOWN"),
            "direction": direction,
            "strength": row.get("strength", 0),
            "description": row.get("description", ""),
            "created_at": (
                row["created_at"].isoformat()
                if pd.notna(row.get("created_at"))
                else None
            ),
            "verified": row.get("verified", False),
        }
        relationships.append(rel)

    # Include indirect relationships if requested
    indirect_relationships = []
    if include_indirect and connected_ids:
        for connected_id in connected_ids:
            indirect = df[
                ((df["source_id"] == connected_id) | (df["target_id"] == connected_id))
                & (df["source_id"] != customer_id)
                & (df["target_id"] != customer_id)
            ]

            for _, row in indirect.iterrows():
                if row["source_id"] == connected_id:
                    indirect_entity = row["target_id"]
                else:
                    indirect_entity = row["source_id"]

                # Skip if we already have a direct relationship
                if indirect_entity in connected_ids or indirect_entity == customer_id:
                    continue

                indirect_relationships.append({
                    "related_entity": indirect_entity,
                    "via": connected_id,
                    "relationship_type": row.get("relationship_type", "UNKNOWN"),
                    "degree": 2,
                })

    result = {
        "customer_id": customer_id,
        "direct_relationships": relationships,
        "direct_count": len(relationships),
    }

    if include_indirect:
        result["indirect_relationships"] = indirect_relationships[:20]  # Limit
        result["indirect_count"] = len(indirect_relationships)

    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def get_relationship_graph(
    customer_id: str,
    depth: int = 2,
    max_nodes: int = 50,
) -> str:
    """
    Obtener el grafo de relaciones de un cliente para visualización.

    Args:
        customer_id: ID del cliente central
        depth: Profundidad del grafo (default: 2)
        max_nodes: Número máximo de nodos (default: 50)

    Returns:
        Grafo en formato de nodos y aristas para visualización
    """
    df = _load_relationships()
    customers_df = _load_customers()

    if df.empty:
        return json.dumps({"error": "No hay datos de relaciones disponibles"})

    nodes = {}
    edges = []
    visited = set()
    queue = [(customer_id, 0)]

    while queue and len(nodes) < max_nodes:
        current_id, current_depth = queue.pop(0)

        if current_id in visited or current_depth > depth:
            continue

        visited.add(current_id)

        # Add node
        node_info = {"id": current_id, "depth": current_depth}

        # Enrich with customer data if available
        if not customers_df.empty:
            customer = customers_df[customers_df["customer_id"] == current_id]
            if not customer.empty:
                c = customer.iloc[0]
                node_info.update({
                    "name": c.get("full_name", current_id),
                    "type": c.get("customer_type", "unknown"),
                    "risk_level": c.get("risk_level", "UNKNOWN"),
                })

        nodes[current_id] = node_info

        # Find connected entities
        if current_depth < depth:
            connections = df[
                (df["source_id"] == current_id) | (df["target_id"] == current_id)
            ]

            for _, row in connections.iterrows():
                if row["source_id"] == current_id:
                    other_id = row["target_id"]
                    source, target = current_id, other_id
                else:
                    other_id = row["source_id"]
                    source, target = other_id, current_id

                # Add edge
                edge = {
                    "source": source,
                    "target": target,
                    "type": row.get("relationship_type", "UNKNOWN"),
                    "strength": row.get("strength", 0),
                }
                if edge not in edges:
                    edges.append(edge)

                # Add to queue
                if other_id not in visited:
                    queue.append((other_id, current_depth + 1))

    return json.dumps(
        {
            "center_node": customer_id,
            "depth": depth,
            "nodes": list(nodes.values()),
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        ensure_ascii=False,
        indent=2,
    )


@tool
def find_connected_entities(
    entity_ids: list[str],
    relationship_types: list[str] | None = None,
) -> str:
    """
    Encontrar conexiones entre un conjunto de entidades.

    Args:
        entity_ids: Lista de IDs de entidades a analizar
        relationship_types: Tipos de relación a considerar (opcional)

    Returns:
        Conexiones encontradas entre las entidades especificadas
    """
    df = _load_relationships()
    if df.empty:
        return json.dumps({"error": "No hay datos de relaciones disponibles"})

    entity_set = set(entity_ids)

    # Find direct connections between entities
    direct_connections = df[
        (df["source_id"].isin(entity_set)) & (df["target_id"].isin(entity_set))
    ]

    if relationship_types:
        relationship_types_upper = [rt.upper() for rt in relationship_types]
        direct_connections = direct_connections[
            direct_connections["relationship_type"].isin(relationship_types_upper)
        ]

    # Find common connections (entities connected to multiple targets)
    all_connections = df[
        (df["source_id"].isin(entity_set)) | (df["target_id"].isin(entity_set))
    ]

    if relationship_types:
        all_connections = all_connections[
            all_connections["relationship_type"].isin(relationship_types_upper)
        ]

    # Count connections per external entity
    connection_counts = defaultdict(lambda: {"connected_to": [], "types": []})

    for _, row in all_connections.iterrows():
        if row["source_id"] in entity_set:
            external = row["target_id"]
            internal = row["source_id"]
        else:
            external = row["source_id"]
            internal = row["target_id"]

        if external not in entity_set:
            connection_counts[external]["connected_to"].append(internal)
            connection_counts[external]["types"].append(row.get("relationship_type", "UNKNOWN"))

    # Find shared connections (connected to 2+ entities)
    shared_connections = {
        entity: data
        for entity, data in connection_counts.items()
        if len(set(data["connected_to"])) >= 2
    }

    # Format direct connections
    direct_list = []
    for _, row in direct_connections.iterrows():
        direct_list.append({
            "source": row["source_id"],
            "target": row["target_id"],
            "type": row.get("relationship_type", "UNKNOWN"),
            "strength": row.get("strength", 0),
        })

    # Format shared connections
    shared_list = []
    for entity, data in shared_connections.items():
        shared_list.append({
            "shared_entity": entity,
            "connects": list(set(data["connected_to"])),
            "relationship_types": list(set(data["types"])),
            "connection_count": len(set(data["connected_to"])),
        })

    # Sort by number of connections
    shared_list.sort(key=lambda x: x["connection_count"], reverse=True)

    return json.dumps(
        {
            "entities_analyzed": list(entity_ids),
            "direct_connections": direct_list,
            "direct_connection_count": len(direct_list),
            "shared_connections": shared_list[:20],  # Limit
            "shared_connection_count": len(shared_list),
            "analysis": {
                "entities_with_connections": len(
                    set(
                        [c["source"] for c in direct_list]
                        + [c["target"] for c in direct_list]
                    )
                ),
                "most_connected_shared": (
                    shared_list[0]["shared_entity"] if shared_list else None
                ),
            },
        },
        ensure_ascii=False,
        indent=2,
    )
