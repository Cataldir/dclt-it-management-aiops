# Docs - Lesson 05

## Module Architecture

The module uses a DAG as the backbone of the process. Each task emits an intermediate artifact consumed by the next stage, which reduces coupling and makes repetition easier.

## Artifacts And Outputs

- Raw data and processed dataset.
- Trained model.
- Metrics, fairness, and canary reports.
- Final rollout decision.

## Where To Apply It

- Airflow in data and ML pipelines.
- Fraud, recommendation, or scoring orchestration.
- Progressive delivery with technical criteria.

## Quick Troubleshooting

- If Airflow is not configured, run the scripts individually first.
- If the DAG fails, check whether the `artifacts/` folder is being created and whether the Python dependencies were installed.
