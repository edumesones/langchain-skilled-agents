# Fintech AML Multi-Agent System

A multi-agent system for **AML / fraud detection** built on **LangGraph**, where a
router-orchestrator dispatches each alert to specialized **Risk** and **Compliance**
agents and a **Synthesizer** merges their findings into a single decision. Ships with
a synthetic-data factory (customers, transactions, alerts, relationship graphs) so the
whole thing runs end-to-end with no real data.

```
                        ┌─────────────────┐
                        │   Orchestrator  │  (router + memory)
                        └────────┬────────┘
                  ┌──────────────┼──────────────┐
                  ▼              │              ▼
            ┌─────────┐          │        ┌────────────┐
            │  Risk   │          │        │ Compliance │
            └────┬────┘          │        └─────┬──────┘
                 └───────┬───────┴──────────────┘
                         ▼
                  ┌────────────┐
                  │Synthesizer │ ─► verdict + reasoning
                  └────────────┘
        (error_handler_node wraps the graph for graceful failures)
```

## Why this design

- **Specialized agents over one mega-prompt.** Risk scoring and regulatory compliance
  are different reasoning tasks with different prompts; separating them keeps each
  agent focused and its output auditable — which matters in a regulated AML context.
- **LangGraph orchestration with explicit routing.** `graph/` defines `state`, `nodes`,
  `edges` and conditional routers (`route_after_orchestrator`, `route_after_risk`,
  `route_after_compliance`) so the control flow is a real, inspectable graph, not an
  opaque agent loop. An `error_handler_node` keeps a single agent failure from crashing
  the run.
- **Synthetic data factory.** `data/synthetic/generators/` builds realistic customers,
  transactions, alerts and **relationship graphs** from seed files
  (`country_risk_scores.json`, `fraud_patterns.json`, `merchant_categories.json`).
  Anyone can clone and run it without sensitive data.
- **Provider-agnostic LLM config** (`config/llm_providers.py`) and typed settings via
  `pydantic-settings`.

## Tech stack

Python 3.11 · LangGraph / LangChain · OpenAI-compatible LLMs · Pydantic v2 ·
pandas / polars / pyarrow · Faker (synthetic data) · NetworkX + PyVis (relationship
graphs) · Gradio (UI) · Rich (CLI).

## Run it

```bash
uv venv && uv pip install -e .      # or: pip install -e .
cp .env.example .env                 # add your LLM provider key
python main.py --generate            # build synthetic dataset (parquet)
python main.py                       # launch the Gradio UI
python main.py --cli                 # interactive CLI mode
```

## Project layout

```
agents/         orchestrator (router + memory), risk, compliance — each with its prompts
graph/          LangGraph: state, nodes, edges, workflow
data/synthetic/ generators + seeds for customers / transactions / alerts / relationships
config/         settings, logging, LLM providers
main.py         entry point (UI / CLI / data generation)
```

> Context: built as a hands-on companion to production AML work (graph-based anomaly
> detection on transaction networks). See also
> [AWS_graph_fraud_detection_system](https://github.com/edumesones/AWS_graph_fraud_detection_system).
