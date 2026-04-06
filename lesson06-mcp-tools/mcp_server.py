"""Lesson 06 mini-application for exposing tools through MCP."""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Any


# ── Tool Registry ───────────────────────────────────────────

TOOLS_DIR = Path(__file__).parent
AUDIT_LOG = TOOLS_DIR / "audit_log.jsonl"

SERVICE_STATE = {
    "fraud-api": {
        "status": "degraded",
        "latency_p95_ms": 410,
        "error_rate": 0.061,
        "recent_change": "deploy fraud-api:v2.4.1",
    },
    "payments-api": {
        "status": "healthy",
        "latency_p95_ms": 210,
        "error_rate": 0.012,
        "recent_change": "no_change_detected",
    },
    "support-agent": {
        "status": "warning",
        "latency_p95_ms": 360,
        "error_rate": 0.028,
        "recent_change": "tool_schema_upgrade",
    },
}

PLAYBOOKS = {
    "scale_out_service": {
        "description": "Increase the horizontal capacity of the service.",
        "requires_human_approval": False,
    },
    "restart_workers": {
        "description": "Restart failed workers without changing the production version.",
        "requires_human_approval": False,
    },
    "rollback_release": {
        "description": "Revert the most recent deployment to the previous version.",
        "requires_human_approval": True,
    },
    "open_incident_ticket": {
        "description": "Escalate the issue for structured human handling.",
        "requires_human_approval": False,
    },
}

def load_tool_definitions() -> list[dict[str, Any]]:
    """Load tool definitions from JSON files."""
    tools: list[dict[str, Any]] = []
    for file_path in TOOLS_DIR.glob("tool_*.json"):
        with open(file_path, encoding="utf-8") as file_handle:
            tools.append(json.load(file_handle))
    return tools


TOOLS_REGISTRY = load_tool_definitions()


def record_audit_event(event: dict[str, Any]) -> None:
    """Write a simple operational event to the local audit trail."""
    event["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(event, ensure_ascii=False) + "\n")


# ── Tool Handlers ───────────────────────────────────────────

def handle_create_github_issue(params: dict[str, Any]) -> dict[str, Any]:
    """Simulate creating a GitHub issue."""
    repo = params["repo"]
    title = params["title"]
    body = params.get("body", "")
    result = {
        "issue_url": f"https://github.com/{repo}/issues/42",
        "title": title,
        "body": body,
        "status": "created",
    }
    print(f"[MCP] Creating issue in repo '{repo}': {title}", file=sys.stderr)
    record_audit_event({"tool": "create_github_issue", "arguments": params, "result": result})
    return result


def handle_check_service_status(params: dict[str, Any]) -> dict[str, Any]:
    """Return the operational context of a known service."""
    service_name = params["service_name"]
    service_state = SERVICE_STATE.get(service_name)
    if service_state is None:
        raise ValueError(f"Unknown service: {service_name}")

    result = {"service_name": service_name, **service_state}
    record_audit_event({"tool": "check_service_status", "arguments": params, "result": result})
    return result


def handle_plan_remediation(params: dict[str, Any]) -> dict[str, Any]:
    """Turn symptoms into a guarded remediation plan."""
    symptom = params["symptom"]
    severity = params["severity"]
    service_name = params["service_name"]

    if symptom == "bad_release" or (symptom == "error_rate" and severity == "critical"):
        playbook_id = "rollback_release"
    elif symptom == "cpu":
        playbook_id = "scale_out_service"
    elif symptom == "latency":
        playbook_id = "restart_workers"
    else:
        playbook_id = "open_incident_ticket"

    plan = {
        "service_name": service_name,
        "recommended_playbook": playbook_id,
        "requires_human_approval": PLAYBOOKS[playbook_id]["requires_human_approval"],
        "reasoning": (
            f"Symptom '{symptom}' with severity '{severity}' for service '{service_name}'."
        ),
        "next_step": "request_approval" if PLAYBOOKS[playbook_id]["requires_human_approval"] else "execute_now",
    }
    record_audit_event({"tool": "plan_remediation", "arguments": params, "result": plan})
    return plan


def handle_execute_playbook(params: dict[str, Any]) -> dict[str, Any]:
    """Simulate executing an operational playbook."""
    playbook_id = params["playbook_id"]
    service_name = params["service_name"]
    approved_by = params.get("approved_by")

    playbook = PLAYBOOKS.get(playbook_id)
    if playbook is None:
        raise ValueError(f"Unknown playbook: {playbook_id}")

    if playbook["requires_human_approval"] and not approved_by:
        result = {
            "status": "pending_approval",
            "service_name": service_name,
            "playbook_id": playbook_id,
            "message": "High-impact playbook requires human approval.",
        }
    else:
        result = {
            "status": "executed",
            "service_name": service_name,
            "playbook_id": playbook_id,
            "approved_by": approved_by,
            "message": playbook["description"],
        }

    record_audit_event({"tool": "execute_playbook", "arguments": params, "result": result})
    return result


HANDLERS: dict[str, Any] = {
    "check_service_status": handle_check_service_status,
    "plan_remediation": handle_plan_remediation,
    "execute_playbook": handle_execute_playbook,
    "create_github_issue": handle_create_github_issue,
}


# ── Simplified JSON-RPC 2.0 Engine ──────────────────────────

def validate_parameters(tool_name: str, params: dict[str, Any]) -> list[str]:
    """Validate parameters against the tool input schema."""
    errors: list[str] = []
    for tool_def in TOOLS_REGISTRY:
        if tool_def["name"] == tool_name:
            schema = tool_def.get("inputSchema", {})
            required = schema.get("required", [])
            for field_name in required:
                if field_name not in params:
                    errors.append(f"Missing required field: '{field_name}'")
            break
    else:
        errors.append(f"Tool '{tool_name}' not found.")
    return errors


def process_request(req: dict[str, Any]) -> dict[str, Any]:
    """Process a JSON-RPC request and return the response."""
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_REGISTRY},
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        errors = validate_parameters(tool_name, arguments)
        if errors:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": "; ".join(errors)},
            }

        handler = HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Handler not implemented for '{tool_name}'",
                },
            }

        try:
            result = handler(arguments)
        except ValueError as error:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(error)},
            }
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: '{method}'"},
    }


# ── Main Loop (STDIO) ───────────────────────────────────────

def main() -> None:
    """Read JSON-RPC requests from STDIN and respond on STDOUT."""
    print("[MCP Server] Started. Waiting for requests over STDIN...", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Invalid JSON"},
            }
            print(json.dumps(resp, ensure_ascii=False))
            sys.stdout.flush()
            continue

        resp = process_request(req)
        print(json.dumps(resp, ensure_ascii=False))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
