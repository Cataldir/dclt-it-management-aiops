"""
Aula 06 – Ferramentas e Protocolos para Agentes de IA (MCP)
============================================================
Servidor MCP simplificado que expõe ferramentas para um agente de IA
segundo o Model Context Protocol. Demonstra:

  - Registro de ferramentas com JSON Schema
  - Descoberta dinâmica de capacidades (tools/list)
  - Invocação estruturada (tools/call)
  - Validação de parâmetros contra o schema

Este exemplo usa JSON-RPC 2.0 sobre STDIO, conforme a especificação MCP.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


# ── Registro de ferramentas ──────────────────────────────────

TOOLS_DIR = Path(__file__).parent

def carregar_definicoes_ferramentas() -> list[dict[str, Any]]:
    """Carrega definições de ferramentas a partir de arquivos JSON."""
    ferramentas: list[dict[str, Any]] = []
    for arquivo in TOOLS_DIR.glob("tool_*.json"):
        with open(arquivo, encoding="utf-8") as f:
            ferramentas.append(json.load(f))
    return ferramentas


TOOLS_REGISTRY = carregar_definicoes_ferramentas()


# ── Handlers de ferramentas ──────────────────────────────────

def handler_criar_issue_github(params: dict[str, Any]) -> dict[str, Any]:
    """Simula a criação de uma issue no GitHub."""
    repo = params["repo"]
    title = params["title"]
    body = params.get("body", "")
    print(f"[MCP] Criando issue no repo '{repo}': {title}", file=sys.stderr)
    return {
        "issue_url": f"https://github.com/{repo}/issues/42",
        "title": title,
        "body": body,
        "status": "created",
    }


HANDLERS: dict[str, Any] = {
    "criar_issue_github": handler_criar_issue_github,
}


# ── Motor JSON-RPC 2.0 simplificado ─────────────────────────

def validar_parametros(tool_name: str, params: dict[str, Any]) -> list[str]:
    """Valida parâmetros contra o inputSchema da ferramenta."""
    erros: list[str] = []
    for tool_def in TOOLS_REGISTRY:
        if tool_def["name"] == tool_name:
            schema = tool_def.get("inputSchema", {})
            required = schema.get("required", [])
            for campo in required:
                if campo not in params:
                    erros.append(f"Campo obrigatório ausente: '{campo}'")
            break
    else:
        erros.append(f"Ferramenta '{tool_name}' não encontrada.")
    return erros


def processar_requisicao(req: dict[str, Any]) -> dict[str, Any]:
    """Processa uma requisição JSON-RPC e retorna a resposta."""
    metodo = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if metodo == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_REGISTRY},
        }

    if metodo == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        erros = validar_parametros(tool_name, arguments)
        if erros:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": "; ".join(erros)},
            }

        handler = HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Handler não implementado para '{tool_name}'",
                },
            }

        resultado = handler(arguments)
        return {"jsonrpc": "2.0", "id": req_id, "result": resultado}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Método desconhecido: '{metodo}'"},
    }


# ── Loop principal (STDIO) ──────────────────────────────────

def main() -> None:
    """Lê requisições JSON-RPC de STDIN e responde em STDOUT."""
    print("[MCP Server] Iniciado. Aguardando requisições via STDIN...", file=sys.stderr)

    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            req = json.loads(linha)
        except json.JSONDecodeError:
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "JSON inválido"},
            }
            print(json.dumps(resp, ensure_ascii=False))
            sys.stdout.flush()
            continue

        resp = processar_requisicao(req)
        print(json.dumps(resp, ensure_ascii=False))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
