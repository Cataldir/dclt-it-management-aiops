# Docs - Lesson 07

## Module Architecture

The module separates responsibilities across workflow, source code, tests, and infrastructure, mirroring the continuous delivery pattern of software adapted to ML. The new `foundry_release_gate.py` acts as a governance layer between validation and deployment: it consolidates accuracy, fairness, and rollout strategy, then requests a decision from an Azure AI Foundry agent when that environment is configured.

## Artifacts And Outputs

- Model and metrics in `models/`.
- Workflow logs and status.
- `release-gate.json` report with an agentic decision or local fallback.
- Local registry of promoted models.

## Where To Apply It

- GitHub Actions for data teams.
- CI/CD with fairness and metric-regression checks.
- Pipelines that need to provision resources before deployment.
- DevOps teams that want to introduce agents without making CI cloud-dependent in local labs.

## Quick Troubleshooting

- If `pytest` fails, rerun `uv sync --python 3.13` from the lesson directory.
- If the deployment workflow does not reproduce locally, run `terraform init` inside `infra/`.
- If the gate falls back to `local-policy`, check whether `.env` was filled with `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_DEPLOYMENT_NAME`.
- If Foundry mode fails due to authentication, run `az login` before local execution.
