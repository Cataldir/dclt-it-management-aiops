# Lesson 08 - Presentation Script

## Lesson Title

Agentic remediation: how to close the loop between detection, decision, approval, and action.

## Learning Objective

By the end of this lesson, the class should understand:

1. How to structure an operational agent with policies and playbooks.
2. Why human approval still matters for sensitive actions.
3. How to evaluate an agent repeatedly before trusting it.

## Lesson Application

Application demonstrated: local remediation flow with playbook selection, approval, execution, and Monte Carlo evaluation.

Main files: `anomaly_remediation.py` and `stochastic_evaluation.py`

## Application Build Sequence

### Build 1 - Detect and classify the incident

### Build 2 - Choose the right playbook

### Build 3 - Require approval when necessary

### Build 4 - Execute remediation

### Build 5 - Measure adherence, safety, and resolution

## Demo Commands

```bash
python anomaly_remediation.py --scenario bad_release --auto-approve
python stochastic_evaluation.py --episodes 10
```

## Where To Apply This Knowledge

- AgentOps for support and platform operations.
- Human-in-the-loop actions.
- Behavior validation before more aggressive automation.
