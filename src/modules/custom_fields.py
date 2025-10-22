"""
Custom fields tools for Tactical RMM MCP Server
"""
from typing import Any, Dict, List, Optional
from .client import TRMMClient


def get_tools():
    """Return list of custom field-related MCP tools"""
    return [
        {
            "name": "trmm_list_custom_fields",
            "description": "Get all custom fields configured in Tactical RMM",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Filter by model type (e.g., 'agent', 'client', 'site')",
                        "enum": ["agent", "client", "site", "all"],
                        "default": "all"
                    }
                }
            }
        },
        {
            "name": "trmm_create_custom_field",
            "description": "Create a new custom field",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Model to attach field to",
                        "enum": ["agent", "client", "site"]
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the custom field"
                    },
                    "field_type": {
                        "type": "string",
                        "description": "Type of custom field",
                        "enum": ["text", "number", "single", "multiple", "checkbox", "datetime"]
                    },
                    "options": {
                        "type": "array",
                        "description": "Options for single/multiple choice fields",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "default_value": {
                        "type": "string",
                        "description": "Default value for the field"
                    }
                },
                "required": ["model", "name", "field_type"]
            }
        },
        {
            "name": "trmm_get_agent_custom_fields",
            "description": "Get custom field values for a specific agent",
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
    """Handle custom field-related tool calls"""
    client = TRMMClient()
    
    if name == "trmm_list_custom_fields":
        result = client.get("/core/customfields/")
        
        # Filter by model if specified
        model_filter = arguments.get("model", "all")
        if model_filter != "all":
            result = [field for field in result if field.get("model", "").lower() == model_filter.lower()]
        
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_create_custom_field":
        payload = {
            "model": arguments["model"],
            "name": arguments["name"],
            "type": arguments["field_type"],
            "options": arguments.get("options", [])
        }
        
        if "default_value" in arguments:
            payload["default_value"] = arguments["default_value"]
        
        result = client.post("/core/customfields/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_agent_custom_fields":
        agent_id = arguments["agent_id"]
        # Get agent details which includes custom fields
        result = client.get(f"/agents/{agent_id}/")
        custom_fields = result.get("custom_fields", [])
        return [{"type": "text", "text": str(custom_fields)}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
