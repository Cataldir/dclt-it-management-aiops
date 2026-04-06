# Docs - Lesson 08

## Module Architecture

The module uses synthetic telemetry, decision rules, and a playbook catalog to show the behavior of an operational agent without depending on an external LLM.

## Artifacts And Outputs

- Remediation plan per incident.
- Playbook execution result.
- Monte Carlo report with aggregated metrics.

## Where To Apply It

- AgentOps simulation.
- Safety review of automated actions.
- Baseline before integrating MCP, a real LLM, or an Azure AI Foundry agent.

## Quick Troubleshooting

- If you want reproducible results, set `--seed` in the executions.
- Use `--auto-approve` only for demonstration; pending approval behavior is part of the lesson.
