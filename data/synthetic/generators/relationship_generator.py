"""Relationship/Graph data generator for synthetic fintech data."""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from faker import Faker

fake = Faker(["es_ES"])
Faker.seed(42)
random.seed(42)


# =============================================================================
# Constants
# =============================================================================

ENTITY_TYPES = ["CUSTOMER", "ACCOUNT", "COMPANY", "DEVICE", "IP"]

RELATIONSHIP_TYPES = [
    "TRANSFER",
    "SHARED_DEVICE",
    "SHARED_ADDRESS",
    "FAMILY",
    "BUSINESS_PARTNER",
    "SHARED_IP",
    "SHARED_PHONE",
    "BENEFICIARY",
]

DISCOVERY_METHODS = [
    "TRANSACTION",
    "KYC",
    "DEVICE_FINGERPRINT",
    "MANUAL",
    "ADDRESS_MATCH",
    "PHONE_MATCH",
]


class RelationshipGenerator:
    """Generator for synthetic relationship/graph data."""

    def __init__(self, seed: int = 42):
        """Initialize the generator."""
        self.seed = seed
        random.seed(seed)
        Faker.seed(seed)
        self.fake = Faker(["es_ES"])

    def generate_relationship(
        self,
        source_id: str,
        source_type: str,
        source_name: str,
        target_id: str,
        target_type: str,
        target_name: str,
        relationship_index: int,
    ) -> dict[str, Any]:
        """Generate a single relationship record."""
        relationship_id = str(uuid.uuid4())

        # Relationship type based on entity types
        if source_type == "CUSTOMER" and target_type == "CUSTOMER":
            rel_type = random.choice([
                "TRANSFER", "FAMILY", "BUSINESS_PARTNER", "SHARED_ADDRESS"
            ])
        elif source_type == "CUSTOMER" and target_type == "DEVICE":
            rel_type = "SHARED_DEVICE"
        elif source_type == "CUSTOMER" and target_type == "IP":
            rel_type = "SHARED_IP"
        elif source_type == "CUSTOMER" and target_type == "COMPANY":
            rel_type = "BUSINESS_PARTNER"
        else:
            rel_type = random.choice(RELATIONSHIP_TYPES)

        # Direction
        direction = "DIRECTED" if rel_type in ["TRANSFER", "BENEFICIARY"] else "UNDIRECTED"

        # Timestamps
        first_interaction = self.fake.date_time_between(start_date="-2y", end_date="-30d")
        last_interaction = self.fake.date_time_between(start_date=first_interaction, end_date="now")

        # Metrics
        interaction_count = random.randint(1, 100)
        total_amount = random.uniform(100, 500000) if rel_type == "TRANSFER" else 0
        average_amount = total_amount / interaction_count if interaction_count > 0 else 0

        # Strength based on recency and frequency
        days_since_last = (datetime.now() - last_interaction).days
        recency_factor = max(0, 1 - (days_since_last / 365))
        frequency_factor = min(1, interaction_count / 50)
        strength = round((recency_factor * 0.4 + frequency_factor * 0.6), 2)

        # Suspicion flags
        is_suspicious = random.random() < 0.15
        suspicion_reasons = []
        if is_suspicious:
            reasons = [
                "Circular transactions detected",
                "Rapid fund movement",
                "Common device with blocked account",
                "Address matches shell company",
                "Unusual relationship pattern",
            ]
            suspicion_reasons = random.sample(reasons, k=random.randint(1, 2))

        # Cluster assignment
        part_of_cluster = random.random() < 0.3
        cluster_id = f"CLUSTER-{random.randint(1, 50)}" if part_of_cluster else None

        # Discovery
        discovery_method = random.choice(DISCOVERY_METHODS)
        discovered_at = self.fake.date_time_between(start_date=first_interaction, end_date="now")

        return {
            # Identification
            "relationship_id": relationship_id,
            # Source
            "source_entity_type": source_type,
            "source_entity_id": source_id,
            "source_entity_name": source_name,
            # Target
            "target_entity_type": target_type,
            "target_entity_id": target_id,
            "target_entity_name": target_name,
            # Connection
            "relationship_type": rel_type,
            "direction": direction,
            "strength": strength,
            # Metrics
            "first_interaction": first_interaction,
            "last_interaction": last_interaction,
            "interaction_count": interaction_count,
            "total_amount": round(total_amount, 2),
            "average_amount": round(average_amount, 2),
            # Flags
            "is_suspicious": is_suspicious,
            "suspicion_reason": "; ".join(suspicion_reasons) if suspicion_reasons else None,
            "part_of_cluster": part_of_cluster,
            "cluster_id": cluster_id,
            # Metadata
            "discovered_at": discovered_at,
            "last_updated": self.fake.date_time_between(start_date=discovered_at, end_date="now"),
            "discovery_method": discovery_method,
        }

    def generate_relationships(
        self,
        customers_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        count: int | None = None,
    ) -> pd.DataFrame:
        """Generate relationships based on transactions and customer data."""
        relationships = []
        seen_pairs = set()

        # 1. Generate relationships from transactions
        # Group transactions by customer pairs
        outbound_txs = transactions_df[
            (transactions_df["direction"] == "OUTBOUND") &
            (transactions_df["beneficiary_name"].notna())
        ]

        customer_lookup = {
            row["customer_id"]: row
            for _, row in customers_df.iterrows()
        }

        # Transaction-based relationships
        for _, tx in outbound_txs.sample(n=min(500, len(outbound_txs))).iterrows():
            source_id = tx["originator_customer_id"]
            # Create pseudo-target for external beneficiaries
            target_id = f"EXT-{uuid.uuid4().hex[:8]}"

            pair_key = (source_id, target_id)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            source_customer = customer_lookup.get(source_id)
            if source_customer is None:
                continue

            rel = self.generate_relationship(
                source_id=source_id,
                source_type="CUSTOMER",
                source_name=f"{source_customer['first_name']} {source_customer['last_name']}",
                target_id=target_id,
                target_type="CUSTOMER",
                target_name=tx["beneficiary_name"],
                relationship_index=len(relationships),
            )
            rel["relationship_type"] = "TRANSFER"
            relationships.append(rel)

        # 2. Generate shared device relationships
        device_groups = transactions_df.groupby("device_id")["originator_customer_id"].apply(set)
        for device_id, customer_ids in device_groups.items():
            if device_id is None or pd.isna(device_id):
                continue
            customer_ids = list(customer_ids)
            if len(customer_ids) > 1:
                for i, cust1 in enumerate(customer_ids[:5]):
                    for cust2 in customer_ids[i+1:6]:
                        pair_key = tuple(sorted([cust1, cust2]))
                        if pair_key in seen_pairs:
                            continue
                        seen_pairs.add(pair_key)

                        c1 = customer_lookup.get(cust1)
                        c2 = customer_lookup.get(cust2)
                        if c1 is None or c2 is None:
                            continue

                        rel = self.generate_relationship(
                            source_id=cust1,
                            source_type="CUSTOMER",
                            source_name=f"{c1['first_name']} {c1['last_name']}",
                            target_id=cust2,
                            target_type="CUSTOMER",
                            target_name=f"{c2['first_name']} {c2['last_name']}",
                            relationship_index=len(relationships),
                        )
                        rel["relationship_type"] = "SHARED_DEVICE"
                        rel["is_suspicious"] = True
                        rel["suspicion_reason"] = "Multiple customers sharing same device"
                        relationships.append(rel)

        # 3. Generate shared address relationships (simulated)
        # Group by postal code as proxy for address
        address_groups = customers_df.groupby("postal_code")["customer_id"].apply(list)
        for postal_code, customer_ids in address_groups.items():
            if len(customer_ids) > 1 and random.random() < 0.1:
                for i, cust1 in enumerate(customer_ids[:3]):
                    for cust2 in customer_ids[i+1:4]:
                        pair_key = tuple(sorted([cust1, cust2]))
                        if pair_key in seen_pairs:
                            continue
                        seen_pairs.add(pair_key)

                        c1 = customer_lookup.get(cust1)
                        c2 = customer_lookup.get(cust2)
                        if c1 is None or c2 is None:
                            continue

                        rel = self.generate_relationship(
                            source_id=cust1,
                            source_type="CUSTOMER",
                            source_name=f"{c1['first_name']} {c1['last_name']}",
                            target_id=cust2,
                            target_type="CUSTOMER",
                            target_name=f"{c2['first_name']} {c2['last_name']}",
                            relationship_index=len(relationships),
                        )
                        rel["relationship_type"] = "SHARED_ADDRESS"
                        relationships.append(rel)

        # 4. Generate family relationships (based on shared last name in same area)
        name_location_groups = customers_df.groupby(["last_name", "city"])["customer_id"].apply(list)
        for (last_name, city), customer_ids in name_location_groups.items():
            if len(customer_ids) > 1 and random.random() < 0.3:
                cust1 = customer_ids[0]
                cust2 = customer_ids[1]

                pair_key = tuple(sorted([cust1, cust2]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                c1 = customer_lookup.get(cust1)
                c2 = customer_lookup.get(cust2)
                if c1 is None or c2 is None:
                    continue

                rel = self.generate_relationship(
                    source_id=cust1,
                    source_type="CUSTOMER",
                    source_name=f"{c1['first_name']} {c1['last_name']}",
                    target_id=cust2,
                    target_type="CUSTOMER",
                    target_name=f"{c2['first_name']} {c2['last_name']}",
                    relationship_index=len(relationships),
                )
                rel["relationship_type"] = "FAMILY"
                relationships.append(rel)

        # 5. Create some suspicious clusters
        num_clusters = 5
        for cluster_num in range(num_clusters):
            cluster_size = random.randint(3, 8)
            cluster_customers = customers_df.sample(n=min(cluster_size, len(customers_df)))
            cluster_id = f"CLUSTER-SUSP-{cluster_num + 1}"

            customer_ids = list(cluster_customers["customer_id"].values)
            for i, cust1 in enumerate(customer_ids):
                for cust2 in customer_ids[i+1:]:
                    pair_key = tuple(sorted([cust1, cust2]))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    c1 = customer_lookup.get(cust1)
                    c2 = customer_lookup.get(cust2)
                    if c1 is None or c2 is None:
                        continue

                    rel = self.generate_relationship(
                        source_id=cust1,
                        source_type="CUSTOMER",
                        source_name=f"{c1['first_name']} {c1['last_name']}",
                        target_id=cust2,
                        target_type="CUSTOMER",
                        target_name=f"{c2['first_name']} {c2['last_name']}",
                        relationship_index=len(relationships),
                    )
                    rel["relationship_type"] = random.choice(["TRANSFER", "BUSINESS_PARTNER"])
                    rel["is_suspicious"] = True
                    rel["part_of_cluster"] = True
                    rel["cluster_id"] = cluster_id
                    rel["suspicion_reason"] = "Part of suspicious network cluster"
                    relationships.append(rel)

        # Limit if count specified
        if count and len(relationships) > count:
            relationships = random.sample(relationships, count)

        return pd.DataFrame(relationships)
