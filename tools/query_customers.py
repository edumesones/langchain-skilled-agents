"""Customer data query tools."""

import json
from pathlib import Path

import pandas as pd
from langchain_core.tools import tool

from config.settings import get_settings

settings = get_settings()
DATA_DIR = Path(settings.data_dir)


def _load_customers() -> pd.DataFrame:
    """Load customers from parquet file."""
    path = DATA_DIR / "synthetic" / "customers.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@tool
def get_customer_by_id(customer_id: str) -> str:
    """
    Obtener información completa de un cliente por su ID.

    Args:
        customer_id: ID único del cliente (ej: "CUST-000001")

    Returns:
        Información completa del cliente en formato JSON
    """
    df = _load_customers()
    if df.empty:
        return json.dumps({"error": "No hay datos de clientes disponibles"})

    customer = df[df["customer_id"] == customer_id]
    if customer.empty:
        return json.dumps({"error": f"Cliente {customer_id} no encontrado"})

    record = customer.iloc[0].to_dict()
    # Convert timestamps to strings
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None
        elif hasattr(value, "isoformat"):
            record[key] = value.isoformat()

    return json.dumps(record, ensure_ascii=False, indent=2)


@tool
def search_customers(
    risk_level: str | None = None,
    customer_type: str | None = None,
    country: str | None = None,
    pep: bool | None = None,
    limit: int = 10,
) -> str:
    """
    Buscar clientes por criterios.

    Args:
        risk_level: Nivel de riesgo (LOW, MEDIUM, HIGH, CRITICAL)
        customer_type: Tipo de cliente (individual, business)
        country: País de residencia (código ISO: ES, PT, FR, etc.)
        pep: Persona Políticamente Expuesta (true/false)
        limit: Número máximo de resultados (default: 10)

    Returns:
        Lista de clientes que cumplen los criterios
    """
    df = _load_customers()
    if df.empty:
        return json.dumps({"error": "No hay datos de clientes disponibles"})

    # Apply filters
    if risk_level:
        df = df[df["risk_level"] == risk_level.upper()]
    if customer_type:
        df = df[df["customer_type"] == customer_type.lower()]
    if country:
        df = df[df["country"] == country.upper()]
    if pep is not None:
        df = df[df["pep"] == pep]

    # Limit results
    df = df.head(limit)

    if df.empty:
        return json.dumps({"results": [], "count": 0})

    # Select key columns
    columns = [
        "customer_id",
        "full_name",
        "customer_type",
        "risk_level",
        "country",
        "pep",
        "onboarding_date",
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
def get_customer_risk_profile(customer_id: str) -> str:
    """
    Obtener el perfil de riesgo detallado de un cliente.

    Args:
        customer_id: ID único del cliente

    Returns:
        Perfil de riesgo incluyendo factores, scores y flags
    """
    df = _load_customers()
    if df.empty:
        return json.dumps({"error": "No hay datos de clientes disponibles"})

    customer = df[df["customer_id"] == customer_id]
    if customer.empty:
        return json.dumps({"error": f"Cliente {customer_id} no encontrado"})

    c = customer.iloc[0]

    # Build risk profile
    risk_profile = {
        "customer_id": c["customer_id"],
        "full_name": c.get("full_name", "N/A"),
        "risk_assessment": {
            "overall_level": c.get("risk_level", "UNKNOWN"),
            "score": c.get("risk_score", 0),
            "last_review": (
                c["last_risk_review"].isoformat()
                if pd.notna(c.get("last_risk_review"))
                else None
            ),
        },
        "risk_factors": {
            "pep": c.get("pep", False),
            "country_risk": c.get("country", "ES"),
            "customer_type": c.get("customer_type", "individual"),
            "occupation_risk": c.get("occupation", "empleado"),
            "source_of_funds": c.get("source_of_funds", "salary"),
        },
        "limits": {
            "monthly_limit": c.get("monthly_limit", 0),
            "transaction_limit": c.get("transaction_limit", 0),
        },
        "kyc_status": {
            "status": c.get("kyc_status", "UNKNOWN"),
            "last_update": (
                c["kyc_last_update"].isoformat()
                if pd.notna(c.get("kyc_last_update"))
                else None
            ),
            "documents_verified": c.get("documents_verified", False),
        },
        "account_age_days": (
            (pd.Timestamp.now() - c["onboarding_date"]).days
            if pd.notna(c.get("onboarding_date"))
            else None
        ),
    }

    return json.dumps(risk_profile, ensure_ascii=False, indent=2)
