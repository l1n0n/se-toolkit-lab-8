#!/usr/bin/env python3
"""
Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then execs into `nanobot gateway`.
"""

import json
import os
import sys
from pathlib import Path


def resolve_config() -> str:
    """Read config.json, override fields from env vars, write config.resolved.json."""
    config_path = Path(__file__).parent / "config.json"
    # Write resolved config to /tmp to avoid permission issues in Docker
    resolved_path = Path("/tmp/nanobot-config.resolved.json")

    with open(config_path) as f:
        config = json.load(f)

    # Override LLM provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base = os.environ.get("LLM_API_BASE_URL")
    llm_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base:
        config["providers"]["custom"]["apiBase"] = llm_api_base
    if llm_model:
        config["agents"]["defaults"]["model"] = llm_model

    # Override gateway settings
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if "gateway" not in config:
        config["gateway"] = {}
    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Override MCP LMS server env vars
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}
    if "lms" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["lms"] = {
            "command": "python",
            "args": ["-m", "mcp_lms"],
        }
    if "env" not in config["tools"]["mcpServers"]["lms"]:
        config["tools"]["mcpServers"]["lms"]["env"] = {}

    if lms_backend_url:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Override webchat channel settings
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")

    if webchat_host or webchat_port:
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["enabled"] = True
        if webchat_host:
            config["channels"]["webchat"]["host"] = webchat_host
        if webchat_port:
            config["channels"]["webchat"]["port"] = int(webchat_port)

    # Configure mcp_webchat MCP server for structured UI
    # The webchat UI relay URL is the internal URL the MCP server uses to send UI messages
    # Token is the access key for authentication
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY")
    webchat_container_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765")

    if "mcp_webchat" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["mcp_webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {},
        }
    if "env" not in config["tools"]["mcpServers"]["mcp_webchat"]:
        config["tools"]["mcpServers"]["mcp_webchat"]["env"] = {}

    # Set the UI relay URL (internal Docker network) and token
    config["tools"]["mcpServers"]["mcp_webchat"]["env"]["NANOBOT_WEBCCHAT_UI_RELAY_URL"] = f"http://localhost:{webchat_container_port}"
    if nanobot_access_key:
        config["tools"]["mcpServers"]["mcp_webchat"]["env"]["NANOBOT_WEBCCHAT_UI_TOKEN"] = nanobot_access_key

    # Configure mcp_obs MCP server for observability tools
    victorialogs_port = os.environ.get("CONST_VICTORIALOGS_CONTAINER_PORT", "9428")
    victoriatraces_port = os.environ.get("CONST_VICTORIATRACES_CONTAINER_PORT", "10428")

    if "mcp_obs" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["mcp_obs"] = {
            "command": "python",
            "args": ["-m", "mcp_obs"],
            "env": {},
        }
    if "env" not in config["tools"]["mcpServers"]["mcp_obs"]:
        config["tools"]["mcpServers"]["mcp_obs"]["env"] = {}

    # Set VictoriaLogs and VictoriaTraces URLs (internal Docker network)
    config["tools"]["mcpServers"]["mcp_obs"]["env"]["VICTORIALOGS_URL"] = f"http://victorialogs:{victorialogs_port}"
    config["tools"]["mcpServers"]["mcp_obs"]["env"]["VICTORIATRACES_URL"] = f"http://victoriatraces:{victoriatraces_port}"

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    return str(resolved_path)


def main():
    """Resolve config and exec into nanobot gateway."""
    # Use /tmp for workspace to avoid permission issues with bind-mounted volumes
    workspace_dir = Path("/tmp/nanobot-workspace")
    resolved_config = resolve_config()

    # Copy workspace contents from /app/nanobot/workspace to /tmp
    src_workspace = Path(__file__).parent / "workspace"
    if src_workspace.exists():
        import shutil
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        shutil.copytree(src_workspace, workspace_dir)

    # Create necessary directories in workspace for cron and memory
    cron_dir = workspace_dir / "cron"
    memory_dir = workspace_dir / "memory"
    cron_dir.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)

    print(f"Using config: {resolved_config}", file=sys.stderr)
    print(f"Workspace: {workspace_dir}", file=sys.stderr)

    # Exec into nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_config, "--workspace", str(workspace_dir)])


if __name__ == "__main__":
    main()
