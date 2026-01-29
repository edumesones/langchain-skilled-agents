#!/usr/bin/env python3
"""
Fintech AML Multi-Agent System

Main entry point for the application.

Usage:
    python main.py                 # Launch the UI
    python main.py --generate      # Generate synthetic data first
    python main.py --cli           # Run in CLI mode (no UI)
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from rich.console import Console

from config.logging_config import setup_logging, get_logger
from config.settings import get_settings

console = Console()
logger = get_logger(__name__)


def check_data_exists() -> bool:
    """Check if synthetic data has been generated."""
    settings = get_settings()
    data_dir = Path(settings.data_dir) / "synthetic"

    required_files = [
        "customers.parquet",
        "transactions.parquet",
        "alerts.parquet",
        "relationships.parquet",
    ]

    return all((data_dir / f).exists() for f in required_files)


def generate_data():
    """Generate synthetic data."""
    console.print("[cyan]Generando datos sintéticos...[/cyan]")

    from scripts.generate_data import generate_all_data, print_summary

    results = generate_all_data()
    print_summary(results)


async def run_cli_mode():
    """Run the system in CLI mode (interactive)."""
    from graph.workflow import run_workflow
    import uuid

    session_id = str(uuid.uuid4())
    console.print("[bold cyan]Fintech AML - Modo CLI[/bold cyan]")
    console.print(f"Sesión: {session_id[:8]}...")
    console.print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            user_input = console.input("[bold green]>>> [/bold green]")

            if user_input.lower() in ("salir", "exit", "quit"):
                console.print("[dim]¡Hasta luego![/dim]")
                break

            if not user_input.strip():
                continue

            console.print("[dim]Procesando...[/dim]")

            result = await run_workflow(
                user_input=user_input,
                session_id=session_id,
            )

            response = result.get("final_response", "Sin respuesta")
            console.print(f"\n[cyan]{response}[/cyan]\n")

        except KeyboardInterrupt:
            console.print("\n[dim]¡Hasta luego![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            logger.exception("Error in CLI mode")


def launch_ui(host: str, port: int, share: bool, debug: bool):
    """Launch the Gradio UI."""
    from ui.app import launch_app

    launch_app(
        server_name=host,
        server_port=port,
        share=share,
        debug=debug,
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fintech AML Multi-Agent System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--generate", "-g",
        action="store_true",
        help="Generar datos sintéticos antes de iniciar",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Ejecutar en modo CLI (sin interfaz gráfica)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host para el servidor UI",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Puerto para el servidor UI",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Crear URL pública (Gradio share)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activar modo debug",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    console.print()
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]        Fintech AML - Sistema Multi-Agente[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print()

    # Check/generate data
    if args.generate or not check_data_exists():
        if not check_data_exists():
            console.print("[yellow]No se encontraron datos sintéticos. Generando...[/yellow]")
        generate_data()
        console.print()

    # Run in appropriate mode
    if args.cli:
        console.print("[dim]Iniciando modo CLI...[/dim]\n")
        asyncio.run(run_cli_mode())
    else:
        console.print(f"[dim]Iniciando UI en http://{args.host}:{args.port}[/dim]\n")
        launch_ui(args.host, args.port, args.share, args.debug)


if __name__ == "__main__":
    main()
