#!/usr/bin/env python3
"""
Servidor MCP para SonarQube
Permite acesso às funcionalidades do SonarQube via Model Context Protocol
"""
import asyncio
import json
import os
import sys
from typing import Any, Optional
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuração via variáveis de ambiente
SONARQUBE_URL = os.environ.get("SONARQUBE_URL", "")
SONARQUBE_TOKEN = os.environ.get("SONARQUBE_TOKEN", "")

if not SONARQUBE_URL or not SONARQUBE_TOKEN:
    print("ERRO: SONARQUBE_URL e SONARQUBE_TOKEN devem ser configurados", file=sys.stderr)
    print("Configure as variáveis de ambiente antes de executar o servidor", file=sys.stderr)
    sys.exit(1)

# Criar instância do servidor MCP
server = Server("sonarqube-mcp-server")

def make_sonarqube_request(endpoint: str, params: Optional[dict] = None) -> dict:
    """
    Faz uma requisição autenticada à API do SonarQube
    """
    url = f"{SONARQUBE_URL.rstrip('/')}/api/{endpoint.lstrip('/')}"
    headers = {"Accept": "application/json"}
    auth = (SONARQUBE_TOKEN, "")
    
    try:
        response = requests.get(url, params=params or {}, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lista todas as ferramentas disponíveis"""
    return [
        Tool(
            name="search_issues",
            description="Busca issues do SonarQube em projetos. Pode filtrar por projeto, severidade e status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectKeys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de chaves de projetos (ex: ['com.thomsonreuters:rt-data-scanner'])"
                    },
                    "severities": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]},
                        "description": "Filtrar por severidade"
                    },
                    "statuses": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["OPEN", "CONFIRMED", "REOPENED", "RESOLVED", "CLOSED"]},
                        "description": "Filtrar por status"
                    },
                    "pageSize": {
                        "type": "integer",
                        "description": "Tamanho da página (padrão: 100, máximo: 500)",
                        "default": 100
                    },
                    "page": {
                        "type": "integer",
                        "description": "Número da página (padrão: 1)",
                        "default": 1
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_project_measures",
            description="Obtém métricas de um projeto do SonarQube (cobertura, complexidade, linhas de código, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectKey": {
                        "type": "string",
                        "description": "Chave do projeto (ex: 'com.thomsonreuters:rt-data-scanner')"
                    },
                    "metricKeys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de métricas a buscar (ex: ['coverage', 'ncloc', 'complexity', 'violations'])",
                        "default": ["coverage", "ncloc", "complexity", "violations", "code_smells", "bugs", "vulnerabilities"]
                    }
                },
                "required": ["projectKey"]
            }
        ),
        Tool(
            name="get_quality_gate_status",
            description="Obtém o status do Quality Gate de um projeto",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectKey": {
                        "type": "string",
                        "description": "Chave do projeto"
                    }
                },
                "required": ["projectKey"]
            }
        ),
        Tool(
            name="list_projects",
            description="Lista todos os projetos disponíveis no SonarQube",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Número da página",
                        "default": 1
                    }
                }
            }
        ),
        Tool(
            name="get_project_issues_summary",
            description="Obtém um resumo das issues de um projeto agrupadas por severidade",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectKey": {
                        "type": "string",
                        "description": "Chave do projeto"
                    }
                },
                "required": ["projectKey"]
            }
        ),
        Tool(
            name="ping_sonarqube",
            description="Verifica se o servidor SonarQube está acessível",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Executa uma ferramenta"""
    
    if name == "ping_sonarqube":
        result = make_sonarqube_request("system/status")
        if "error" in result:
            return [TextContent(type="text", text=f"Erro ao conectar: {result['error']}")]
        return [TextContent(type="text", text=f"SonarQube está acessível. Status: {result.get('status', 'UNKNOWN')}")]
    
    elif name == "list_projects":
        page = arguments.get("page", 1)
        result = make_sonarqube_request("projects/search", {"p": page})
        if "error" in result:
            return [TextContent(type="text", text=f"Erro: {result['error']}")]
        
        projects = result.get("components", [])
        output = f"Total de projetos: {result.get('paging', {}).get('total', 0)}\n\n"
        for project in projects:
            output += f"- {project.get('key', 'N/A')}: {project.get('name', 'N/A')}\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "search_issues":
        params = {
            "ps": arguments.get("pageSize", 100),
            "p": arguments.get("page", 1)
        }
        
        if project_keys := arguments.get("projectKeys"):
            params["componentKeys"] = ",".join(project_keys)
        
        if severities := arguments.get("severities"):
            params["severities"] = ",".join(severities)
        
        if statuses := arguments.get("statuses"):
            params["statuses"] = ",".join(statuses)
        
        result = make_sonarqube_request("issues/search", params)
        if "error" in result:
            return [TextContent(type="text", text=f"Erro: {result['error']}")]
        
        issues = result.get("issues", [])
        total = result.get("total", 0)
        paging = result.get("paging", {})
        
        output = f"Total de issues: {total}\n"
        output += f"Página {paging.get('pageIndex', 1)} de {paging.get('total', 1)}\n"
        output += f"Issues nesta página: {len(issues)}\n\n"
        
        # Agrupar por severidade
        by_severity = {}
        for issue in issues:
            severity = issue.get("severity", "UNKNOWN")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        for severity in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]:
            if severity in by_severity:
                output += f"\n{severity}: {len(by_severity[severity])} issues\n"
                for issue in by_severity[severity][:5]:  # Mostrar apenas as 5 primeiras
                    text_range = issue.get("textRange", {})
                    location = f"Linha {text_range.get('startLine', '?')}" if text_range else "N/A"
                    output += f"  - {issue.get('message', 'N/A')[:80]}...\n"
                    output += f"    Componente: {issue.get('component', 'N/A')}\n"
                    output += f"    Localização: {location}\n"
                    output += f"    Status: {issue.get('status', 'N/A')}\n"
                if len(by_severity[severity]) > 5:
                    output += f"  ... e mais {len(by_severity[severity]) - 5} issues\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "get_project_measures":
        project_key = arguments.get("projectKey")
        metric_keys = arguments.get("metricKeys", ["coverage", "ncloc", "complexity", "violations", "code_smells", "bugs", "vulnerabilities"])
        
        params = {
            "component": project_key,
            "metricKeys": ",".join(metric_keys)
        }
        
        result = make_sonarqube_request("measures/component", params)
        if "error" in result:
            return [TextContent(type="text", text=f"Erro: {result['error']}")]
        
        component = result.get("component", {})
        measures = component.get("measures", [])
        
        output = f"Métricas do projeto: {project_key}\n\n"
        for measure in measures:
            metric = measure.get("metric", "N/A")
            value = measure.get("value", "N/A")
            output += f"{metric}: {value}\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "get_quality_gate_status":
        project_key = arguments.get("projectKey")
        result = make_sonarqube_request("qualitygates/project_status", {"projectKey": project_key})
        if "error" in result:
            return [TextContent(type="text", text=f"Erro: {result['error']}")]
        
        status = result.get("status", "UNKNOWN")
        conditions = result.get("conditions", [])
        
        output = f"Quality Gate Status: {status}\n\n"
        output += "Condições:\n"
        for condition in conditions:
            metric = condition.get("metricKey", "N/A")
            cond_status = condition.get("status", "N/A")
            actual = condition.get("actualValue", "N/A")
            threshold = condition.get("errorThreshold", "N/A")
            output += f"  {metric}: {cond_status} (Atual: {actual}, Limite: {threshold})\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "get_project_issues_summary":
        project_key = arguments.get("projectKey")
        result = make_sonarqube_request("issues/search", {
            "componentKeys": project_key,
            "ps": 500
        })
        
        if "error" in result:
            return [TextContent(type="text", text=f"Erro: {result['error']}")]
        
        issues = result.get("issues", [])
        total = result.get("total", 0)
        
        by_severity = {}
        by_status = {}
        
        for issue in issues:
            severity = issue.get("severity", "UNKNOWN")
            status = issue.get("status", "UNKNOWN")
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        output = f"Resumo de Issues - {project_key}\n"
        output += f"Total: {total}\n\n"
        
        output += "Por Severidade:\n"
        for severity in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]:
            count = by_severity.get(severity, 0)
            if count > 0:
                output += f"  {severity}: {count}\n"
        
        output += "\nPor Status:\n"
        for status in ["OPEN", "CONFIRMED", "REOPENED", "RESOLVED", "CLOSED"]:
            count = by_status.get(status, 0)
            if count > 0:
                output += f"  {status}: {count}\n"
        
        return [TextContent(type="text", text=output)]
    
    else:
        return [TextContent(type="text", text=f"Ferramenta desconhecida: {name}")]

async def main():
    """Função principal do servidor"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

def entry_point():
    """Entry point para execução via uvx"""
    asyncio.run(main())

if __name__ == "__main__":
    entry_point()
