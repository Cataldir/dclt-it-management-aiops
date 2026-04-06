# Docs - Lesson 06

## Module Architecture

The module uses JSON-RPC over STDIN/STDOUT to demonstrate the MCP flow. Tool definitions live in separate JSON files, while validation and execution logic stays in the Python server.

## Artifacts And Outputs

- `tools/list` and `tools/call` responses.
- Local JSONL audit trail.
- Playbook plans and executions.
- Agent-backed orchestration report (via `mcp_agent_client.py`).

## Where To Apply It

- Enterprise agents with internal tools.
- Approval controls for sensitive actions.
- Contracts between the model and the operational backend.
- Full-loop demonstration: tool discovery, agent orchestration, and audited execution.

## Quick Troubleshooting

- Send one JSON line at a time to STDIN.
- If a tool fails, check the tool name and the required fields in its schema.
- If the MCP agent client falls back to local mode, check whether `.env` contains the Foundry environment variables.
