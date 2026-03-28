"""MCP server exposing observability tools for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel


class LogsSearchParams(BaseModel):
    query: str = "severity:ERROR",
    limit: int = 10
    time_range: str = "10m"


class LogsErrorCountParams(BaseModel):
    time_range: str = "10m"
    service: str = "Learning Management Service"


class TracesListParams(BaseModel):
    service: str = "Learning Management Service"
    limit: int = 10


class TracesGetParams(BaseModel):
    trace_id: str


async def logs_search(client: ObservabilityClient, args: LogsSearchParams) -> str:
    """Search VictoriaLogs using LogsQL query."""
    query = f"_time:{args.time_range} {args.query}"
    url = f"{client.logs_url}/select/logsql/query"
    
    async with httpx.AsyncClient() as http:
        response = await http.post(
            url,
            params={"query": query, "limit": args.limit},
            timeout=30.0
        )
        response.raise_for_status()
        return response.text


async def logs_error_count(client: ObservabilityClient, args: LogsErrorCountParams) -> dict:
    """Count errors per service over a time window."""
    query = f"_time:{args.time_range} service.name:\"{args.service}\" severity:ERROR"
    url = f"{client.logs_url}/select/logsql/query"
    
    async with httpx.AsyncClient() as http:
        response = await http.post(
            url,
            params={"query": query, "limit": 1000},
            timeout=30.0
        )
        response.raise_for_status()
        lines = response.text.strip().split("\n") if response.text else []
        return {"count": len(lines), "service": args.service, "time_range": args.time_range}


async def traces_list(client: ObservabilityClient, args: TracesListParams) -> str:
    """List recent traces for a service from VictoriaTraces."""
    url = f"{client.traces_url}/select/jaeger/api/traces"
    
    async with httpx.AsyncClient() as http:
        response = await http.get(
            url,
            params={"service": args.service, "limit": args.limit},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return json.dumps(data, indent=2)


async def traces_get(client: ObservabilityClient, args: TracesGetParams) -> str:
    """Fetch a specific trace by ID."""
    url = f"{client.traces_url}/select/jaeger/api/traces/{args.trace_id}"
    
    async with httpx.AsyncClient() as http:
        response = await http.get(url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data, indent=2)


class ObservabilityClient:
    def __init__(self, logs_url: str, traces_url: str):
        self.logs_url = logs_url
        self.traces_url = traces_url


def create_server(logs_url: str, traces_url: str) -> Server:
    server = Server("observability")
    client = ObservabilityClient(logs_url, traces_url)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="logs_search",
                description="Search VictoriaLogs using LogsQL query. Returns matching log entries.",
                inputSchema=LogsSearchParams.model_json_schema(),
            ),
            Tool(
                name="logs_error_count",
                description="Count errors for a service over a time window.",
                inputSchema=LogsErrorCountParams.model_json_schema(),
            ),
            Tool(
                name="traces_list",
                description="List recent traces for a service from VictoriaTraces.",
                inputSchema=TracesListParams.model_json_schema(),
            ),
            Tool(
                name="traces_get",
                description="Fetch a specific trace by ID. Returns full trace with spans.",
                inputSchema=TracesGetParams.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        handlers = {
            "logs_search": lambda args: logs_search(client, args),
            "logs_error_count": lambda args: logs_error_count(client, args),
            "traces_list": lambda args: traces_list(client, args),
            "traces_get": lambda args: traces_get(client, args),
        }
        handler = handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        try:
            if name == "logs_search":
                args = LogsSearchParams.model_validate(arguments or {})
            elif name == "logs_error_count":
                args = LogsErrorCountParams.model_validate(arguments or {})
            elif name == "traces_list":
                args = TracesListParams.model_validate(arguments or {})
            elif name == "traces_get":
                args = TracesGetParams.model_validate(arguments or {})
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            result = await handler(args)
            if isinstance(result, str):
                return [TextContent(type="text", text=result)]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    return server


async def main() -> None:
    import os
    logs_url = os.environ.get("VICTORIALOGS_URL", "http://localhost:9428")
    traces_url = os.environ.get("VICTORIATRACES_URL", "http://localhost:10428")
    
    server = create_server(logs_url, traces_url)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
