# Lesson 06 - Presentation Script

## Lesson Title

Tools and protocols for agents: connecting the agent to the real world through MCP.

## Learning Objective

By the end of this lesson, the class should understand:

1. Why agents need clear contracts to use tools.
2. How `tools/list` and `tools/call` organize discovery and execution.
3. How guardrails and auditing fit into the tooling layer.

## Lesson Application

Application demonstrated: local MCP server that checks service state, plans remediation, executes playbooks, and records an audit trail.

Main file: `mcp_server.py`

## Application Build Sequence

### Build 1 - Register tools and schemas

### Build 2 - Expose dynamic discovery

### Build 3 - Plan remediation

### Build 4 - Execute a playbook with approval

### Build 5 - Audit tool calls

### Build 6 - Agent client orchestration

Goal: demonstrate the full loop — a client discovers tools, orchestrates remediation, and executes through MCP.

## Demo Commands

```bash
python mcp_server.py
```

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

```bash
python mcp_agent_client.py --service fraud-api --mode auto --auto-approve --output artifacts/orchestration.json
python mcp_agent_client.py --service fraud-api --mode foundry-agent --auto-approve --output artifacts/orchestration-foundry.json
```

## Where To Apply This Knowledge

- IT support agents.
- Internal tools connected to LLMs.
- Integration of operational playbooks with governance.
