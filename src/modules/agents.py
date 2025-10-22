"""
Agent-related tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List, Optional
from .client import TRMMClient


def get_tools():
    """Return list of agent-related MCP tools"""
    return [
        {
            "name": "trmm_list_agents",
            "description": "List all agents in Tactical RMM. Can optionally include detailed information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "boolean",
                        "description": "Include detailed agent information (default: false)",
                        "default": False
                    }
                }
            }
        },
        {
            "name": "trmm_get_agent",
            "description": "Get detailed information about a specific agent by agent ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The agent ID to retrieve"
                    }
                },
                "required": ["agent_id"]
            }
        },
        {
            "name": "trmm_update_agent_custom_fields",
            "description": "Update custom field values for a specific agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The agent ID to update"
                    },
                    "custom_fields": {
                        "type": "array",
                        "description": "Array of custom field updates",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {
                                    "type": "integer",
                                    "description": "Custom field ID"
                                },
                                "string_value": {
                                    "type": "string",
                                    "description": "Value to set"
                                }
                            },
                            "required": ["field", "string_value"]
                        }
                    }
                },
                "required": ["agent_id", "custom_fields"]
            }
        },
        {
            "name": "trmm_get_agent_tasks",
            "description": "Get all tasks configured for a specific agent",
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
    """Handle agent-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_list_agents":
        detail = arguments.get("detail", False)
        params = {"detail": "true" if detail else "false"}
        result = client.get("/agents/", params=params)
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_agent":
        agent_id = arguments["agent_id"]
        result = client.get(f"/agents/{agent_id}/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_update_agent_custom_fields":
        agent_id = arguments["agent_id"]
        custom_fields = arguments["custom_fields"]
        payload = {"custom_fields": custom_fields}
        result = client.put(f"/agents/{agent_id}/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_agent_tasks":
        agent_id = arguments["agent_id"]
        result = client.get(f"/agents/{agent_id}/tasks/")
        return [{"type": "text", "text": str(result)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
