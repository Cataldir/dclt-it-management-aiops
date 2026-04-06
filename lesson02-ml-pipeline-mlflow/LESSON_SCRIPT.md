# Lesson 02 - Presentation Script

## Lesson Title

AI development lifecycle: from dataset to artifact ready for governance and deployment.

## Learning Objective

By the end of this lesson, the class should understand:

1. That an AI project does not end at training time.
2. That traceability of parameters, metrics, and artifacts is part of the product.
3. That data, model, and documentation must move together.

## Lesson Application

Application demonstrated: local hospital readmission pipeline with training, evaluation, artifacts, and optional MLflow tracking.

Main file: `ml_pipeline.py`

## Application Build Sequence

### Build 1 - Prepare data

Goal: load a real CSV or generate a controlled synthetic dataset.

### Build 2 - Train with controlled parameters

Goal: show that training must be reproducible and explainable.

### Build 3 - Evaluate and record metrics

Goal: move the model out of notebook mode and into formal comparison.

### Build 4 - Save artifacts and document the model

Goal: show that the pipeline output is more than just a `.pkl` file.

### Build 5 - Optional tracking with MLflow

Goal: show the natural evolution from a local pipeline to an auditable experiment trail.

### Build 6 - Agent-backed experiment review

Goal: demonstrate how a Foundry agent (or local policy) can review training artifacts and suggest next steps.

## Demo Commands

```bash
python ml_pipeline.py --artifacts-dir artifacts
python ml_pipeline.py --data patient_data.csv --artifacts-dir artifacts
python experiment_review_agent.py --artifacts-dir artifacts --mode auto --output artifacts/review.json
python experiment_review_agent.py --artifacts-dir artifacts --mode foundry-agent --output artifacts/review-foundry.json
```

## Where To Apply This Knowledge

- Tabular classification projects in enterprises.
- Baseline delivery for MLOps pipelines.
- Experiment organization in data squads.
