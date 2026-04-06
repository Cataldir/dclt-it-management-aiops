# Lesson 07 - Presentation Script

## Lesson Title

CI/CD for models: how to combine training, validation, deployment, and registration in a single pipeline.

## Learning Objective

By the end of this lesson, the class should understand:

1. How a workflow unifies ML artifacts and infrastructure.
2. Why technical gates must run before deployment.
3. How progressive delivery and registration fit into the final flow.

## Lesson Application

Application demonstrated: GitHub Actions workflow for credit-risk training with tests, fairness checks, Terraform, and model registration.

Extension in this version: an Azure AI Foundry agent can review the release context and issue a decision before deployment.

Main file: `.github/workflows/ml-pipeline.yml`

## Application Build Sequence

### Build 1 - Automated training

### Build 2 - Accuracy and fairness gate

### Build 3 - Agentic release gate with Azure AI Foundry

### Build 4 - Integration tests

### Build 5 - Provisioning with Terraform

### Build 6 - Canary deployment and registration

## Demo Commands

```bash
python src/train.py --data data/features/latest.csv --output models/credit_risk_local.pkl
python src/foundry_release_gate.py --model models/credit_risk_local.pkl --mode dry-run
pytest tests/integration -v
```

## Where To Apply This Knowledge

- MLOps in squads with CI/CD.
- Controlled model promotion.
- Governance for artifacts and infrastructure.
- Agent-assisted approval in DevOps release flows.
