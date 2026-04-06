# Lesson 06 - MCP Server for AI Operations

## Overview

This module demonstrates how to expose operational capabilities to agents through MCP. The server lists tools, validates arguments, records local audit events, and shows how structured contracts reduce ambiguity between agent and environment.

## What You Will Practice

- Dynamic tool discovery with `tools/list`.
- Structured tool invocation with `tools/call`.
- Playbook planning and execution with guardrails.
- Local auditing of executed actions.

## Technologies

- Python 3.11+
- JSON-RPC 2.0
- Simplified JSON Schema
- Model Context Protocol

## Prerequisites

- Python 3.11+

## Module Structure

- `README.md`: quick guide for the module.
- `LESSON_SCRIPT.md`: lesson script / presentation guide.
- `docs/README.md`: supporting documentation.
- `mcp_server.py`: local MCP server.
- `tool_*.json`: exposed tool definitions.

## Quick Start

```bash
python mcp_server.py
```

Example STDIN request:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

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

## Important Note

This server is educational. In a real environment, add authentication, authorization, durable storage, and more complete structural validation.
