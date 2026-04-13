"""Agentic release gate with optional Azure AI Foundry support."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any

from common import (
    evaluate_model_accuracy,
    load_model,
    load_or_create_dataset,
    measure_fairness_gap,
    write_json_artifact,
)

FOUNDRY_REQUIRED_ENV_VARS = (
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_MODEL_DEPLOYMENT_NAME",
)


def foundry_is_configured() -> bool:
    """Return whether the local environment is configured to use Foundry."""
    from dotenv import load_dotenv

    load_dotenv(override=False)
    return all(os.getenv(variable_name) for variable_name in FOUNDRY_REQUIRED_ENV_VARS)


def build_release_context(
    model_path: str,
    data_path: str,
    accuracy_threshold: float,
    max_fairness_gap: float,
    deployment_strategy: str,
    traffic_weight: int,
    seed: int = 42,
) -> dict[str, Any]:
    """Build the technical context reviewed by the release gate."""
    dataset = load_or_create_dataset(data_path, seed=seed)
    model = load_model(model_path)
    accuracy = evaluate_model_accuracy(model, dataset, seed=seed)
    fairness = measure_fairness_gap(model, dataset, seed=seed)

    return {
        "model_path": model_path,
        "data_path": data_path,
        "seed": seed,
        "metrics": {
            "accuracy": round(accuracy, 4),
            "min_accuracy": round(accuracy_threshold, 4),
        },
        "fairness": {
            "fairness_gap": round(float(fairness["fairness_gap"]), 4),
            "max_fairness_gap": round(max_fairness_gap, 4),
            "recall_by_group": fairness["recall_by_group"],
        },
        "deployment": {
            "strategy": deployment_strategy,
            "traffic_weight": traffic_weight,
        },
    }


def run_local_release_policy(context: dict[str, Any]) -> dict[str, Any]:
    """Apply a deterministic local policy for labs without cloud access."""
    accuracy = float(context["metrics"]["accuracy"])
    minimum_accuracy = float(context["metrics"]["min_accuracy"])
    fairness_gap = float(context["fairness"]["fairness_gap"])
    maximum_gap = float(context["fairness"]["max_fairness_gap"])
    traffic_weight = int(context["deployment"]["traffic_weight"])
    strategy = str(context["deployment"]["strategy"])

    reasons: list[str] = []
    recommended_actions: list[str] = []
    decision = "approve"
    risk_level = "low"
    requires_human_approval = False

    if accuracy < minimum_accuracy:
        decision = "reject"
        risk_level = "high"
        reasons.append(
            f"Accuracy {accuracy:.4f} is below the minimum threshold {minimum_accuracy:.4f}."
        )
        recommended_actions.append("retrain the model before allowing any rollout")

    if fairness_gap > maximum_gap:
        decision = "reject"
        risk_level = "high"
        reasons.append(
            f"Fairness gap {fairness_gap:.4f} is above the allowed limit {maximum_gap:.4f}."
        )
        recommended_actions.append("review the model and affected segments before deployment")

    if decision == "approve" and strategy == "canary" and traffic_weight > 10:
        decision = "hold"
        risk_level = "medium"
        requires_human_approval = True
        reasons.append("Canary traffic above 10% requires human approval.")
        recommended_actions.append("reduce the canary to 10% or collect manual approval")

    if decision == "approve" and accuracy < minimum_accuracy + 0.015:
        decision = "hold"
        risk_level = "medium"
        requires_human_approval = True
        reasons.append("Accuracy too close to the threshold requires reinforced follow-up.")
        recommended_actions.append("monitor the deployment for at least 30 minutes before full rollout")

    if decision == "approve":
        reasons.append("Metrics and fairness are within the safe window for initial deployment.")
        recommended_actions.append("proceed with the canary deployment under reinforced observability")
        recommended_actions.append("register the model only after monitoring the initial signals")

    if decision == "hold" and not recommended_actions:
        recommended_actions.append("collect human approval before continuing the release")

    summary_map = {
        "approve": "Release approved for canary deployment",
        "hold": "Release awaiting human approval",
        "reject": "Release rejected by the gate",
    }
    return {
        "engine": "local-policy",
        "decision": decision,
        "risk_level": risk_level,
        "requires_human_approval": requires_human_approval,
        "rationale": reasons,
        "recommended_actions": recommended_actions,
        "summary": summary_map[decision],
    }


def build_foundry_prompt(context: dict[str, Any]) -> str:
    """Build the prompt sent to the release-governance agent."""
    return (
        "You are a DevOps governance agent responsible for approving model releases. "
        "Analyze the context below and respond ONLY in JSON with the keys: "
        "decision, risk_level, requires_human_approval, rationale, recommended_actions, summary. "
        "Use decision in {approve, hold, reject}. "
        "If risk is high, block the deployment. Context:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def parse_agent_json(raw_text: str) -> dict[str, Any]:
    """Extract the first valid JSON object returned by the agent."""
    stripped = raw_text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Agent response does not contain valid JSON.")
    return json.loads(stripped[start : end + 1])


def run_foundry_release_review(context: dict[str, Any]) -> dict[str, Any]:
    """Run release review with a versioned agent in Azure AI Foundry.

    Uses the Microsoft Agent Framework SDK (agent-framework-azure-ai).
    """
    from dotenv import load_dotenv

    load_dotenv(override=False)

    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    agent_name = os.getenv("FOUNDRY_RELEASE_AGENT_NAME", "devops-release-governor")

    if not project_endpoint or not model_name:
        raise ValueError(
            "Set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME to use Foundry mode."
        )

    async def _run() -> dict[str, Any]:
        from agent_framework import Message
        from agent_framework.azure import AzureAIClient
        from azure.identity.aio import DefaultAzureCredential

        async with DefaultAzureCredential() as credential:
            client = AzureAIClient(
                project_endpoint=project_endpoint,
                model_deployment_name=model_name,
                agent_name=agent_name,
                credential=credential,
                use_latest_version=True,
            )
            try:
                response = await client.get_response([
                    Message("system", [
                        "You are a DevOps governance agent. "
                        "Evaluate model release risk based on accuracy, fairness, and rollout strategy. "
                        "Respond only in JSON."
                    ]),
                    Message("user", [build_foundry_prompt(context)]),
                ])
                result = parse_agent_json(response.text)
                result["engine"] = "azure-ai-foundry"
                result["agent_name"] = agent_name
                return result
            finally:
                await client.close()

    return asyncio.run(_run())


def evaluate_release(
    context: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    """Choose between Foundry and local fallback to issue the release decision."""
    fallback_reason: str | None = None

    if mode == "dry-run":
        assessment = run_local_release_policy(context)
    elif mode == "foundry":
        assessment = run_foundry_release_review(context)
    else:
        if foundry_is_configured():
            try:
                assessment = run_foundry_release_review(context)
            except Exception as error:  # pragma: no cover - depende de Azure real
                fallback_reason = str(error)
                assessment = run_local_release_policy(context)
        else:
            fallback_reason = "Foundry environment variables are missing; using local policy."
            assessment = run_local_release_policy(context)

    report: dict[str, Any] = {
        "context": context,
        "assessment": assessment,
    }
    if fallback_reason:
        report["fallback_reason"] = fallback_reason
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic release gate for Lesson 07")
    parser.add_argument("--model", type=str, required=True, help="Serialized model.")
    parser.add_argument("--data", type=str, default="data/features/latest.csv", help="Evaluation dataset.")
    parser.add_argument(
        "--accuracy-threshold",
        type=float,
        default=0.85,
        help="Minimum required accuracy for the release.",
    )
    parser.add_argument(
        "--max-fairness-gap",
        type=float,
        default=0.18,
        help="Maximum allowed gap across segments.",
    )
    parser.add_argument(
        "--deployment-strategy",
        type=str,
        default="canary",
        help="Planned rollout strategy.",
    )
    parser.add_argument(
        "--traffic-weight",
        type=int,
        default=10,
        help="Planned traffic percentage for the initial rollout.",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "dry-run", "foundry"],
        default="auto",
        help="Gate execution mode: local, Azure AI Foundry, or automatic.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for split reproducibility.")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to persist the gate assessment.",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Fail the process when the final decision is not approve.",
    )
    args = parser.parse_args()

    context = build_release_context(
        model_path=args.model,
        data_path=args.data,
        accuracy_threshold=args.accuracy_threshold,
        max_fairness_gap=args.max_fairness_gap,
        deployment_strategy=args.deployment_strategy,
        traffic_weight=args.traffic_weight,
        seed=args.seed,
    )
    report = evaluate_release(context, mode=args.mode)

    if args.output:
        write_json_artifact(args.output, report)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.enforce and (
        report["assessment"]["decision"] != "approve"
        or report["assessment"].get("requires_human_approval", False)
    ):
        raise SystemExit(
            f"Release blocked by the agentic gate: {report['assessment']['decision']}"
        )


if __name__ == "__main__":
    main()