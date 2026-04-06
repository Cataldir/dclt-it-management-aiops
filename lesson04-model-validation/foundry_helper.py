"""Shared Foundry agent helper for Lesson 04.

Uses the azure-ai-projects >= 2.0.0 Responses-based Agent API.
See https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme
"""

from __future__ import annotations

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


def run_foundry_json_agent(
    prompt: str,
    *,
    instructions: str,
    agent_name_env_var: str,
    default_agent_name: str,
) -> dict[str, Any]:
    from dotenv import load_dotenv

    load_dotenv(override=False)

    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import PromptAgentDefinition
    from azure.identity import DefaultAzureCredential

    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    agent_name = os.getenv(agent_name_env_var, default_agent_name)

    if not project_endpoint or not model_name:
        raise ValueError(
            "Set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME to use Foundry mode."
        )

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model_name,
                instructions=instructions,
            ),
        )

        conversation_id: str | None = None
        try:
            conversation = openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}],
            )
            conversation_id = conversation.id
            response = openai_client.responses.create(
                conversation=conversation_id,
                extra_body={
                    "agent_reference": {"name": agent.name, "type": "agent_reference"},
                },
            )
            result = parse_agent_json(response.output_text)
            result["engine"] = "azure-ai-foundry"
            result["agent_name"] = agent.name
            result["agent_version"] = agent.version
            return result
        finally:
            if conversation_id is not None:
                openai_client.conversations.delete(conversation_id=conversation_id)
            project_client.agents.delete_version(
                agent_name=agent.name, agent_version=agent.version,
            )
