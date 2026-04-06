# Lesson 08 - Agentic Remediation with Stochastic Evaluation

## Overview

This module closes the course with a full AI Ops flow: detect signals, diagnose the incident, plan remediation, require approval when necessary, execute a playbook, and measure agent behavior across multiple episodes.

## What You Will Practice

- Explicit policies for playbook selection.
- Human-approval guardrails for sensitive actions.
- Simulated remediation execution.
- Stochastic evaluation of adherence, safety, and resolution.

## Technologies

- Python 3.11+
- NumPy
- JSON for playbook contracts and reports

## Prerequisites

- Python 3.11+
- `pip`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation.
- `anomaly_remediation.py`: main remediation flow.
- `stochastic_evaluation.py`: Monte Carlo evaluation.
- `playbooks.json`: versioned action catalog.

## Quick Start

```bash
pip install -r requirements.txt
python anomaly_remediation.py --scenario bad_release --auto-approve --save-report artifacts/remediation.json
python stochastic_evaluation.py --episodes 50 --save-report artifacts/stochastic-eval.json
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

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture, usage, and troubleshooting.

## Where To Apply This Knowledge

- Agent-guided remediation in support and platform teams.
- Safety evaluation of agents before production.
- Human-in-the-loop flows for high-impact actions.

## Connection To The Track

- Reuses observability from Lesson 01.
- Reuses gates from Lesson 04.
- Can consume Lesson 06 MCP as the tooling backend.
- Can reuse the Azure AI Foundry gate from Lesson 07 to decide rollback and promotion.

## Natural Extension

Replace the local policy engine with an LLM-based agent or a hosted Azure AI Foundry agent while keeping playbook contracts, approval, and evaluation intact.
