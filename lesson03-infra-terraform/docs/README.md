# Docs - Lesson 03

## Module Architecture

The module declares a minimal AI infrastructure stack with a private network, managed cluster, and isolated GPU capacity for specialized workloads.

## Artifacts And Outputs

- Terraform stack ready for `plan` and `apply`.
- Outputs for integration with later automation.

## Where To Apply It

- Internal MLOps platforms.
- Cloud training environments.
- Governance and cost baselines for data squads.

## Quick Troubleshooting

- If the Azure provider is not authenticated, run `az login` before `terraform plan`.
- Adjust `terraform.tfvars` to avoid unavailable SKUs or regions.
