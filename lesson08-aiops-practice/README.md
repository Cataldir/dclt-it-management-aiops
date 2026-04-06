# Lesson 08 - Agentic Remediation with Stochastic Evaluation

## Overview

This module closes the course with a full AI Ops flow: detect signals, diagnose the incident, plan remediation, require approval when necessary, execute a playbook, and measure agent behavior across multiple episodes. The core lesson scripts now support both `local-policy` and `foundry-agent` planning modes, while the pipeline-oriented scripts reuse the same execution path inside workflow steps.

## What You Will Practice

- Explicit policies for playbook selection.
- Foundry-backed diagnosis and playbook selection with local execution guardrails.
- Human-approval guardrails for sensitive actions.
- Simulated remediation execution.
- Stochastic evaluation of adherence, safety, and resolution.
- Foundry-backed evaluation gate for remediation runs.

## Technologies

- Python 3.13
- NumPy
- Azure AI Foundry through `azure-ai-projects`
- JSON for playbook contracts and reports

## Prerequisites

- Python 3.13
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation.
- `pyproject.toml`: lesson-local UV project definition.
- `.env.example`: environment variables for Azure AI Foundry integration.
- `.github/workflows/`: remediation and evaluation workflow.
- `anomaly_remediation.py`: main remediation flow.
- `agent_pipeline_common.py`: shared Foundry helper for pipeline scripts.
- `agentic_remediation_pipeline.py`: workflow-oriented remediation planner and executor.
- `agentic_evaluation_gate.py`: workflow-oriented evaluation gate for remediation runs.
- `stochastic_evaluation.py`: Monte Carlo evaluation.
- `playbooks.json`: versioned action catalog.

## Quick Start

```bash
uv sync --python 3.13
uv run python anomaly_remediation.py --scenario bad_release --mode local-policy --auto-approve --save-report artifacts/remediation.json
uv run python stochastic_evaluation.py --episodes 50 --mode local-policy --save-report artifacts/stochastic-eval.json
```

## End-To-End Mode Switch

```bash
uv run python anomaly_remediation.py --scenario bad_release --mode foundry-agent --auto-approve --save-report artifacts/remediation-foundry.json
uv run python stochastic_evaluation.py --episodes 10 --mode foundry-agent --save-report artifacts/stochastic-eval-foundry.json
```

`anomaly_remediation.py` uses the selected mode for diagnosis and playbook selection, while execution remains local and policy-checked through the playbook catalog. `stochastic_evaluation.py` reuses the same mode in every episode.

## Pipeline Agent Scripts

```bash
uv run python agentic_remediation_pipeline.py --scenario bad_release --mode auto --auto-approve --output artifacts/remediation-agent.json
uv run python stochastic_evaluation.py --episodes 25 --mode auto --save-report artifacts/stochastic-eval.json
uv run python agentic_evaluation_gate.py --report artifacts/stochastic-eval.json --mode auto --remediation-mode auto --enforce --output artifacts/evaluation-gate.json
```

### Running With Azure AI Foundry

```bash
cp .env.example .env
uv run python agentic_remediation_pipeline.py --scenario bad_release --mode foundry-agent --auto-approve --output artifacts/remediation-foundry.json
uv run python agentic_evaluation_gate.py --episodes 25 --mode foundry-agent --remediation-mode foundry-agent --output artifacts/evaluation-foundry.json
```

## Available Scenarios

- `healthy`
- `latency_spike`
- `cpu_saturation`
- `transient_error`
- `bad_release`

## Expected Outputs

- Incident diagnosis.
- Plan with rationale and approval requirements.
- Playbook execution result.
- Aggregated stochastic-evaluation report.
- Agent review for remediation planning.
- Agentic evaluation decision with `approve`, `hold`, or `reject`.

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture, usage, and troubleshooting.

## Where To Apply This Knowledge

- Agent-guided remediation in support and platform teams.
- Safety evaluation of agents before production.
- Human-in-the-loop flows for high-impact actions.
- CI/CD workflows that must decide whether remediation automation can advance.
- Labs comparing deterministic policy versus agent-driven planning on the same playbook catalog.

## Connection To The Track

- Reuses observability from Lesson 01.
- Reuses gates from Lesson 04.
- Can consume Lesson 06 MCP as the tooling backend.
- Reuses the Foundry integration pattern from Lesson 07, but applies it to remediation and evaluation scripts inside workflows.

## Natural Extension

Replace the temporary prompt agent with a dedicated deployed Foundry agent while keeping playbook contracts, approval, and evaluation intact.
