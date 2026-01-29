"""Transaction data query tools."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from langchain_core.tools import tool

from config.settings import get_settings

settings = get_settings()
DATA_DIR = Path(settings.data_dir)


def _load_transactions() -> pd.DataFrame:
    """Load transactions from parquet file."""
    path = DATA_DIR / "synthetic" / "transactions.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@tool
def get_transaction_by_id(transaction_id: str) -> str:
    """
    Obtener detalles completos de una transacción por su ID.

    Args:
        transaction_id: ID único de la transacción (ej: "TXN-00000001")

    Returns:
        Detalles completos de la transacción
    """
    df = _load_transactions()
    if df.empty:
        return json.dumps({"error": "No hay datos de transacciones disponibles"})

    txn = df[df["transaction_id"] == transaction_id]
    if txn.empty:
        return json.dumps({"error": f"Transacción {transaction_id} no encontrada"})

    record = txn.iloc[0].to_dict()
    # Convert timestamps and handle NaN
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None
        elif hasattr(value, "isoformat"):
            record[key] = value.isoformat()

    return json.dumps(record, ensure_ascii=False, indent=2)


@tool
def get_customer_transactions(
    customer_id: str,
    days: int = 30,
    transaction_type: str | None = None,
    min_amount: float | None = None,
    limit: int = 50,
) -> str:
    """
    Obtener transacciones de un cliente.

    Args:
        customer_id: ID del cliente
        days: Número de días hacia atrás (default: 30)
        transaction_type: Filtrar por tipo (transfer, payment, withdrawal, deposit, etc.)
        min_amount: Monto mínimo de transacción
        limit: Número máximo de resultados (default: 50)

    Returns:
        Lista de transacciones del cliente
    """
    df = _load_transactions()
    if df.empty:
        return json.dumps({"error": "No hay datos de transacciones disponibles"})

    # Filter by customer
    df = df[df["customer_id"] == customer_id]

    if df.empty:
        return json.dumps({
            "customer_id": customer_id,
            "transactions": [],
            "count": 0,
            "message": "No se encontraron transacciones para este cliente",
        })

    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    if "timestamp" in df.columns:
        df = df[df["timestamp"] >= cutoff_date]

    # Filter by type
    if transaction_type:
        df = df[df["transaction_type"] == transaction_type.lower()]

    # Filter by amount
    if min_amount is not None:
        df = df[df["amount"] >= min_amount]

    # Sort by date descending and limit
    df = df.sort_values("timestamp", ascending=False).head(limit)

    # Select columns
    columns = [
        "transaction_id",
        "timestamp",
        "transaction_type",
        "amount",
        "currency",
        "counterparty_name",
        "counterparty_country",
        "channel",
        "status",
        "risk_flag",
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
            "period_days": days,
            "transactions": results,
            "count": len(results),
        },
        ensure_ascii=False,
        indent=2,
    )


@tool
def search_transactions(
    start_date: str | None = None,
    end_date: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    transaction_type: str | None = None,
    counterparty_country: str | None = None,
    risk_flag: bool | None = None,
    limit: int = 50,
) -> str:
    """
    Buscar transacciones por criterios múltiples.

    Args:
        start_date: Fecha inicio (formato: YYYY-MM-DD)
        end_date: Fecha fin (formato: YYYY-MM-DD)
        min_amount: Monto mínimo
        max_amount: Monto máximo
        transaction_type: Tipo de transacción
        counterparty_country: País de la contraparte (código ISO)
        risk_flag: Solo transacciones marcadas como riesgo
        limit: Número máximo de resultados (default: 50)

    Returns:
        Lista de transacciones que cumplen los criterios
    """
    df = _load_transactions()
    if df.empty:
        return json.dumps({"error": "No hay datos de transacciones disponibles"})

    # Apply filters
    if start_date:
        df = df[df["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["timestamp"] <= pd.to_datetime(end_date)]
    if min_amount is not None:
        df = df[df["amount"] >= min_amount]
    if max_amount is not None:
        df = df[df["amount"] <= max_amount]
    if transaction_type:
        df = df[df["transaction_type"] == transaction_type.lower()]
    if counterparty_country:
        df = df[df["counterparty_country"] == counterparty_country.upper()]
    if risk_flag is not None:
        df = df[df["risk_flag"] == risk_flag]

    # Sort and limit
    df = df.sort_values("timestamp", ascending=False).head(limit)

    # Select columns
    columns = [
        "transaction_id",
        "customer_id",
        "timestamp",
        "transaction_type",
        "amount",
        "currency",
        "counterparty_name",
        "counterparty_country",
        "risk_flag",
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
def get_transaction_stats(
    customer_id: str,
    days: int = 30,
) -> str:
    """
    Obtener estadísticas de transacciones de un cliente.

    Args:
        customer_id: ID del cliente
        days: Período de análisis en días (default: 30)

    Returns:
        Estadísticas agregadas: totales, promedios, patrones
    """
    df = _load_transactions()
    if df.empty:
        return json.dumps({"error": "No hay datos de transacciones disponibles"})

    # Filter by customer
    df = df[df["customer_id"] == customer_id]

    if df.empty:
        return json.dumps({
            "customer_id": customer_id,
            "error": "No se encontraron transacciones para este cliente",
        })

    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    if "timestamp" in df.columns:
        df = df[df["timestamp"] >= cutoff_date]

    if df.empty:
        return json.dumps({
            "customer_id": customer_id,
            "period_days": days,
            "message": "No hay transacciones en el período especificado",
        })

    # Calculate stats
    stats = {
        "customer_id": customer_id,
        "period_days": days,
        "summary": {
            "total_transactions": len(df),
            "total_amount": float(df["amount"].sum()),
            "average_amount": float(df["amount"].mean()),
            "max_amount": float(df["amount"].max()),
            "min_amount": float(df["amount"].min()),
            "std_amount": float(df["amount"].std()) if len(df) > 1 else 0,
        },
        "by_type": (
            df.groupby("transaction_type")
            .agg({"amount": ["count", "sum", "mean"]})
            .round(2)
            .to_dict()
            if "transaction_type" in df.columns
            else {}
        ),
        "by_channel": (
            df["channel"].value_counts().to_dict()
            if "channel" in df.columns
            else {}
        ),
        "risk_flags": {
            "flagged_transactions": int(df["risk_flag"].sum()) if "risk_flag" in df.columns else 0,
            "flagged_percentage": (
                float(df["risk_flag"].mean() * 100)
                if "risk_flag" in df.columns
                else 0
            ),
        },
        "temporal_patterns": {
            "transactions_per_day": len(df) / days if days > 0 else 0,
            "amount_per_day": float(df["amount"].sum()) / days if days > 0 else 0,
        },
    }

    # Simplify by_type structure
    if stats["by_type"]:
        simplified_by_type = {}
        for txn_type in df["transaction_type"].unique():
            type_df = df[df["transaction_type"] == txn_type]
            simplified_by_type[txn_type] = {
                "count": len(type_df),
                "total": float(type_df["amount"].sum()),
                "average": float(type_df["amount"].mean()),
            }
        stats["by_type"] = simplified_by_type

    return json.dumps(stats, ensure_ascii=False, indent=2)
