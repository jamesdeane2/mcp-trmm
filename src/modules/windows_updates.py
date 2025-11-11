"""
Windows Update tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List
from .client import TRMMClient


def get_tools():
    """Return list of Windows Update-related MCP tools"""
    return [
        {
            "name": "trmm_scan_windows_updates",
            "description": "Trigger a Windows Update scan on a specific agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The agent ID to scan for updates"
                    }
                },
                "required": ["agent_id"]
            }
        },
        {
            "name": "trmm_scan_all_agents_updates",
            "description": "Trigger Windows Update scans on all agents (use with caution on large deployments). Can filter by client, site, status, or monitoring type.",
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
    """Handle Windows Update-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_scan_windows_updates":
        agent_id = arguments["agent_id"]
        result = client.post(f"/winupdate/{agent_id}/scan/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_scan_all_agents_updates":
        # Get all agents with details for filtering
        agents = client.get("/agents/", params={"detail": "true"})
        
        # Apply filters
        filtered_agents = agents
        
        # Filter by client_name (case-insensitive)
        if "client_name" in arguments and arguments["client_name"]:
            client_name_filter = arguments["client_name"].lower()
            filtered_agents = [
                agent for agent in filtered_agents 
                if agent.get("client_name", "").lower() == client_name_filter
            ]
        
        # Filter by site_name (case-insensitive)
        if "site_name" in arguments and arguments["site_name"]:
            site_name_filter = arguments["site_name"].lower()
            filtered_agents = [
                agent for agent in filtered_agents 
                if agent.get("site_name", "").lower() == site_name_filter
            ]
        
        # Filter by status (default to online)
        status_filter = arguments.get("status", "online").lower()
        filtered_agents = [
            agent for agent in filtered_agents 
            if agent.get("status", "").lower() == status_filter
        ]
        
        # Filter by monitoring_type
        if "monitoring_type" in arguments and arguments["monitoring_type"]:
            monitoring_type_filter = arguments["monitoring_type"].lower()
            filtered_agents = [
                agent for agent in filtered_agents 
                if agent.get("monitoring_type", "").lower() == monitoring_type_filter
            ]
        
        results = []
        for agent in filtered_agents:
            try:
                result = client.post(f"/winupdate/{agent['agent_id']}/scan/")
                # Only include essential fields and scan status
                results.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "client_name": agent.get("client_name", "unknown"),
                    "site_name": agent.get("site_name", "unknown"),
                    "scan_status": "success"
                })
            except Exception as e:
                results.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "client_name": agent.get("client_name", "unknown"),
                    "site_name": agent.get("site_name", "unknown"),
                    "scan_status": "failed",
                    "error": str(e)
                })
        
        response = {
            "total_agents": len(agents),
            "filtered_agents": len(filtered_agents),
            "scanned_agents": len(results),
            "filters_applied": {
                k: v for k, v in arguments.items() 
                if k in ["client_name", "site_name", "status", "monitoring_type"] and v
            },
            "results": results
        }
        
        return [{"type": "text", "text": str(response)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
