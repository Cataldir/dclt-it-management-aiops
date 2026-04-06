# Lesson 02 - ML Pipeline with Tracking and Artifacts

## Overview

This module shows the minimum lifecycle of an AI application that needs to move beyond a notebook and become a reproducible artifact. The pipeline generates or loads data, trains the model, evaluates metrics, saves local artifacts, and records evidence for future comparison.

## What You Will Practice

- Data preparation for tabular classification.
- Reproducible training with controlled parameters.
- Technical evaluation with persisted metrics.
- Generation of `model.pkl`, `metrics.json`, and `model_card.md`.
- Optional tracking through MLflow.

## Technologies

- Python 3.13
- pandas
- scikit-learn
- MLflow
- Azure AI Foundry through `azure-ai-projects`

## Prerequisites

- Python 3.13
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation and practical applications.
- `ml_pipeline.py`: main executable.
- `experiment_review_agent.py`: agent-backed experiment review.
- `foundry_helper.py`: shared Foundry agent helper.
- `.env.example`: environment variables for Azure AI Foundry integration.
- `pyproject.toml`: lesson-local UV project definition.

## Quick Start

```bash
uv sync --python 3.13
uv run python ml_pipeline.py --artifacts-dir artifacts
```

To use your own CSV:

```bash
uv run python ml_pipeline.py --data patient_data.csv --artifacts-dir artifacts
```

## Experiment Review Agent

After running the pipeline, review the artifacts with the agent:

```bash
uv run python experiment_review_agent.py --artifacts-dir artifacts --mode auto --output artifacts/review.json
```

Use `--mode foundry-agent` with a configured `.env` to let a Foundry agent produce the review.

## Expected Outputs

- `artifacts/model.pkl`
- `artifacts/metrics.json`
- `artifacts/model_card.md`
- `artifacts/review.json` (experiment review agent output)

## Supporting Files

- See `LESSON_SCRIPT.md` for classroom delivery.
- See `docs/README.md` for architecture, practical usage, and troubleshooting.

## Where To Apply This Knowledge

- Baselines for fraud, churn, delinquency, and support.
- AI prototypes that need to become auditable pipelines.
- Data teams that need to hand off clear artifacts to MLOps.

## Connection To The Track

- Lesson 04 builds on the ideas of baselines and metrics for promotion gates.
- Lesson 07 reuses the same flow inside CI/CD.
- The experiment review agent pattern is reused across Lessons 03–06 and 08.

## Suggested Evaluation

- Compare different `seed` values and observe metric variation.
- Compare behavior with and without MLflow installed locally.
