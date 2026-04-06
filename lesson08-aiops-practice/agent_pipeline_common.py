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
    return all(os.getenv(variable_name) for variable_name in FOUNDRY_REQUIRED_ENV_VARS)


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


def extract_agent_message(messages: Any) -> str:
    last_message = ""
    for message in messages:
        if getattr(message, "role", None) != "assistant":
            continue
        text_messages = getattr(message, "text_messages", None)
        if text_messages:
            last_message = text_messages[-1].text.value

    if not last_message:
        raise ValueError("Could not locate the agent text response.")
    return last_message


def run_foundry_json_agent(
    prompt: str,
    *,
    instructions: str,
    agent_name_env_var: str,
    default_agent_name: str,
) -> dict[str, Any]:
    from dotenv import load_dotenv

    load_dotenv(override=False)

    from azure.ai.agents.models import ListSortOrder
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    agent_name = os.getenv(agent_name_env_var, default_agent_name)

    if not project_endpoint or not model_name:
        raise ValueError(
            "Set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME to use Foundry mode."
        )

    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )
    agent = project_client.agents.create_agent(
        model=model_name,
        name=agent_name,
        instructions=instructions,
    )

    try:
        thread = project_client.agents.threads.create()
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )

        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        if run.status == "failed":
            raise RuntimeError(f"Agent execution failed: {run.last_error}")

        messages = project_client.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING,
        )
        response = parse_agent_json(extract_agent_message(messages))
        response["engine"] = "azure-ai-foundry"
        response["agent_name"] = agent.name
        response["run_status"] = run.status
        return response
    finally:
        project_client.agents.delete_agent(agent.id)