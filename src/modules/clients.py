"""
Client and site management tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List
from .client import TRMMClient


def get_tools():
    """Return list of client/site-related MCP tools"""
    return [
        {
            "name": "trmm_list_clients",
            "description": "List all clients configured in Tactical RMM",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle client/site-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_list_clients":
        result = client.get("/clients/")
        return [{"type": "text", "text": str(result)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
