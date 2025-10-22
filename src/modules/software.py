"""
Software inventory tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List
from .client import TRMMClient


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
            "description": "Get software inventory for all agents (warning: may be large dataset)",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "trmm_refresh_all_software",
            "description": "Refresh software inventory for all agents (use with caution on large deployments)",
            "inputSchema": {
                "type": "object",
                "properties": {}
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
        # Get all agents first
        agents = client.get("/agents/", params={"detail": "false"})
        all_software = []
        
        for agent in agents:
            try:
                software = client.get(f"/software/{agent['agent_id']}/")
                all_software.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "software": software
                })
            except Exception as e:
                all_software.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "error": str(e)
                })
        
        return [{"type": "text", "text": str(all_software)}]
    
    elif name == "trmm_refresh_all_software":
        # Get all agents first
        agents = client.get("/agents/", params={"detail": "false"})
        results = []
        
        for agent in agents:
            try:
                result = client.put(f"/software/{agent['agent_id']}/")
                results.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "result": result
                })
            except Exception as e:
                results.append({
                    "agent_id": agent["agent_id"],
                    "hostname": agent.get("hostname", "unknown"),
                    "error": str(e)
                })
        
        return [{"type": "text", "text": str(results)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
