"""Main Gradio application for the Fintech AML Multi-Agent System."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Generator

import gradio as gr

from config.settings import get_settings
from graph.workflow import run_workflow, get_workflow_visualization
from ui.theme import create_linear_dark_theme, LINEAR_DARK_CSS
from ui.components import (
    create_example_queries,
    format_workflow_status,
    format_context_panel,
    format_skills_panel,
    format_log_entry,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatSession:
    """Manages a chat session with state."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.user_id = "analyst"
        self.messages: list = []
        self.context: dict = {}
        self.loaded_skills: list[str] = []
        self.logs: list[str] = []
        self.current_node: str | None = None
        self.route: str | None = None

    def add_log(self, level: str, agent: str, message: str):
        """Add a log entry."""
        entry = format_log_entry(datetime.now(), level, agent, message)
        self.logs.append(entry)
        # Keep last 50 logs
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]

    def get_logs_html(self) -> str:
        """Get all logs as HTML."""
        if not self.logs:
            return '<div style="color: #71717a; font-size: 0.875rem;">Sin actividad reciente</div>'
        return "".join(reversed(self.logs[-20:]))


# Global session storage (in production, use proper session management)
_sessions: dict[str, ChatSession] = {}


def get_session(session_id: str | None = None) -> ChatSession:
    """Get or create a chat session."""
    if session_id and session_id in _sessions:
        return _sessions[session_id]

    session = ChatSession()
    _sessions[session.session_id] = session
    return session


async def process_message(
    message: str,
    history: list,
    session_state: dict,
) -> tuple[list, dict, str, str, str]:
    """
    Process a user message through the workflow.

    Returns:
        Tuple of (history, session_state, workflow_status, context_panel, logs)
    """
    if not message.strip():
        return history, session_state, "", "", ""

    # Get or create session
    session_id = session_state.get("session_id")
    session = get_session(session_id)

    # Update session state
    session_state["session_id"] = session.session_id

    # Add user message to history
    history = history or []
    history.append((message, None))

    # Log the request
    session.add_log("INFO", "SYSTEM", f"Nueva consulta recibida")

    try:
        # Run the workflow
        session.add_log("INFO", "ORCH", "Analizando solicitud...")

        result = await run_workflow(
            user_input=message,
            session_id=session.session_id,
            user_id=session.user_id,
            messages=None,  # Let workflow manage messages
        )

        # Extract results
        final_response = result.get("final_response", "Sin respuesta")
        session.current_node = result.get("current_node")
        session.route = result.get("route")

        # Update context
        task_context = result.get("task_context") or {}
        if task_context:
            session.context.update(task_context)

        # Log completion
        if result.get("error"):
            session.add_log("ERROR", "SYSTEM", f"Error: {result['error']}")
        else:
            session.add_log("INFO", "SYSTEM", "Consulta procesada exitosamente")

        # Update history with response
        history[-1] = (message, final_response)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        session.add_log("ERROR", "SYSTEM", f"Error: {str(e)}")
        error_msg = f"Error al procesar la solicitud: {str(e)}"
        history[-1] = (message, error_msg)

    # Generate UI components
    workflow_status = format_workflow_status(
        session.current_node,
        session.route,
        None,
    )
    context_panel = format_context_panel(session.context)
    logs_html = session.get_logs_html()

    return history, session_state, workflow_status, context_panel, logs_html


