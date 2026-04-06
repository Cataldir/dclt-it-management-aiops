"""Lesson 03 Terraform plan review agent.

Analyzes a ``terraform show -json`` plan file (or a simulated plan) and
produces a risk assessment using local policy rules or an Azure AI Foundry
agent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from foundry_helper import (
    CLI_MODE_CHOICES,
    foundry_is_configured,
    normalize_mode,
    run_foundry_json_agent,
)

DESTRUCTIVE_ACTIONS = {"delete", "replace"}


def simulate_plan() -> dict[str, Any]:
    """Return a synthetic Terraform plan for demonstration."""
    return {
        "format_version": "1.2",
        "terraform_version": "1.7.0",
        "planned_values": {},
        "resource_changes": [
            {
                "address": "azurerm_resource_group.ai_rg",
                "type": "azurerm_resource_group",
                "change": {"actions": ["create"]},
            },
            {
                "address": "azurerm_virtual_network.ai_vnet",
                "type": "azurerm_virtual_network",
                "change": {"actions": ["create"]},
            },
            {
                "address": "azurerm_subnet.gpu_subnet",
                "type": "azurerm_subnet",
                "change": {"actions": ["create"]},
            },
            {
                "address": "azurerm_kubernetes_cluster.ai_cluster",
                "type": "azurerm_kubernetes_cluster",
                "change": {"actions": ["create"]},
            },
            {
                "address": "azurerm_kubernetes_cluster_node_pool.gpu_pool",
                "type": "azurerm_kubernetes_cluster_node_pool",
                "change": {"actions": ["create"]},
            },
        ],
    }


def load_plan(plan_path: str) -> dict[str, Any]:
    return json.loads(Path(plan_path).read_text(encoding="utf-8"))


def summarize_changes(plan: dict[str, Any]) -> dict[str, Any]:
    creates = 0
    updates = 0
    deletes = 0
    replaces = 0
    destructive_resources: list[str] = []

    for change in plan.get("resource_changes", []):
        actions = set(change.get("change", {}).get("actions", []))
        if "create" in actions:
            creates += 1
        if "update" in actions:
            updates += 1
        if "delete" in actions:
            deletes += 1
            destructive_resources.append(change["address"])
        if "replace" in actions:
            replaces += 1
            destructive_resources.append(change["address"])

    return {
        "total_changes": creates + updates + deletes + replaces,
        "creates": creates,
        "updates": updates,
        "deletes": deletes,
        "replaces": replaces,
        "destructive_resources": destructive_resources,
    }


def run_local_review(plan: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_changes(plan)
    reasons: list[str] = []
    decision = "approve"
    risk_level = "low"
    recommended_actions: list[str] = []

    if summary["deletes"] > 0 or summary["replaces"] > 0:
        decision = "hold"
        risk_level = "high"
        reasons.append(
            f"{summary['deletes']} delete(s) and {summary['replaces']} replace(s) detected: "
            f"{', '.join(summary['destructive_resources'])}."
        )
        recommended_actions.append("review destructive changes with the infrastructure owner before applying")

    if summary["total_changes"] == 0:
        reasons.append("No changes detected.")
        recommended_actions.append("verify that the plan file reflects the intended configuration")

    if decision == "approve":
        reasons.append(
            f"Plan contains {summary['creates']} create(s) and {summary['updates']} update(s) with no destructive operations."
        )
        recommended_actions.append("proceed with terraform apply")

    return {
        "engine": "local-policy",
        "decision": decision,
        "risk_level": risk_level,
        "change_summary": summary,
        "rationale": reasons,
        "recommended_actions": recommended_actions,
        "summary": f"Local plan review: {decision} (risk: {risk_level})",
    }


def build_foundry_prompt(plan: dict[str, Any]) -> str:
    summary = summarize_changes(plan)
    context = {
        "change_summary": summary,
        "resource_changes": plan.get("resource_changes", []),
    }
    return (
        "You are an infrastructure review agent responsible for assessing Terraform plans. "
        "Analyze the plan summary below and respond ONLY in JSON with the keys: "
        "decision (approve, hold, reject), risk_level (low, medium, high), "
        "rationale (list of strings), recommended_actions (list of strings), summary (string). "
        "Context:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def run_foundry_review(plan: dict[str, Any]) -> dict[str, Any]:
    response = run_foundry_json_agent(
        build_foundry_prompt(plan),
        instructions=(
            "You are an infrastructure review agent. "
            "Assess the Terraform plan for destructive actions and misconfigurations. "
            "Return a structured review in JSON only."
        ),
        agent_name_env_var="FOUNDRY_PLAN_AGENT_NAME",
        default_agent_name="terraform-plan-reviewer",
    )
    response.setdefault("decision", "hold")
    response.setdefault("risk_level", "medium")
    response.setdefault("rationale", [])
    response.setdefault("recommended_actions", [])
    response.setdefault("summary", "Foundry plan review completed")
    return response


def review_plan(
    plan_path: str | None = None,
    mode: str = "auto",
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)
    plan = load_plan(plan_path) if plan_path else simulate_plan()
    fallback_reason: str | None = None

    if normalized_mode == "local-policy":
        assessment = run_local_review(plan)
    elif normalized_mode == "foundry-agent":
        assessment = run_foundry_review(plan)
    else:
        if foundry_is_configured():
            try:
                assessment = run_foundry_review(plan)
            except (ImportError, OSError, RuntimeError, ValueError) as error:
                fallback_reason = str(error)
                assessment = run_local_review(plan)
        else:
            fallback_reason = "Foundry environment variables are missing; using local policy."
            assessment = run_local_review(plan)

    report: dict[str, Any] = {
        "requested_mode": normalized_mode,
        "assessment": assessment,
    }
    if fallback_reason:
        report["fallback_reason"] = fallback_reason
    return report


def save_report(path: str, report: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Terraform plan review agent for Lesson 03")
    parser.add_argument(
        "--plan-file",
        type=str,
        default=None,
        help="Path to a terraform show -json output. When omitted, a simulated plan is used.",
    )
    parser.add_argument("--mode", choices=CLI_MODE_CHOICES, default="auto", help="Review mode.")
    parser.add_argument("--output", type=str, default=None, help="Optional path to persist the review report.")
    args = parser.parse_args()

    report = review_plan(plan_path=args.plan_file, mode=args.mode)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        save_report(args.output, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
