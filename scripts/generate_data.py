#!/usr/bin/env python3
"""
Script to generate synthetic data for the Fintech AML system.

Usage:
    python scripts/generate_data.py [--customers N] [--transactions N] [--alerts N]

This script generates:
- Customers (1000 by default)
- Transactions (100000 by default)
- Alerts (200 by default)
- Relationships (derived from customers)
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from config.settings import get_settings
from data.synthetic.generators import (
    CustomerGenerator,
    TransactionGenerator,
    AlertGenerator,
    RelationshipGenerator,
)

console = Console()
logger = logging.getLogger(__name__)


def generate_all_data(
    n_customers: int = 1000,
    n_transactions: int = 100000,
    n_alerts: int = 200,
    seed: int | None = None,
) -> dict[str, int]:
    """
    Generate all synthetic data.

    Args:
        n_customers: Number of customers to generate
        n_transactions: Number of transactions to generate
        n_alerts: Number of alerts to generate
        seed: Random seed for reproducibility

    Returns:
        Dictionary with counts of generated records
    """
    settings = get_settings()
    output_dir = Path(settings.data_dir) / "synthetic"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        # Generate customers
        task1 = progress.add_task("[cyan]Generando clientes...", total=1)
        customer_gen = CustomerGenerator(seed=seed)
        customers_df = customer_gen.generate_customers(n_customers)
        customers_path = output_dir / "customers.parquet"
        customers_df.to_parquet(customers_path, index=False)
        results["customers"] = len(customers_df)
        progress.update(task1, completed=1)
        console.print(f"  [green]✓[/green] {len(customers_df):,} clientes guardados en {customers_path}")

        # Extract customer IDs for other generators (use external_id as it's more readable)
        customer_ids = customers_df["external_id"].tolist()

        # Generate transactions
        task2 = progress.add_task("[cyan]Generando transacciones...", total=1)
        txn_gen = TransactionGenerator(seed=seed)
        transactions_df = txn_gen.generate_transactions(n_transactions, customer_ids)
        transactions_path = output_dir / "transactions.parquet"
        transactions_df.to_parquet(transactions_path, index=False)
        results["transactions"] = len(transactions_df)
        progress.update(task2, completed=1)
        console.print(f"  [green]✓[/green] {len(transactions_df):,} transacciones guardadas en {transactions_path}")

        # Generate alerts
        task3 = progress.add_task("[cyan]Generando alertas...", total=1)
        alert_gen = AlertGenerator(seed=seed)
        alerts_df = alert_gen.generate_alerts(n_alerts, customer_ids, transactions_df)
        alerts_path = output_dir / "alerts.parquet"
        alerts_df.to_parquet(alerts_path, index=False)
        results["alerts"] = len(alerts_df)
        progress.update(task3, completed=1)
        console.print(f"  [green]✓[/green] {len(alerts_df):,} alertas guardadas en {alerts_path}")

        # Generate relationships
        task4 = progress.add_task("[cyan]Generando relaciones...", total=1)
        rel_gen = RelationshipGenerator(seed=seed)
        relationships_df = rel_gen.generate_relationships(customers_df)
        relationships_path = output_dir / "relationships.parquet"
        relationships_df.to_parquet(relationships_path, index=False)
        results["relationships"] = len(relationships_df)
        progress.update(task4, completed=1)
        console.print(f"  [green]✓[/green] {len(relationships_df):,} relaciones guardadas en {relationships_path}")

    return results


def print_summary(results: dict[str, int]) -> None:
    """Print a summary table of generated data."""
    table = Table(title="Datos Sintéticos Generados", title_style="bold cyan")

    table.add_column("Tipo", style="cyan")
    table.add_column("Cantidad", justify="right", style="green")
    table.add_column("Archivo", style="dim")

    settings = get_settings()
    output_dir = Path(settings.data_dir) / "synthetic"

    for data_type, count in results.items():
        file_path = output_dir / f"{data_type}.parquet"
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        table.add_row(
            data_type.title(),
            f"{count:,}",
            f"{file_path.name} ({file_size:.1f} MB)",
        )

    console.print()
    console.print(table)


def print_data_preview(data_type: str, limit: int = 5) -> None:
    """Print a preview of generated data."""
    import pandas as pd

    settings = get_settings()
    file_path = Path(settings.data_dir) / "synthetic" / f"{data_type}.parquet"

    if not file_path.exists():
        console.print(f"[red]Archivo no encontrado: {file_path}[/red]")
        return

    df = pd.read_parquet(file_path)

    console.print(f"\n[bold cyan]Preview de {data_type.title()}[/bold cyan] (primeros {limit} registros):")

    # Select a subset of columns for display
    if data_type == "customers":
        cols = ["external_id", "first_name", "last_name", "risk_category", "nationality", "is_pep"]
    elif data_type == "transactions":
        cols = ["transaction_id", "customer_id", "timestamp", "transaction_type", "amount", "currency"]
    elif data_type == "alerts":
        cols = ["alert_id", "customer_id", "alert_type", "severity", "status", "risk_score"]
    elif data_type == "relationships":
        cols = ["source_id", "target_id", "relationship_type", "strength"]
    else:
        cols = df.columns[:6].tolist()

    available_cols = [c for c in cols if c in df.columns]
    preview_df = df[available_cols].head(limit)

    # Convert to Rich table
    table = Table(show_header=True, header_style="bold")
    for col in available_cols:
        table.add_column(col)

    for _, row in preview_df.iterrows():
        table.add_row(*[str(v)[:30] for v in row.values])

    console.print(table)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Genera datos sintéticos para el sistema Fintech AML",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--customers", "-c",
        type=int,
        default=1000,
        help="Número de clientes a generar",
    )
    parser.add_argument(
        "--transactions", "-t",
        type=int,
        default=100000,
        help="Número de transacciones a generar",
    )
    parser.add_argument(
        "--alerts", "-a",
        type=int,
        default=200,
        help="Número de alertas a generar",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Seed para reproducibilidad",
    )
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Mostrar preview de los datos generados",
    )

    args = parser.parse_args()

    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]     Fintech AML - Generador de Datos Sintéticos[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print()

    console.print(f"[dim]Configuración:[/dim]")
    console.print(f"  • Clientes: {args.customers:,}")
    console.print(f"  • Transacciones: {args.transactions:,}")
    console.print(f"  • Alertas: {args.alerts:,}")
    console.print(f"  • Seed: {args.seed or 'aleatorio'}")
    console.print()

    try:
        results = generate_all_data(
            n_customers=args.customers,
            n_transactions=args.transactions,
            n_alerts=args.alerts,
            seed=args.seed,
        )

        print_summary(results)

        if args.preview:
            for data_type in ["customers", "transactions", "alerts", "relationships"]:
                print_data_preview(data_type)

        console.print("\n[bold green]¡Datos generados exitosamente![/bold green]")
        return 0

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        logger.exception("Error generating data")
        return 1


if __name__ == "__main__":
    sys.exit(main())
