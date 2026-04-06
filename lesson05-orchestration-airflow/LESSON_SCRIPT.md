# Lesson 05 - Presentation Script

## Lesson Title

Model and agent orchestration: how to turn ML scripts into an operational workflow.

## Learning Objective

By the end of this lesson, the class should understand:

1. How a DAG organizes dependencies between stages.
2. Why validation, canary deployment, and rollout should live in the same flow.
3. How to prepare a pipeline for multiple environments and continuous operations.

## Lesson Application

Application demonstrated: weekly fraud pipeline in Airflow with ingestion, preprocessing, training, validation, canary deployment, and rollout.

Main file: `fraud_pipeline_dag.py`

## Application Build Sequence

### Build 1 - Ingestion and preprocessing

### Build 2 - Training and metrics

### Build 3 - Quality gate

### Build 4 - Canary deployment

### Build 5 - Monitoring and rollout

## Demo Commands

```bash
airflow dags test fraud_model_pipeline 2026-01-01
python scripts/ingest_transactions.py --output artifacts/raw_transactions.jsonl
```

## Where To Apply This Knowledge

- Recurring retraining pipelines.
- ML jobs with strong step dependencies.
- Controlled model promotion flows.
