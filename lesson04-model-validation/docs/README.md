# Docs - Lesson 04

## Module Architecture

The module takes a production baseline and a candidate, computes global and group-level metrics, and returns a structured decision for promotion or blocking.

## Artifacts And Outputs

- Final decision: `approved` or `rejected`.
- Gate-by-gate result.
- Recommended next step for the pipeline.
- Agent-backed promotion review with human-readable rationale (via `promotion_review_agent.py`).

## Where To Apply It

- Periodic model revalidation.
- Candidate promotion inside CI/CD pipelines.
- Regulated environments with fairness requirements.
- Automated promotion triage before stakeholder sign-off.

## Quick Troubleshooting

- If `scikit-learn` is not installed, rerun `uv sync --python 3.13` from the lesson directory.
- Use the three provided scenarios to demonstrate approval, performance rejection, and fairness rejection.
- If the promotion review agent falls back to local mode, check whether `.env` contains the Foundry environment variables.
