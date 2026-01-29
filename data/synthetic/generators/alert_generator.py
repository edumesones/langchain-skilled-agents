"""Alert data generator for synthetic fintech data."""

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

ALERT_TYPES = [
    "STRUCTURING",
    "VELOCITY",
    "SANCTIONS",
    "PEP",
    "UNUSUAL_ACTIVITY",
    "GEOGRAPHIC",
]

ALERT_SUBTYPES = {
    "STRUCTURING": ["CASH_STRUCTURING", "TRANSFER_STRUCTURING", "DEPOSIT_STRUCTURING"],
    "VELOCITY": ["HIGH_FREQUENCY", "BURST_ACTIVITY", "DORMANT_REACTIVATION"],
    "SANCTIONS": ["POTENTIAL_MATCH", "COUNTRY_SANCTIONS", "SECTOR_SANCTIONS"],
    "PEP": ["NEW_PEP_CUSTOMER", "PEP_HIGH_VALUE", "PEP_INTERNATIONAL"],
    "UNUSUAL_ACTIVITY": ["BEHAVIOR_CHANGE", "INCOME_MISMATCH", "PURPOSE_MISMATCH"],
    "GEOGRAPHIC": ["HIGH_RISK_COUNTRY", "UNUSUAL_LOCATION", "RAPID_GEO_CHANGE"],
}

TYPOLOGIES = [
    "LAYERING",
    "SMURFING",
    "ROUND_TRIPPING",
    "SHELL_COMPANY",
    "TRADE_BASED",
    "CASH_INTENSIVE",
]

ALERT_SOURCES = ["TM_ENGINE", "SANCTIONS_SCREENING", "MANUAL", "ML_MODEL"]

WORKFLOW_STATUSES = ["NEW", "IN_REVIEW", "ESCALATED", "PENDING_INFO", "CLOSED"]

QUEUES = ["L1_REVIEW", "L2_INVESTIGATION", "COMPLIANCE_OFFICER"]

OUTCOMES = ["SAR_FILED", "ESCALATED", "CLOSED_FP", "CLOSED_NO_ACTION", "CLOSED_LEGITIMATE"]

PRIORITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# SLA hours by priority
SLA_HOURS = {
    "CRITICAL": 4,
    "HIGH": 24,
    "MEDIUM": 72,
    "LOW": 168,
}


