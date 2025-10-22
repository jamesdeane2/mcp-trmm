"""
Audit log tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List, Optional
from .client import TRMMClient


def get_tools():
    """Return list of audit log-related MCP tools"""
    return [
        {
            "name": "trmm_query_audit_logs",
            "description": "Query audit logs with optional filters for agent and action type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 1
                    },
                    "rows_per_page": {
                        "type": "integer",
                        "description": "Number of rows per page",
                        "default": 100
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Field to sort by",
                        "default": "entry_time"
                    },
                    "descending": {
                        "type": "boolean",
                        "description": "Sort in descending order",
                        "default": True
                    },
                    "agent_filter": {
                        "type": "array",
                        "description": "Filter by specific agent IDs",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "action_filter": {
                        "type": "array",
                        "description": "Filter by action types (e.g., 'modify', 'create', 'delete')",
                        "items": {"type": "string"},
                        "default": []
                    }
                }
            }
        }
    ]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle audit log-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_query_audit_logs":
        payload = {
            "pagination": {
                "sortBy": arguments.get("sort_by", "entry_time"),
                "descending": arguments.get("descending", True),
                "page": arguments.get("page", 1),
                "rowsPerPage": arguments.get("rows_per_page", 100),
                "rowsNumber": 0  # Will be calculated by server
            }
        }
        
        # Add filters if provided
        agent_filter = arguments.get("agent_filter", [])
        if agent_filter:
            payload["agentFilter"] = agent_filter
        
        action_filter = arguments.get("action_filter", [])
        if action_filter:
            payload["actionFilter"] = action_filter
        
        result = client.patch("/logs/audit/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
