"""
Task management tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List, Optional
from .client import TRMMClient


def get_tools():
    """Return list of task-related MCP tools"""
    return [
        {
            "name": "trmm_list_tasks",
            "description": "List all automated tasks configured in Tactical RMM",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "trmm_create_collector_task",
            "description": "Create a new collector task that runs scripts and stores output in custom fields",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the task"
                    },
                    "policy": {
                        "type": "integer",
                        "description": "Policy ID to assign task to"
                    },
                    "script_id": {
                        "type": "integer",
                        "description": "Script ID to run"
                    },
                    "custom_field": {
                        "type": "integer",
                        "description": "Custom field ID to store the output"
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Type of task schedule",
                        "enum": ["daily", "weekly", "monthly", "runonce"],
                        "default": "daily"
                    },
                    "run_time_date": {
                        "type": "string",
                        "description": "Run time in ISO format (e.g., '2025-01-01T08:00:00Z')"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Script timeout in seconds",
                        "default": 90
                    },
                    "script_args": {
                        "type": "array",
                        "description": "Arguments to pass to the script",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "daily_interval": {
                        "type": "integer",
                        "description": "Interval for daily tasks (default: 1)",
                        "default": 1
                    },
                    "weekly_interval": {
                        "type": "integer",
                        "description": "Interval for weekly tasks (default: 1)",
                        "default": 1
                    },
                    "run_asap_after_missed": {
                        "type": "boolean",
                        "description": "Run task ASAP if missed",
                        "default": True
                    }
                },
                "required": ["name", "policy", "script_id", "custom_field", "run_time_date"]
            }
        },
        {
            "name": "trmm_get_task_results",
            "description": "Get task execution results for a specific agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The agent ID"
                    }
                },
                "required": ["agent_id"]
            }
        }
    ]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle task-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_list_tasks":
        result = client.get("/tasks/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_create_collector_task":
        payload = {
            "name": arguments["name"],
            "policy": arguments["policy"],
            "custom_field": arguments["custom_field"],
            "task_type": arguments.get("task_type", "daily"),
            "run_time_date": arguments["run_time_date"],
            "daily_interval": arguments.get("daily_interval", 1),
            "weekly_interval": arguments.get("weekly_interval", 1),
            "run_asap_after_missed": arguments.get("run_asap_after_missed", True),
            "alert_severity": "info",
            "assigned_check": None,
            "actions": [{
                "name": arguments["name"],
                "type": "script",
                "script": arguments["script_id"],
                "timeout": arguments.get("timeout", 90),
                "script_args": arguments.get("script_args", [])
            }]
        }
        result = client.post("/tasks/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_task_results":
        agent_id = arguments["agent_id"]
        result = client.get(f"/agents/{agent_id}/tasks/")
        return [{"type": "text", "text": str(result)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
