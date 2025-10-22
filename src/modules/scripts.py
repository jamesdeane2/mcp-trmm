"""
Script execution tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List, Optional
from .client import TRMMClient


def get_tools():
    """Return list of script-related MCP tools"""
    return [
        {
            "name": "trmm_run_script",
            "description": "Run a script on a specific agent. The script must exist in the Script Library.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The agent ID to run the script on"
                    },
                    "script_id": {
                        "type": "integer",
                        "description": "The script ID from the Script Library (hover over script in UI to see ID)"
                    },
                    "args": {
                        "type": "array",
                        "description": "Array of command line arguments to pass to the script",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "env_vars": {
                        "type": "array",
                        "description": "Array of environment variables",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 90)",
                        "default": 90
                    },
                    "output": {
                        "type": "string",
                        "description": "Output handling: 'wait' to wait for results, 'forget' to run and forget, 'email' to email results",
                        "enum": ["wait", "forget", "email"],
                        "default": "wait"
                    },
                    "run_as_user": {
                        "type": "boolean",
                        "description": "Run as logged-in user instead of SYSTEM",
                        "default": False
                    },
                    "save_all_output": {
                        "type": "boolean",
                        "description": "Save all output to database",
                        "default": False
                    }
                },
                "required": ["agent_id", "script_id"]
            }
        },
        {
            "name": "trmm_run_command",
            "description": "Run an ad-hoc command or script code on a specific agent (test/execute endpoint)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The agent ID to run the command on"
                    },
                    "code": {
                        "type": "string",
                        "description": "The command or script code to execute"
                    },
                    "shell": {
                        "type": "string",
                        "description": "Shell to use: 'cmd', 'powershell', or 'python'",
                        "enum": ["cmd", "powershell", "python"],
                        "default": "powershell"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 90)",
                        "default": 90
                    },
                    "args": {
                        "type": "array",
                        "description": "Array of arguments",
                        "items": {"type": "string"},
                        "default": []
                    }
                },
                "required": ["agent_id", "code"]
            }
        }
    ]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle script-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_run_script":
        agent_id = arguments["agent_id"]
        payload = {
            "script": arguments["script_id"],
            "args": arguments.get("args", []),
            "env_vars": arguments.get("env_vars", []),
            "timeout": arguments.get("timeout", 90),
            "output": arguments.get("output", "wait"),
            "run_as_user": arguments.get("run_as_user", False),
            "save_all_output": arguments.get("save_all_output", False),
            "emails": [],
            "emailMode": "default",
            "custom_field": None
        }
        result = client.post(f"/agents/{agent_id}/runscript/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_run_command":
        agent_id = arguments["agent_id"]
        payload = {
            "code": arguments["code"],
            "shell": arguments.get("shell", "powershell"),
            "timeout": arguments.get("timeout", 90),
            "args": arguments.get("args", [])
        }
        result = client.post(f"/scripts/{agent_id}/test/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
