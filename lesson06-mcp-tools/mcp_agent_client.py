"""Lesson 06 MCP agent client.

Starts the MCP server as a subprocess, discovers available tools, and
orchestrates a remediation flow by calling tools in sequence.  The
orchestration strategy can be driven by local policy or by a Foundry agent.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from foundry_helper import (
    CLI_MODE_CHOICES,
    foundry_is_configured,
    normalize_mode,
    run_foundry_json_agent,
)

SERVER_SCRIPT = Path(__file__).with_name("mcp_server.py")


class MCPClient:
    """Thin wrapper around the MCP server subprocess (STDIO transport)."""

    def __init__(self) -> None:
        self._process = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request = {"jsonrpc": "2.0", "id": self._next_id(), "method": method}
        if params is not None:
            request["params"] = params
        assert self._process.stdin is not None
        assert self._process.stdout is not None
        self._process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
        self._process.stdin.flush()
        line = self._process.stdout.readline()
        if not line:
            raise RuntimeError("MCP server returned no response.")
        return json.loads(line)

    def list_tools(self) -> list[dict[str, Any]]:
        response = self.send("tools/list")
        return response.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        response = self.send("tools/call", {"name": name, "arguments": arguments})
        if "error" in response:
            raise RuntimeError(response["error"].get("message", "Unknown MCP error"))
        return response.get("result", {})

    def close(self) -> None:
        if self._process.stdin:
            self._process.stdin.close()
        self._process.terminate()
        self._process.wait(timeout=5)


def run_local_orchestration(
    client: MCPClient,
    service: str,
    auto_approve: bool = False,
    approved_by: str | None = None,
) -> dict[str, Any]:
    """Fixed sequence: check status → plan → execute."""
    status = client.call_tool("check_service_status", {"service_name": service})

    symptom = "unknown"
    severity = "medium"
    if status.get("error_rate", 0) > 0.05:
        symptom = "error_rate"
        severity = "critical" if status.get("error_rate", 0) > 0.08 else "high"
    elif status.get("latency_p95_ms", 0) > 400:
        symptom = "latency"
        severity = "high"

    plan = client.call_tool(
        "plan_remediation",
        {"service_name": service, "symptom": symptom, "severity": severity},
    )

    exec_args: dict[str, Any] = {
        "service_name": service,
        "playbook_id": plan["recommended_playbook"],
    }
    if auto_approve or approved_by:
        exec_args["approved_by"] = approved_by or "auto-approval-bot"

    execution = client.call_tool("execute_playbook", exec_args)

    return {
        "engine": "local-policy",
        "service_status": status,
        "plan": plan,
        "execution": execution,
        "summary": f"Local orchestration: {execution.get('status', 'unknown')}",
    }


def build_foundry_orchestration_prompt(
    tools: list[dict[str, Any]],
    service: str,
) -> str:
    tool_names = [t["name"] for t in tools]
    return (
        "You are an MCP orchestration agent. "
        f"Available tools: {tool_names}. "
        f"The target service is '{service}'. "
        "Decide which tools to call and in what order to diagnose and remediate the service. "
        "Respond ONLY in JSON with the keys: "
        "steps (list of objects with tool_name and arguments), rationale (list of strings), summary (string)."
    )


def run_foundry_orchestration(
    client: MCPClient,
    tools: list[dict[str, Any]],
    service: str,
    auto_approve: bool = False,
    approved_by: str | None = None,
) -> dict[str, Any]:
    response = run_foundry_json_agent(
        build_foundry_orchestration_prompt(tools, service),
        instructions=(
            "You are an MCP orchestration agent. "
            "Plan a tool-call sequence to diagnose and remediate the given service. "
            "Return the plan in JSON only."
        ),
        agent_name_env_var="FOUNDRY_MCP_AGENT_NAME",
        default_agent_name="mcp-orchestration-agent",
    )

    step_results: list[dict[str, Any]] = []
    for step in response.get("steps", []):
        tool_name = step.get("tool_name", "")
        arguments = step.get("arguments", {})
        if tool_name == "execute_playbook" and (auto_approve or approved_by):
            arguments["approved_by"] = approved_by or "auto-approval-bot"
        try:
            result = client.call_tool(tool_name, arguments)
            step_results.append({"tool_name": tool_name, "arguments": arguments, "result": result})
        except RuntimeError as error:
            step_results.append({"tool_name": tool_name, "arguments": arguments, "error": str(error)})

    response["step_results"] = step_results
    response.setdefault("summary", "Foundry orchestration completed")
    return response


def orchestrate(
    service: str = "fraud-api",
    mode: str = "auto",
    auto_approve: bool = False,
    approved_by: str | None = None,
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)
    client = MCPClient()
    fallback_reason: str | None = None

    try:
        tools = client.list_tools()

        if normalized_mode == "local-policy":
            assessment = run_local_orchestration(client, service, auto_approve, approved_by)
        elif normalized_mode == "foundry-agent":
            assessment = run_foundry_orchestration(client, tools, service, auto_approve, approved_by)
        else:
            if foundry_is_configured():
                try:
                    assessment = run_foundry_orchestration(client, tools, service, auto_approve, approved_by)
                except (ImportError, OSError, RuntimeError, ValueError) as error:
                    fallback_reason = str(error)
                    assessment = run_local_orchestration(client, service, auto_approve, approved_by)
            else:
                fallback_reason = "Foundry environment variables are missing; using local policy."
                assessment = run_local_orchestration(client, service, auto_approve, approved_by)
    finally:
        client.close()

    report: dict[str, Any] = {
        "requested_mode": normalized_mode,
        "service": service,
        "available_tools": [t["name"] for t in tools],
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
    parser = argparse.ArgumentParser(description="MCP agent client for Lesson 06")
    parser.add_argument("--service", default="fraud-api", help="Target service to diagnose.")
    parser.add_argument("--mode", choices=CLI_MODE_CHOICES, default="auto", help="Orchestration mode.")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve high-impact playbooks.")
    parser.add_argument("--approved-by", type=str, default=None, help="Human identity for approval.")
    parser.add_argument("--output", type=str, default=None, help="Optional path to persist the report.")
    args = parser.parse_args()

    report = orchestrate(
        service=args.service,
        mode=args.mode,
        auto_approve=args.auto_approve,
        approved_by=args.approved_by,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.output:
        save_report(args.output, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
