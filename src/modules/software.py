"""
Software inventory tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List
from .client import TRMMClient


def _filter_agents(agents: List[Dict], arguments: Dict[str, Any]) -> List[Dict]:
    """Helper function to filter agents based on arguments"""
    filtered = agents
    
    # Filter by client_name (case-insensitive)
    if "client_name" in arguments and arguments["client_name"]:
        client_name_filter = arguments["client_name"].lower()
        filtered = [
            agent for agent in filtered 
            if agent.get("client_name", "").lower() == client_name_filter
        ]
    
    # Filter by site_name (case-insensitive)
    if "site_name" in arguments and arguments["site_name"]:
        site_name_filter = arguments["site_name"].lower()
        filtered = [
            agent for agent in filtered 
            if agent.get("site_name", "").lower() == site_name_filter
        ]
    
    # Filter by status
    if "status" in arguments and arguments["status"]:
        status_filter = arguments["status"].lower()
        filtered = [
            agent for agent in filtered 
            if agent.get("status", "").lower() == status_filter
        ]
    
    # Filter by monitoring_type
    if "monitoring_type" in arguments and arguments["monitoring_type"]:
        monitoring_type_filter = arguments["monitoring_type"].lower()
        filtered = [
            agent for agent in filtered 
            if agent.get("monitoring_type", "").lower() == monitoring_type_filter
        ]
    
    return filtered


def get_tools():
    """Return list of software-related MCP tools"""
    return [
        {
            "name": "trmm_get_agent_software",
            "description": "Get list of installed software on a specific agent",
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
        },
        {
            "name": "trmm_refresh_agent_software",
            "description": "Refresh the software inventory for a specific agent",
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
        },
        {
            "name": "trmm_get_all_software",
            "description": "Get software inventory for all agents (warning: may be large dataset). Can filter by client, site, status, or monitoring type.",
            "inputSchema": {
                "type": "object",
                "properties": {
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
            "name": "trmm_refresh_all_software",
            "description": "Refresh software inventory for all agents (use with caution on large deployments). Can filter by client, site, status, or monitoring type.",
            "inputSchema": {
                "type": "object",
                "properties": {
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
                        "description": "Filter by agent status (optional, default: online)",
                        "enum": ["online", "offline"],
                        "default": "online"
                    },
                    "monitoring_type": {
                        "type": "string",
                        "description": "Filter by monitoring type (optional)",
                        "enum": ["workstation", "server"]
                    }
                }
            }
        }
    ]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle software-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_get_agent_software":
        agent_id = arguments["agent_id"]
        result = client.get(f"/software/{agent_id}/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_refresh_agent_software":
        agent_id = arguments["agent_id"]
        result = client.put(f"/software/{agent_id}/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_all_software":
        # Get all agents with details for filtering
        agents = client.get("/agents/", params={"detail": "true"})
        
        # Apply filters
        filtered_agents = _filter_agents(agents, arguments)
        
        all_software = []
        for agent in filtered_agents:
            try:
                software = client.get(f"/software/{agent['agent_id']}/")
                # Only include essential agent fields, software list can stay full
                all_software.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "client_name": agent.get("client_name", "unknown"),
                    "site_name": agent.get("site_name", "unknown"),
                    "software_count": len(software) if isinstance(software, list) else 0,
                    "software": software
                })
            except Exception as e:
                all_software.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "client_name": agent.get("client_name", "unknown"),
                    "site_name": agent.get("site_name", "unknown"),
                    "error": str(e)
                })
        
        response = {
            "total_agents": len(agents),
            "filtered_agents": len(filtered_agents),
            "filters_applied": {
                k: v for k, v in arguments.items() 
                if k in ["client_name", "site_name", "status", "monitoring_type"] and v
            },
            "software_data": all_software
        }
        
        return [{"type": "text", "text": str(response)}]
    
    elif name == "trmm_refresh_all_software":
        # Get all agents with details for filtering
        agents = client.get("/agents/", params={"detail": "true"})
        
        # Apply filters (default to online agents)
        if "status" not in arguments:
            arguments["status"] = "online"
        filtered_agents = _filter_agents(agents, arguments)
        
        results = []
        for agent in filtered_agents:
            try:
                result = client.put(f"/software/{agent['agent_id']}/")
                # Only include essential fields and refresh status
                results.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "client_name": agent.get("client_name", "unknown"),
                    "site_name": agent.get("site_name", "unknown"),
                    "refresh_status": "success"
                })
            except Exception as e:
                results.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "client_name": agent.get("client_name", "unknown"),
                    "site_name": agent.get("site_name", "unknown"),
                    "refresh_status": "failed",
                    "error": str(e)
                })
        
        response = {
            "total_agents": len(agents),
            "filtered_agents": len(filtered_agents),
            "refreshed_agents": len(results),
            "filters_applied": {
                k: v for k, v in arguments.items() 
                if k in ["client_name", "site_name", "status", "monitoring_type"] and v
            },
            "results": results
        }
        
        return [{"type": "text", "text": str(response)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
