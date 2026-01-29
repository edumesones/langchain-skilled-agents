"""Alert data query tools."""

import json
from pathlib import Path

import pandas as pd
from langchain_core.tools import tool

from config.settings import get_settings

settings = get_settings()
DATA_DIR = Path(settings.data_dir)


def _load_alerts() -> pd.DataFrame:
    """Load alerts from parquet file."""
    path = DATA_DIR / "synthetic" / "alerts.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@tool
def get_alert_by_id(alert_id: str) -> str:
    """
    Obtener detalles completos de una alerta por su ID.

    Args:
        alert_id: ID único de la alerta (ej: "ALT-000001")

    Returns:
        Detalles completos de la alerta incluyendo transacciones relacionadas
    """
    df = _load_alerts()
    if df.empty:
        return json.dumps({"error": "No hay datos de alertas disponibles"})

    alert = df[df["alert_id"] == alert_id]
    if alert.empty:
        return json.dumps({"error": f"Alerta {alert_id} no encontrada"})

    record = alert.iloc[0].to_dict()
    # Convert timestamps and handle complex types
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None
        elif hasattr(value, "isoformat"):
            record[key] = value.isoformat()
        elif isinstance(value, (list, dict)):
            pass  # Keep as is
        elif hasattr(value, "tolist"):
            record[key] = value.tolist()

    return json.dumps(record, ensure_ascii=False, indent=2)


@tool
def get_customer_alerts(
    customer_id: str,
    status: str | None = None,
    include_closed: bool = False,
    limit: int = 20,
) -> str:
    """
    Obtener alertas de un cliente específico.

    Args:
        customer_id: ID del cliente
        status: Filtrar por estado (OPEN, IN_REVIEW, ESCALATED, CLOSED_FP, CLOSED_SAR)
        include_closed: Incluir alertas cerradas (default: False)
        limit: Número máximo de resultados (default: 20)

    Returns:
        Lista de alertas del cliente
    """
    df = _load_alerts()
    if df.empty:
        return json.dumps({"error": "No hay datos de alertas disponibles"})

    # Filter by customer
    df = df[df["customer_id"] == customer_id]

    if df.empty:
        return json.dumps({
            "customer_id": customer_id,
            "alerts": [],
            "count": 0,
            "message": "No se encontraron alertas para este cliente",
        })

    # Filter by status
    if status:
        df = df[df["status"] == status.upper()]
    elif not include_closed:
        df = df[~df["status"].str.startswith("CLOSED")]

    # Sort by creation date and limit
    if "created_at" in df.columns:
        df = df.sort_values("created_at", ascending=False)
    df = df.head(limit)

    # Select columns
    columns = [
        "alert_id",
        "alert_type",
        "severity",
        "status",
        "created_at",
        "sla_deadline",
        "risk_score",
        "description",
        "assigned_to",
    ]
    available_columns = [c for c in columns if c in df.columns]
    results = df[available_columns].to_dict(orient="records")

    # Convert timestamps
    for record in results:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif hasattr(value, "isoformat"):
                record[key] = value.isoformat()

    return json.dumps(
        {
            "customer_id": customer_id,
            "alerts": results,
            "count": len(results),
        },
        ensure_ascii=False,
        indent=2,
    )


