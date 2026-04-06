# Docs - Lesson 01

## Module Architecture

The module is composed of a single Python executable that generates operational signals, detects anomalous behavior, and produces a structured JSON report.

## Artifacts And Outputs

- Report with current signals and baseline.
- Operational severity.
- Initial action recommendation.

## Where To Apply It

- Internal API monitoring.
- Observability for enterprise services.
- Baseline for event correlation in AIOps.

## Quick Troubleshooting

- If `numpy` is not installed, rerun `uv sync --python 3.13` from the lesson directory.
- If you want to compare scenarios, save each execution to a different JSON file under `artifacts/`.
