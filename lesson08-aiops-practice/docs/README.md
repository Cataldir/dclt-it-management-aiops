# Docs - Lesson 08

## Module Architecture

The module now has two layers: a core remediation flow that can run in `local-policy`, `foundry-agent`, or `auto` mode, plus workflow-oriented wrapper scripts that call the same core path inside CI/CD jobs.

## Artifacts And Outputs

- Remediation plan per incident.
- Playbook execution result.
- Monte Carlo report with aggregated metrics.
- Remediation pipeline report with agent metadata or local fallback information.
- Evaluation gate report with `approve`, `hold`, or `reject`.

## Where To Apply It

- AgentOps simulation.
- Safety review of automated actions.
- Baseline before integrating MCP or moving to a dedicated deployed Foundry agent.

## Quick Troubleshooting

- If you want reproducible results, set `--seed` in the executions.
- Use `--auto-approve` only for demonstration; pending approval behavior is part of the lesson.
- Use `--mode local-policy` to demonstrate deterministic planning and `--mode foundry-agent` when you want diagnosis and playbook selection to come from a Foundry agent.
- If the pipeline scripts fall back to local mode, check whether `.env` contains `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_DEPLOYMENT_NAME`.
- If Foundry mode is enabled locally, run `az login` before executing the pipeline scripts.