def create_app() -> gr.Blocks:
    """Create the Gradio application."""

    theme = create_linear_dark_theme()

    with gr.Blocks(
        theme=theme,
        css=LINEAR_DARK_CSS,
        title="Fintech AML - Sistema Multi-Agente",
    ) as app:
        # Session state
        session_state = gr.State({"session_id": None})

        # Header
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                    <div style="padding: 1rem 0;">
                        <h1 class="header-title">Fintech AML System</h1>
                        <p class="header-subtitle">
                            Sistema Multi-Agente para Análisis de Riesgo y Compliance
                        </p>
                    </div>
                """)

        # Main layout
        with gr.Row():
            # Left sidebar - Status
            with gr.Column(scale=1, min_width=250):
                workflow_status = gr.HTML(
                    value=format_workflow_status(None, None, None),
                    label="Estado",
                )

                context_panel = gr.HTML(
                    value=format_context_panel(None),
                    label="Contexto",
                )

                skills_panel = gr.HTML(
                    value=format_skills_panel(None),
                    label="Skills",
                )

                # Workflow visualization
                with gr.Accordion("Arquitectura del Workflow", open=False):
                    gr.Code(
                        value=get_workflow_visualization(),
                        language=None,
                        label="Diagrama",
                        interactive=False,
                    )

            # Center - Chat
            with gr.Column(scale=3, min_width=500):
                chatbot = gr.Chatbot(
                    label="Conversación",
                    height=500,
                    show_copy_button=True,
                    bubble_full_width=False,
                    avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=fintech"),
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Escribe tu consulta aquí... (Ej: Analiza el cliente CUST-000042)",
                        label="Mensaje",
                        scale=5,
                        container=False,
                    )
                    submit_btn = gr.Button(
                        "Enviar",
                        variant="primary",
                        scale=1,
                    )

                # Example queries
                with gr.Accordion("Consultas de ejemplo", open=False):
                    examples = gr.Examples(
                        examples=create_example_queries(),
                        inputs=msg_input,
                        label="Ejemplos",
                    )

            # Right sidebar - Logs
            with gr.Column(scale=1, min_width=300):
                gr.HTML("""
                    <div class="sidebar-panel">
                        <div class="sidebar-title">Registro de Actividad</div>
                    </div>
                """)
                logs_panel = gr.HTML(
                    value='<div style="color: #71717a; font-size: 0.875rem;">Sin actividad reciente</div>',
                )

                # Quick actions
                with gr.Accordion("Acciones Rápidas", open=False):
                    clear_btn = gr.Button("Limpiar conversación", size="sm")
                    new_session_btn = gr.Button("Nueva sesión", size="sm")

        # Footer
        gr.HTML("""
            <div style="
                text-align: center;
                padding: 1rem;
                margin-top: 1rem;
                border-top: 1px solid #27272a;
                color: #71717a;
                font-size: 0.8125rem;
            ">
                Fintech AML Multi-Agent System • Powered by LangGraph + LangChain
                <br>
                <span style="color: #52525b;">
                    Cumplimiento: Ley 10/2010 PBC/FT • GDPR • SEPBLAC
                </span>
            </div>
        """)

        # Event handlers
        async def on_submit(message, history, state):
            return await process_message(message, history, state)

        def clear_chat():
            return [], {"session_id": None}

        def new_session():
            session = ChatSession()
            _sessions[session.session_id] = session
            return (
                [],
                {"session_id": session.session_id},
                format_workflow_status(None, None, None),
                format_context_panel(None),
                '<div style="color: #71717a; font-size: 0.875rem;">Nueva sesión iniciada</div>',
            )

        # Wire up events
        submit_btn.click(
            fn=on_submit,
            inputs=[msg_input, chatbot, session_state],
            outputs=[chatbot, session_state, workflow_status, context_panel, logs_panel],
        ).then(
            fn=lambda: "",
            outputs=[msg_input],
        )

        msg_input.submit(
            fn=on_submit,
            inputs=[msg_input, chatbot, session_state],
            outputs=[chatbot, session_state, workflow_status, context_panel, logs_panel],
        ).then(
            fn=lambda: "",
            outputs=[msg_input],
        )

        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, session_state],
        )

        new_session_btn.click(
            fn=new_session,
            outputs=[chatbot, session_state, workflow_status, context_panel, logs_panel],
        )

    return app


def launch_app(
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    share: bool = False,
    debug: bool = False,
) -> None:
    """
    Launch the Gradio application.

    Args:
        server_name: Server hostname
        server_port: Server port
        share: Create public URL
        debug: Enable debug mode
    """
    app = create_app()

    logger.info(f"Launching Fintech AML UI on {server_name}:{server_port}")

    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        debug=debug,
        show_error=True,
    )


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Launch Fintech AML UI")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument("--share", action="store_true", help="Create public URL")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    launch_app(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        debug=args.debug,
    )