class AlertGenerator:
    """Generator for synthetic alert data."""

    def __init__(self, seed: int = 42):
        """Initialize the generator."""
        self.seed = seed
        random.seed(seed)
        Faker.seed(seed)
        self.fake = Faker(["es_ES"])

    def generate_alert(
        self,
        customer_id: str,
        customer_name: str,
        customer_risk_category: str,
        account_id: str,
        transactions_df: pd.DataFrame,
        alert_index: int,
    ) -> dict[str, Any]:
        """Generate a single alert record."""
        alert_id = str(uuid.uuid4())
        case_id = f"CASE-{datetime.now().year}-{alert_index + 1:05d}"

        # Select transactions for this customer
        customer_txs = transactions_df[
            transactions_df["originator_customer_id"] == customer_id
        ]

        if len(customer_txs) == 0:
            # Create dummy transaction references
            primary_tx_id = str(uuid.uuid4())
            related_tx_ids = []
            total_amount = random.uniform(1000, 50000)
            tx_count = 1
            date_range_start = self.fake.date_between(start_date="-90d", end_date="-30d")
            date_range_end = self.fake.date_between(start_date=date_range_start, end_date="today")
        else:
            # Sample transactions
            sample_size = min(random.randint(1, 10), len(customer_txs))
            sampled_txs = customer_txs.sample(n=sample_size)
            primary_tx_id = sampled_txs.iloc[0]["transaction_id"]
            related_tx_ids = list(sampled_txs["transaction_id"].values[1:])
            total_amount = sampled_txs["amount_value"].sum()
            tx_count = len(sampled_txs)
            date_range_start = sampled_txs["executed_at"].min()
            date_range_end = sampled_txs["executed_at"].max()
            if hasattr(date_range_start, 'date'):
                date_range_start = date_range_start.date()
            if hasattr(date_range_end, 'date'):
                date_range_end = date_range_end.date()

        # Alert type based on customer risk
        if customer_risk_category == "HIGH":
            alert_type = random.choices(
                ALERT_TYPES,
                weights=[0.2, 0.15, 0.2, 0.15, 0.15, 0.15],
            )[0]
        else:
            alert_type = random.choices(
                ALERT_TYPES,
                weights=[0.3, 0.25, 0.05, 0.05, 0.25, 0.1],
            )[0]

        alert_subtype = random.choice(ALERT_SUBTYPES[alert_type])
        typology = random.choice(TYPOLOGIES) if random.random() < 0.4 else None

        # Source
        source_system = random.choices(
            ALERT_SOURCES,
            weights=[0.5, 0.2, 0.1, 0.2],
        )[0]

        rule_id = f"RULE-{alert_type[:3]}-{random.randint(100, 999)}"
        rule_name = f"{alert_type.replace('_', ' ').title()} Detection"

        # Severity
        initial_score = self._calculate_alert_severity(
            alert_type=alert_type,
            customer_risk=customer_risk_category,
            total_amount=total_amount,
            tx_count=tx_count,
        )

        priority = self._get_priority(initial_score)
        sla_hours = SLA_HOURS[priority]

        # Timing
        created_at = self.fake.date_time_between(start_date="-30d", end_date="now")
        sla_deadline = created_at + timedelta(hours=sla_hours)
        sla_breached = datetime.now() > sla_deadline and random.random() < 0.1

        # Workflow status
        workflow_status = random.choices(
            WORKFLOW_STATUSES,
            weights=[0.15, 0.25, 0.1, 0.1, 0.4],
        )[0]

        # Queue based on priority
        if priority == "CRITICAL":
            current_queue = random.choice(["L2_INVESTIGATION", "COMPLIANCE_OFFICER"])
        elif priority == "HIGH":
            current_queue = random.choice(["L1_REVIEW", "L2_INVESTIGATION"])
        else:
            current_queue = "L1_REVIEW"

        # Assignment
        assigned_to = f"ANALYST-{random.randint(100, 999)}" if workflow_status != "NEW" else None
        assignment_date = created_at + timedelta(hours=random.randint(1, 24)) if assigned_to else None

        # Status history
        status_history = self._generate_status_history(workflow_status, created_at)

        # Decision (if closed)
        if workflow_status == "CLOSED":
            outcome = random.choices(
                OUTCOMES,
                weights=[0.05, 0.1, 0.50, 0.25, 0.10],
            )[0]
            decision_date = status_history[-1]["changed_at"]
            decided_by = assigned_to
            rationale = self._generate_rationale(outcome)
        else:
            outcome = None
            decision_date = None
            decided_by = None
            rationale = None

        # SAR
        sar_required = outcome == "SAR_FILED"
        sar_id = f"SAR-{datetime.now().year}-{random.randint(10000, 99999)}" if sar_required else None
        sar_filed_date = decision_date.date() if sar_required and decision_date else None

        # Metrics
        if assignment_date:
            time_to_first_review = int((assignment_date - created_at).total_seconds() / 60)
        else:
            time_to_first_review = None

        if decision_date:
            time_to_decision = (decision_date - created_at).total_seconds() / 3600
        else:
            time_to_decision = None

        return {
            # Identification
            "alert_id": alert_id,
            "case_id": case_id,
            # Source
            "source_system": source_system,
            "source_rule_id": rule_id,
            "source_rule_name": rule_name,
            "source_rule_version": "1.0",
            "source_model_id": f"ML-{random.randint(100, 999)}" if source_system == "ML_MODEL" else None,
            "source_model_version": "2.1" if source_system == "ML_MODEL" else None,
            # Subject
            "subject_customer_id": customer_id,
            "subject_customer_name": customer_name,
            "subject_customer_risk_category": customer_risk_category,
            "subject_account_id": account_id,
            # Transactions
            "primary_transaction_id": primary_tx_id,
            "related_transaction_ids": related_tx_ids,
            "transaction_count": tx_count,
            "total_amount": round(total_amount, 2),
            "currency": "EUR",
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
            # Classification
            "alert_type": alert_type,
            "alert_subtype": alert_subtype,
            "typology": typology,
            "scenario_id": f"SCN-{alert_type[:3]}-{random.randint(1, 20):02d}",
            # Severity
            "initial_score": initial_score,
            "current_score": initial_score + random.randint(-10, 10),
            "priority": priority,
            "sla_hours": sla_hours,
            "sla_deadline": sla_deadline,
            "sla_breached": sla_breached,
            # Workflow
            "workflow_status": workflow_status,
            "current_queue": current_queue,
            "assigned_to": assigned_to,
            "assignment_date": assignment_date,
            # Status history
            "status_history": status_history,
            # Decision
            "decision_outcome": outcome,
            "decision_date": decision_date,
            "decided_by": decided_by,
            "decision_rationale": rationale,
            "evidence_summary": self._generate_evidence_summary() if outcome else None,
            # SAR
            "sar_required": sar_required,
            "sar_id": sar_id,
            "sar_filed_date": sar_filed_date,
            "sar_type": "INITIAL" if sar_required else None,
            "sepblac_reference": f"SEPBLAC-{random.randint(100000, 999999)}" if sar_required else None,
            # Evidence
            "evidence_documents": [],
            "notes_count": random.randint(0, 10),
            "screenshots": [],
            "external_sources_checked": ["World-Check", "Dow Jones", "LexisNexis"] if random.random() < 0.3 else [],
            # Metrics
            "time_to_first_review_minutes": time_to_first_review,
            "time_to_decision_hours": time_to_decision,
            "review_count": len(status_history) - 1,
            "escalation_count": sum(1 for s in status_history if s["status"] == "ESCALATED"),
            # Related
            "related_alert_ids": [],
            "related_customer_ids": [],
            "network_cluster_id": f"CLUSTER-{random.randint(1, 50)}" if random.random() < 0.2 else None,
            # Metadata
            "created_at": created_at,
            "updated_at": status_history[-1]["changed_at"] if status_history else created_at,
            "is_training_case": random.random() < 0.1,
            "feedback_provided": workflow_status == "CLOSED" and random.random() < 0.7,
            "feedback_correct": random.random() < 0.85,
        }

    def _calculate_alert_severity(
        self,
        alert_type: str,
        customer_risk: str,
        total_amount: float,
        tx_count: int,
    ) -> int:
        """Calculate alert severity score."""
        score = 30

        # Type-based scoring
        type_scores = {
            "SANCTIONS": 40,
            "PEP": 30,
            "STRUCTURING": 25,
            "GEOGRAPHIC": 20,
            "VELOCITY": 15,
            "UNUSUAL_ACTIVITY": 15,
        }
        score += type_scores.get(alert_type, 15)

        # Customer risk
        if customer_risk == "HIGH":
            score += 20
        elif customer_risk == "MEDIUM":
            score += 10

        # Amount
        if total_amount > 50000:
            score += 20
        elif total_amount > 10000:
            score += 10
        elif total_amount > 5000:
            score += 5

        # Transaction count
        if tx_count > 5:
            score += 10
        elif tx_count > 2:
            score += 5

        # Randomness
        score += random.randint(-10, 10)

        return max(0, min(100, score))

    def _get_priority(self, score: int) -> str:
        """Get priority from severity score."""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_status_history(
        self,
        current_status: str,
        created_at: datetime,
    ) -> list[dict[str, Any]]:
        """Generate status history for alert."""
        history = [
            {
                "status": "NEW",
                "changed_at": created_at,
                "changed_by": "SYSTEM",
                "reason": "Alert generated",
            }
        ]

        current_time = created_at

        if current_status in ["IN_REVIEW", "ESCALATED", "PENDING_INFO", "CLOSED"]:
            current_time += timedelta(hours=random.randint(1, 24))
            history.append({
                "status": "IN_REVIEW",
                "changed_at": current_time,
                "changed_by": f"ANALYST-{random.randint(100, 999)}",
                "reason": "Assigned for review",
            })

        if current_status in ["ESCALATED", "CLOSED"]:
            if random.random() < 0.3:
                current_time += timedelta(hours=random.randint(2, 48))
                history.append({
                    "status": "ESCALATED",
                    "changed_at": current_time,
                    "changed_by": f"ANALYST-{random.randint(100, 999)}",
                    "reason": "Requires L2 investigation",
                })

        if current_status == "PENDING_INFO":
            current_time += timedelta(hours=random.randint(4, 72))
            history.append({
                "status": "PENDING_INFO",
                "changed_at": current_time,
                "changed_by": f"ANALYST-{random.randint(100, 999)}",
                "reason": "Awaiting additional documentation",
            })

        if current_status == "CLOSED":
            current_time += timedelta(hours=random.randint(1, 168))
            history.append({
                "status": "CLOSED",
                "changed_at": current_time,
                "changed_by": f"ANALYST-{random.randint(100, 999)}",
                "reason": "Investigation completed",
            })

        return history

    def _generate_rationale(self, outcome: str) -> str:
        """Generate decision rationale."""
        rationales = {
            "SAR_FILED": "Actividad sospechosa confirmada. Se detectaron patrones consistentes con blanqueo de capitales. Se ha procedido a comunicar al SEPBLAC.",
            "ESCALATED": "Caso requiere revisión por Compliance Officer debido a la complejidad y monto involucrado.",
            "CLOSED_FP": "Tras análisis detallado, se determina que la actividad es consistente con el perfil del cliente y no presenta indicios de actividad sospechosa.",
            "CLOSED_NO_ACTION": "La alerta fue generada por una regla demasiado sensible. El comportamiento observado está dentro de los parámetros normales.",
            "CLOSED_LEGITIMATE": "Actividad verificada como legítima. Cliente proporcionó documentación que justifica las transacciones.",
        }
        return rationales.get(outcome, "Investigación completada.")

    def _generate_evidence_summary(self) -> str:
        """Generate evidence summary."""
        summaries = [
            "Se revisaron {} transacciones en el periodo. Se identificaron {} patrones sospechosos.",
            "Análisis de red reveló conexiones con {} entidades relacionadas.",
            "Verificación de documentación completada. {} discrepancias encontradas.",
            "Screening de sanciones actualizado. {} coincidencias potenciales revisadas.",
        ]
        return random.choice(summaries).format(random.randint(5, 50), random.randint(0, 5))

    def generate_alerts(
        self,
        customers_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        count: int = 200,
    ) -> pd.DataFrame:
        """Generate alerts for given customers and transactions."""
        alerts = []

        # Prefer high-risk customers for alerts
        high_risk_customers = customers_df[
            customers_df["risk_category"].isin(["HIGH", "MEDIUM"])
        ]

        if len(high_risk_customers) < count:
            # Add some low-risk customers
            low_risk_sample = customers_df[
                customers_df["risk_category"] == "LOW"
            ].sample(n=min(count - len(high_risk_customers), len(customers_df)))
            selected_customers = pd.concat([high_risk_customers, low_risk_sample])
        else:
            selected_customers = high_risk_customers.sample(n=count)

        for i, (_, customer) in enumerate(selected_customers.iterrows()):
            if i >= count:
                break

            alert = self.generate_alert(
                customer_id=customer["customer_id"],
                customer_name=f"{customer['first_name']} {customer['last_name']}",
                customer_risk_category=customer["risk_category"],
                account_id=customer["account_id"],
                transactions_df=transactions_df,
                alert_index=i,
            )
            alerts.append(alert)

        df = pd.DataFrame(alerts)

        # Convert list and dict columns to string for parquet
        list_columns = [
            "related_transaction_ids", "status_history", "evidence_documents",
            "screenshots", "external_sources_checked", "related_alert_ids",
            "related_customer_ids"
        ]
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)

        return df
