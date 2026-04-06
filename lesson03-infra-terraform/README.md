# Lesson 03 - AI Infrastructure with Terraform

## Overview

This module shows how to move from an improvised environment to a repeatable infrastructure baseline for AI workloads. The stack uses Terraform to declare networking, cluster resources, and specialized capacity in a reproducible way that is ready to integrate with pipelines.

## What You Will Practice

- Declarative provisioning of AI infrastructure.
- Separation of responsibilities between network, cluster, and GPU capacity.
- Use of variables to adapt the same code to multiple environments.
- Exposure of outputs for integration with later workflows.

## Technologies

- Terraform 1.5+
- AzureRM Provider
- Azure AKS
- Python 3.13 (plan review agent)
- Azure AI Foundry through `azure-ai-projects`

## Prerequisites

- Terraform 1.5+
- Python 3.13 and `uv` (for the plan review agent)
- Optional Azure account to apply the real stack

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation and practical applications.
- `main.tf`: main stack.
- `terraform.tfvars.example`: example values.
- `plan_review_agent.py`: agent-backed Terraform plan reviewer.
- `foundry_helper.py`: shared Foundry agent helper.
- `.env.example`: environment variables for Azure AI Foundry integration.
- `pyproject.toml`: lesson-local UV project definition for the agent.

## Quick Start

```bash
terraform init
copy terraform.tfvars.example terraform.tfvars
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### Plan Review Agent

Review a Terraform plan with the agent (simulated plan when no file is provided):

```bash
uv sync --python 3.13
uv run python plan_review_agent.py --mode auto --output artifacts/plan-review.json
```

To review a real plan:

```bash
terraform show -json tfplan > plan.json
uv run python plan_review_agent.py --plan-file plan.json --mode auto --output artifacts/plan-review.json
```

## Provisioned Resources

- Resource Group with governance tags.
- Virtual Network and private subnet.
- AKS cluster.
- Dedicated GPU node pool.

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture, use cases, and troubleshooting.

## Where To Apply This Knowledge

- Cloud training and inference platforms.
- Standardized environments for data squads.
- IaC baselines integrated with MLOps and CI/CD.

## Connection To The Track

- Lesson 07 reuses the same declarative infrastructure concept in governed deployment.
- Later lessons build on this foundation for workflows and remediation.
