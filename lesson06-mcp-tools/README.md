# Lesson 06 - MCP Server for AI Operations

## Overview

This module demonstrates how to expose operational capabilities to agents through MCP. The server lists tools, validates arguments, records local audit events, and shows how structured contracts reduce ambiguity between agent and environment.

## What You Will Practice

- Dynamic tool discovery with `tools/list`.
- Structured tool invocation with `tools/call`.
- Playbook planning and execution with guardrails.
- Local auditing of executed actions.

## Technologies

- Python 3.13
- JSON-RPC 2.0
- Simplified JSON Schema
- Model Context Protocol
- Azure AI Foundry through `azure-ai-projects`

## Prerequisites

- Python 3.13
- `uv`

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation.
- `pyproject.toml`: lesson-local UV project definition.
- `mcp_server.py`: local MCP server.
- `mcp_agent_client.py`: agent client that discovers tools and orchestrates remediation.
- `foundry_helper.py`: shared Foundry agent helper.
- `.env.example`: environment variables for Azure AI Foundry integration.
- `tool_*.json`: exposed tool definitions.

## Quick Start

```bash
uv sync --python 3.13
uv run python mcp_server.py
```

Example STDIN request:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

### MCP Agent Client

Run the agent client to automatically discover tools and orchestrate a remediation flow:

```bash
uv run python mcp_agent_client.py --service fraud-api --mode auto --auto-approve --output artifacts/orchestration.json
```

The client starts the MCP server as a subprocess, lists tools, then runs _check status → plan → execute_ using local policy or a Foundry-driven orchestration strategy.

## Available Tools

- `check_service_status`
- `plan_remediation`
- `execute_playbook`
- `create_github_issue`

## Supporting Files

- See `LESSON_SCRIPT.md` for lesson delivery.
- See `docs/README.md` for architecture, usage, and troubleshooting.

## Where To Apply This Knowledge

- Internal support and operations agents.
- Safe integration between LLMs and enterprise tools.
- AgentOps with an auditable trail.

## Connection To The Track

- Lesson 05 provides the operational context.
- Lesson 08 can consume the same playbooks and contracts.
- The MCP agent client shows the full loop: tool discovery, orchestration, and execution using the same Foundry pattern from Lessons 02–05 and 08.

## Important Note

This server is educational. In a real environment, add authentication, authorization, durable storage, and more complete structural validation.
