# Lesson 04 - Presentation Script

## Lesson Title

Model validation in MLOps: how to prevent silent regression before deployment.

## Learning Objective

By the end of this lesson, the class should understand:

1. That a new model should not be promoted just because it was trained later.
2. That performance regression and fairness regression need separate gates.
3. That validation must produce an objective decision consumable by CI/CD.

## Lesson Application

Application demonstrated: local gate that compares the production baseline with a candidate, measures accuracy, measures F1 by group, and decides whether the model can move to staging.

Main file: `model_validation.py`

## Application Build Sequence

### Build 1 - Define baseline and candidate

### Build 2 - Performance regression gate

### Build 3 - Fairness gate by group

### Build 4 - Produce a structured decision

## Demo Commands

```bash
python model_validation.py --scenario candidate_better --save-report artifacts/approved.json
python model_validation.py --scenario accuracy_regression --save-report artifacts/performance-regression.json
python model_validation.py --scenario fairness_regression --save-report artifacts/fairness-regression.json
```

## Where To Apply This Knowledge

- Enterprise MLOps with promotion gates.
- Technical governance for models.
- Behavior validation before automated rollout.
