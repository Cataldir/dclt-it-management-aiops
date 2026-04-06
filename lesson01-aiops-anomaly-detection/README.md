# Lesson 01 - AIOps Anomaly Monitor

## Overview

This module introduces the transition from reactive operations based on static alerts to an AIOps approach driven by operational signals. The application simulates telemetry, detects anomalies, and generates a structured report that can be consumed by pipelines, ITSM flows, or agents.

## What You Will Practice

- Generating synthetic telemetry for operational incidents.
- Detecting anomalies through a statistical baseline.
- Classifying severity and recommending an initial action.
- Producing structured output for downstream automation.

## Technologies

- Python 3.13
- NumPy
- JSON as the operational handoff format

## Prerequisites

- Python 3.13
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation and practical application notes.
- `anomaly_detection.py`: main executable for the lesson.
- `pyproject.toml`: lesson-local UV project definition.

## Quick Start

```bash
uv sync --python 3.13
uv run python anomaly_detection.py --scenario latency_spike --save-report artifacts/lesson01-report.json
```

## Available Scenarios

- `healthy`
- `latency_spike`
- `error_burst`
- `cpu_saturation`

## Expected Outputs

- JSON report with the observed signals.
- Incident detection and severity.
- Initial operational recommendation.
- Human approval flag when applicable.

## Supporting Files

- See `LESSON_SCRIPT.md` for live lesson delivery.
- See `docs/README.md` for architecture, usage, and quick troubleshooting.

## Where To Apply This Knowledge

- API and microservice monitoring.
- Initial incident triage in NOC and SRE teams.
- Observability foundation for remediation workflows.

## Connection To The Track

- Lesson 02 turns signals and artifacts into an ML pipeline.
- Lesson 08 reuses the same incident pattern for agentic remediation.

## Suggested Evaluation

- Vary `--sigma` to observe sensitivity versus false positives.
- Compare scenarios and validate whether the severity matches the operational impact.
