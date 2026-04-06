# Docs - Lesson 03

## Module Architecture

The module declares a minimal AI infrastructure stack with a private network, managed cluster, and isolated GPU capacity for specialized workloads.

## Artifacts And Outputs

- Terraform stack ready for `plan` and `apply`.
- Outputs for integration with later automation.
- Agent-backed plan review report (via `plan_review_agent.py`).

## Where To Apply It

- Internal MLOps platforms.
- Cloud training environments.
- Governance and cost baselines for data squads.
- Automated risk assessment of infrastructure changes before apply.

## Quick Troubleshooting

- If the Azure provider is not authenticated, run `az login` before `terraform plan`.
- Adjust `terraform.tfvars` to avoid unavailable SKUs or regions.
- To review a real plan, run `terraform show -json tfplan > plan.json` and pass it to `plan_review_agent.py --plan-file plan.json`.
- If the plan review agent falls back to local mode, check whether `.env` contains the Foundry environment variables.
