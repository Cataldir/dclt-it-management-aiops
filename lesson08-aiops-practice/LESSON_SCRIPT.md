# Lesson 08 - Presentation Script

## Lesson Title

Agentic remediation: how to close the loop between detection, decision, approval, and action.

## Learning Objective

By the end of this lesson, the class should understand:

1. How to structure an operational agent with policies and playbooks.
2. Why human approval still matters for sensitive actions.
3. How to evaluate an agent repeatedly before trusting it.

## Lesson Application

Application demonstrated: the same remediation flow running in `local-policy` or `foundry-agent` mode, plus workflow-oriented agent scripts for remediation planning and evaluation review.

Main files: `anomaly_remediation.py`, `agentic_remediation_pipeline.py`, `stochastic_evaluation.py`, and `agentic_evaluation_gate.py`

## Application Build Sequence

### Build 1 - Detect and classify the incident

### Build 2 - Choose the right playbook with local policy or a Foundry agent

### Build 3 - Require approval when necessary

### Build 4 - Execute remediation

### Build 5 - Measure adherence, safety, and resolution

### Build 6 - Add an agentic evaluation gate to the workflow

## Demo Commands

```bash
python anomaly_remediation.py --scenario bad_release --mode local-policy --auto-approve
python stochastic_evaluation.py --episodes 10 --mode local-policy
python anomaly_remediation.py --scenario bad_release --mode foundry-agent --auto-approve
python stochastic_evaluation.py --episodes 10 --mode foundry-agent
python agentic_remediation_pipeline.py --scenario bad_release --mode auto --auto-approve --output artifacts/remediation-agent.json
python agentic_evaluation_gate.py --episodes 10 --mode auto --remediation-mode auto --output artifacts/evaluation-gate.json
```

## Where To Apply This Knowledge

- AgentOps for support and platform operations.
- Human-in-the-loop actions.
- Behavior validation before more aggressive automation.
