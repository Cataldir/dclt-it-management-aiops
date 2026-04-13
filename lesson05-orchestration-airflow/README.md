# Lesson 05 - Model Orchestration in Airflow

## Overview

This module turns isolated scripts into a repeatable and monitorable workflow. The application orchestrates ingestion, preprocessing, training, validation, canary deployment, and rollout decisions using Apache Airflow as the main coordinator.

## What You Will Practice

- Defining a DAG for operational ML.
- Clear separation between data, training, and deployment tasks.
- A quality gate before canary deployment.
- Canary monitoring and rollout decisions.

## Technologies

- Python 3.13
- Apache Airflow
- pandas
- scikit-learn
- Azure AI Foundry through `azure-ai-projects`

## Prerequisites

- Python 3.13
- Apache Airflow 2.8+
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation.
- `pyproject.toml`: lesson-local UV project definition.
- `fraud_pipeline_dag.py`: main DAG.
- `preprocess.py`, `evaluate.py`, `monitor.py`: workflow components.
- `canary_observer_agent.py`: agent-backed canary deployment observer.
- `foundry_helper.py`: shared Foundry agent helper.
- `.env.example`: environment variables for Azure AI Foundry integration.
- `scripts/`: helper operational scripts.
- `k8s/`: illustrative canary manifest.

## Quick Start

Preferred for students (cross-platform, including Windows):

```bash
cd lesson05-orchestration-airflow
docker compose up --build -d
docker compose exec airflow-webserver airflow dags test fraud_model_pipeline 2026-01-01
```

Airflow UI: `http://localhost:8080`  
Default credentials: `admin` / `admin`

To stop the environment:

```bash
docker compose down -v
```

Local UV path (optional):

```bash
uv sync --python 3.13
uv run airflow dags test fraud_model_pipeline 2026-01-01
```

To run components individually:

```bash
uv run python scripts/ingest_transactions.py --output artifacts/raw_transactions.jsonl
uv run python scripts/train_fraud_model.py --input artifacts/training_dataset.csv --model-output artifacts/fraud_model.pkl --metrics-output artifacts/metrics.json --fairness-output artifacts/fairness.json
```

### Canary Observer Agent

Observe a canary deployment with the agent (simulated scenarios when no report is provided):

```bash
uv run python canary_observer_agent.py --scenario healthy --mode auto --output artifacts/canary-observation.json
uv run python canary_observer_agent.py --scenario error_spike --mode auto --output artifacts/canary-observation-error.json
```

Available canary scenarios: `healthy`, `error_spike`, `latency_breach`, `accuracy_drop`.

## Expected Outputs

- Synthetic transaction dataset.
- Serialized fraud model.
- Metrics and fairness report.
- Canary report and rollout decision.
- Agent-backed canary observation review.

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture and troubleshooting.

## Where To Apply This Knowledge

- Periodic retraining pipelines.
- Orchestration of fraud, risk, and support jobs.
- Canary deployment flows with observability.

## Connection To The Track

- Lesson 06 expands control through MCP tools.
- Lesson 07 takes the same flow into governed CI/CD.
- Lesson 08 closes the loop with agentic remediation.
- The canary observer agent follows the same Foundry integration pattern used across Lessons 02–04, 06, and 08.
