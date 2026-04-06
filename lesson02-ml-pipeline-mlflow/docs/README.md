# Docs - Lesson 02

## Module Architecture

The module keeps every step inside a single Python executable to keep the lesson simple, but its outputs already separate responsibilities across data, model, metric, and documentation.

## Artifacts And Outputs

- Serialized model for local reuse.
- JSON metrics for comparing executions.
- Model card for communication and governance.

## Where To Apply It

- Baseline MLOps pipelines.
- Proofs of concept that need to become repeatable delivery assets.
- Initial artifact registration for CI/CD.

## Quick Troubleshooting

- If `mlflow` is not available, the pipeline still generates local artifacts.
- If `scikit-learn` or `pandas` are missing, rerun `uv sync --python 3.13` from the lesson directory.