@tool
def search_alerts(
    alert_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    assigned_to: str | None = None,
    min_risk_score: float | None = None,
    sla_breached: bool | None = None,
    limit: int = 50,
) -> str:
    """
    Buscar alertas por múltiples criterios.

    Args:
        alert_type: Tipo de alerta (STRUCTURING, HIGH_RISK_COUNTRY, VELOCITY, UNUSUAL_PATTERN, etc.)
        severity: Severidad (CRITICAL, HIGH, MEDIUM, LOW)
        status: Estado (OPEN, IN_REVIEW, ESCALATED, CLOSED_FP, CLOSED_SAR)
        assigned_to: Analista asignado
        min_risk_score: Puntuación mínima de riesgo (0-100)
        sla_breached: Solo alertas con SLA vencido
        limit: Número máximo de resultados (default: 50)

    Returns:
        Lista de alertas que cumplen los criterios
    """
    df = _load_alerts()
    if df.empty:
        return json.dumps({"error": "No hay datos de alertas disponibles"})

    # Apply filters
    if alert_type:
        df = df[df["alert_type"] == alert_type.upper()]
    if severity:
        df = df[df["severity"] == severity.upper()]
    if status:
        df = df[df["status"] == status.upper()]
    if assigned_to:
        df = df[df["assigned_to"] == assigned_to]
    if min_risk_score is not None:
        df = df[df["risk_score"] >= min_risk_score]
    if sla_breached is not None and "sla_deadline" in df.columns:
        now = pd.Timestamp.now()
        if sla_breached:
            df = df[(df["sla_deadline"] < now) & (~df["status"].str.startswith("CLOSED"))]
        else:
            df = df[(df["sla_deadline"] >= now) | (df["status"].str.startswith("CLOSED"))]

    # Sort by severity and creation date
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    if "severity" in df.columns:
        df["severity_order"] = df["severity"].map(severity_order).fillna(4)
        df = df.sort_values(["severity_order", "created_at"], ascending=[True, False])
        df = df.drop(columns=["severity_order"])

    df = df.head(limit)

    # Select columns
    columns = [
        "alert_id",
        "customer_id",
        "alert_type",
        "severity",
        "status",
        "created_at",
        "sla_deadline",
        "risk_score",
        "assigned_to",
    ]
    available_columns = [c for c in columns if c in df.columns]
    results = df[available_columns].to_dict(orient="records")

    # Convert timestamps
    for record in results:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif hasattr(value, "isoformat"):
                record[key] = value.isoformat()

    return json.dumps(
        {"results": results, "count": len(results)},
        ensure_ascii=False,
        indent=2,
    )


@tool
def get_alerts_summary() -> str:
    """
    Obtener resumen del estado actual de todas las alertas.

    Returns:
        Estadísticas agregadas de alertas por tipo, severidad y estado
    """
    df = _load_alerts()
    if df.empty:
        return json.dumps({"error": "No hay datos de alertas disponibles"})

    now = pd.Timestamp.now()

    # Calculate SLA status
    open_alerts = df[~df["status"].str.startswith("CLOSED")]
    sla_breached = (
        open_alerts[open_alerts["sla_deadline"] < now]
        if "sla_deadline" in df.columns
        else pd.DataFrame()
    )

    summary = {
        "total_alerts": len(df),
        "by_status": df["status"].value_counts().to_dict() if "status" in df.columns else {},
        "by_severity": df["severity"].value_counts().to_dict() if "severity" in df.columns else {},
        "by_type": df["alert_type"].value_counts().to_dict() if "alert_type" in df.columns else {},
        "open_alerts": {
            "count": len(open_alerts),
            "sla_breached": len(sla_breached),
            "sla_breached_percentage": (
                round(len(sla_breached) / len(open_alerts) * 100, 1)
                if len(open_alerts) > 0
                else 0
            ),
        },
        "risk_score_stats": {
            "average": round(df["risk_score"].mean(), 1) if "risk_score" in df.columns else 0,
            "max": round(df["risk_score"].max(), 1) if "risk_score" in df.columns else 0,
            "min": round(df["risk_score"].min(), 1) if "risk_score" in df.columns else 0,
        },
        "by_assigned_analyst": (
            df["assigned_to"].value_counts().to_dict()
            if "assigned_to" in df.columns
            else {}
        ),
        "resolution_stats": {
            "closed_as_fp": len(df[df["status"] == "CLOSED_FP"]) if "status" in df.columns else 0,
            "closed_as_sar": len(df[df["status"] == "CLOSED_SAR"]) if "status" in df.columns else 0,
            "fp_rate": (
                round(
                    len(df[df["status"] == "CLOSED_FP"])
                    / len(df[df["status"].str.startswith("CLOSED")])
                    * 100,
                    1,
                )
                if len(df[df["status"].str.startswith("CLOSED")]) > 0
                else 0
            ),
        },
    }

    return json.dumps(summary, ensure_ascii=False, indent=2)
