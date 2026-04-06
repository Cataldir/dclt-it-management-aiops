# Lesson 07 - Governed CI/CD for Models

## Overview

This module organizes training, validation, provisioning, deployment, and registration into a single CI/CD pipeline. The goal is to show how models, tests, and infrastructure should be treated as part of the same governed delivery flow.

It now also includes an agentic release governance gate: the pipeline can consult an Azure AI Foundry agent to assess operational risk before deployment, with a deterministic local fallback when the lesson runs without Azure credentials.

## What You Will Practice

- Automated training from a reproducible dataset.
- Accuracy and fairness gates.
- Contract tests for the pipeline.
- Agentic release approval in a DevOps context.
- Declarative provisioning in the deployment job.
- Local registration of promoted models.

## Technologies

- Python 3.11+
- GitHub Actions
- Terraform
- pytest
- scikit-learn
- Azure AI Foundry through `azure-ai-projects`

## Prerequisites

- Python 3.11+
- `pip`
- Terraform 1.5+ to reproduce deployment locally
- Optional Azure AI Foundry project to enable the real agent mode

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation.
- `.github/workflows/`: CI/CD workflow.
- `src/`: training, evaluation, fairness, agentic gate, deployment, and registration.
- `tests/`: contract tests.
- `infra/`: Terraform deployment stack.
- `.env.example`: environment variables for Azure AI Foundry integration.

## Quick Start

```bash
pip install -r requirements-ml.txt
python src/train.py --data data/features/latest.csv --output models/credit_risk_local.pkl
python src/evaluate.py --model models/credit_risk_local.pkl --data data/features/latest.csv
python src/bias_check.py --model models/credit_risk_local.pkl --data data/features/latest.csv
python src/foundry_release_gate.py --model models/credit_risk_local.pkl --mode dry-run --output artifacts/release-gate.json
pytest tests/integration -v
```

### Running With Azure AI Foundry

```bash
cp .env.example .env
python src/foundry_release_gate.py --model models/credit_risk_local.pkl --mode foundry --output artifacts/release-gate-foundry.json
```

## Expected Outputs

- Serialized model in `models/`.
- Training-related metrics.
- Fairness result.
- Release agent assessment with decision `approve`, `hold`, or `reject`.
- Local promotion registry entry.

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture, flow, and troubleshooting.

## Where To Apply This Knowledge

- Governed tabular-model pipelines.
- Teams that need to unify data, QA, and infrastructure.
- Controlled model promotion to staging and production.
- Agentic risk review before moving forward in the pipeline.

## Connection To The Track

- Reuses the gates from Lesson 04.
- Reuses the operational logic from Lesson 05.
- Prepares the ground for agent-assisted remediation and rollback in Lesson 08.
