# Lesson 04 - Model Validation Gate

## Overview

This module formalizes model promotion through technical and fairness gates. Instead of relying on manual comparison, the application measures baseline versus candidate behavior, emits a structured decision, and prepares the path for CI/CD, Airflow, and agent validation.

## What You Will Practice

- Comparison between the production baseline and a candidate model.
- Performance regression gate.
- Fairness gate by group.
- Structured decision output for pipelines.

## Technologies

- Python 3.13
- NumPy
- scikit-learn
- Azure AI Foundry through `azure-ai-projects`

## Prerequisites

- Python 3.13
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting module documentation.
- `model_validation.py`: main executable.
- `promotion_review_agent.py`: agent-backed promotion review.
- `foundry_helper.py`: shared Foundry agent helper.
- `.env.example`: environment variables for Azure AI Foundry integration.
- `pyproject.toml`: lesson-local UV project definition.

## Quick Start

```bash
uv sync --python 3.13
uv run python model_validation.py --scenario candidate_better --save-report artifacts/validation-report.json
```

### Promotion Review Agent

Review the validation output with the agent:

```bash
uv run python promotion_review_agent.py --report artifacts/validation-report.json --mode auto --output artifacts/promotion-review.json
```

Or generate a scenario and review it directly:

```bash
uv run python promotion_review_agent.py --scenario accuracy_regression --mode auto --output artifacts/promotion-review.json
```

## Available Scenarios

- `candidate_better`
- `accuracy_regression`
- `fairness_regression`

## Expected Outputs

- JSON report with baseline and candidate metrics.
- Result of each gate.
- Clear next-step recommendation.
- Agent-backed promotion review with rationale and recommended actions.

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for use cases and troubleshooting.

## Where To Apply This Knowledge

- Automated promotion of tabular models.
- ML governance in regulated environments.
- Pre-deployment validation before staging or production.

## Connection To The Track

- Lesson 05 reuses the gate concept before canary deployment.
- Lesson 07 reproduces the same pattern inside CI/CD.
- Lesson 08 applies the same reasoning to operational safety for agents.
- The promotion review agent follows the same Foundry integration pattern used across Lessons 02, 03, 05, 06, and 08.
