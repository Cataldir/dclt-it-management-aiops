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

## Prerequisites

- Python 3.13
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting module documentation.
- `model_validation.py`: main executable.
- `pyproject.toml`: lesson-local UV project definition.

## Quick Start

```bash
uv sync --python 3.13
uv run python model_validation.py --scenario candidate_better --save-report artifacts/validation-report.json
```

## Available Scenarios

- `candidate_better`
- `accuracy_regression`
- `fairness_regression`

## Expected Outputs

- JSON report with baseline and candidate metrics.
- Result of each gate.
- Clear next-step recommendation.

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
