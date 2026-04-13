"""Shared Foundry agent helper for Lesson 02.

Uses the Microsoft Agent Framework SDK (agent-framework-azure-ai).
See https://learn.microsoft.com/azure/ai-foundry/agents/
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any


FOUNDRY_REQUIRED_ENV_VARS = (
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_MODEL_DEPLOYMENT_NAME",
)

NORMALIZED_MODES = ("auto", "local-policy", "foundry-agent")
MODE_ALIASES = {
    "local": "local-policy",
    "foundry": "foundry-agent",
}
CLI_MODE_CHOICES = (*NORMALIZED_MODES, *MODE_ALIASES.keys())


def foundry_is_configured() -> bool:
    from dotenv import load_dotenv

    load_dotenv(override=False)
    return all(os.getenv(v) for v in FOUNDRY_REQUIRED_ENV_VARS)


def normalize_mode(mode: str) -> str:
    normalized = MODE_ALIASES.get(mode, mode)
    if normalized not in NORMALIZED_MODES:
        expected = ", ".join(NORMALIZED_MODES)
        raise ValueError(f"Unsupported mode '{mode}'. Expected one of: {expected}")
    return normalized


def parse_agent_json(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Agent response does not contain valid JSON.")
    return json.loads(stripped[start : end + 1])


async def _run_foundry_agent_async(
    prompt: str,
    *,
    instructions: str,
    agent_name: str,
    project_endpoint: str,
    model_name: str,
) -> dict[str, Any]:
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
                Message("system", [instructions]),
                Message("user", [prompt]),
            ])
            result = parse_agent_json(response.text)
            result["engine"] = "azure-ai-foundry"
            result["agent_name"] = agent_name
            return result
        finally:
            await client.close()


def run_foundry_json_agent(
    prompt: str,
    *,
    instructions: str,
    agent_name_env_var: str,
    default_agent_name: str,
) -> dict[str, Any]:
    from dotenv import load_dotenv

    load_dotenv(override=False)

    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    agent_name = os.getenv(agent_name_env_var, default_agent_name)

    if not project_endpoint or not model_name:
        raise ValueError(
            "Set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME to use Foundry mode."
        )

    return asyncio.run(
        _run_foundry_agent_async(
            prompt,
            instructions=instructions,
            agent_name=agent_name,
            project_endpoint=project_endpoint,
            model_name=model_name,
        )
    )
