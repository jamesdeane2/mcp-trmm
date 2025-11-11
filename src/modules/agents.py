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
            "description": "List all agents in Tactical RMM. Can optionally include detailed information and filter by client, site, status, or monitoring type.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "boolean",
                        "description": "Include detailed agent information (default: false)",
                        "default": False
                    },
                    "client_name": {
                        "type": "string",
                        "description": "Filter by client name (optional)"
                    },
                    "site_name": {
                        "type": "string",
                        "description": "Filter by site name (optional)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by agent status (optional)",
                        "enum": ["online", "offline"]
                    },
                    "monitoring_type": {
                        "type": "string",
                        "description": "Filter by monitoring type (optional)",
                        "enum": ["workstation", "server"]
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
        
        # Apply filters if provided
        filtered_result = result
        
        # Filter by client_name (case-insensitive)
        if "client_name" in arguments and arguments["client_name"]:
            client_name_filter = arguments["client_name"].lower()
            filtered_result = [
                agent for agent in filtered_result 
                if agent.get("client_name", "").lower() == client_name_filter
            ]
        
        # Filter by site_name (case-insensitive)
        if "site_name" in arguments and arguments["site_name"]:
            site_name_filter = arguments["site_name"].lower()
            filtered_result = [
                agent for agent in filtered_result 
                if agent.get("site_name", "").lower() == site_name_filter
            ]
        
        # Filter by status
        if "status" in arguments and arguments["status"]:
            status_filter = arguments["status"].lower()
            filtered_result = [
                agent for agent in filtered_result 
                if agent.get("status", "").lower() == status_filter
            ]
        
        # Filter by monitoring_type
        if "monitoring_type" in arguments and arguments["monitoring_type"]:
            monitoring_type_filter = arguments["monitoring_type"].lower()
            filtered_result = [
                agent for agent in filtered_result 
                if agent.get("monitoring_type", "").lower() == monitoring_type_filter
            ]
        
        # Reduce returned fields to essentials only
        essential_fields = [
            "agent_id", "hostname", "client_name", "site_name", 
            "operating_system", "plat", "status", "monitoring_type",
            "last_seen", "needs_reboot"
        ]
        
        simplified_agents = []
        for agent in filtered_result:
            simplified = {k: agent.get(k) for k in essential_fields if k in agent}
            simplified_agents.append(simplified)
        
        # Return summary with filter info
        response = {
            "total_agents": len(result),
            "filtered_agents": len(filtered_result),
            "filters_applied": {
                k: v for k, v in arguments.items() 
                if k in ["client_name", "site_name", "status", "monitoring_type"] and v
            },
            "agents": simplified_agents
        }
        
        return [{"type": "text", "text": str(response)}]
    
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
