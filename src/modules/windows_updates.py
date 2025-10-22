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
            "description": "Trigger Windows Update scans on all agents (use with caution on large deployments)",
            "inputSchema": {
                "type": "object",
                "properties": {}
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
        # Get all agents
        agents = client.get("/agents/", params={"detail": "false"})
        results = []
        
        for agent in agents:
            try:
                result = client.post(f"/winupdate/{agent['agent_id']}/scan/")
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
