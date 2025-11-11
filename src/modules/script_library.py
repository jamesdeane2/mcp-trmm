"""
Script Library management tools for Tactical RMM MCP Server
Manages scripts in the TRMM Script Library
"""
from typing import Any, Dict, List
from pathlib import Path
from .client import TRMMClient


def get_tools():
    """Return list of Script Library management MCP tools"""
    return [
        {
            "name": "trmm_list_library_scripts",
            "description": "List all scripts in the Tactical RMM Script Library",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "trmm_get_library_script",
            "description": "Get details of a specific script from the Script Library by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_id": {
                        "type": "integer",
                        "description": "The script ID from the Script Library"
                    }
                },
                "required": ["script_id"]
            }
        },
        {
            "name": "trmm_upload_script_to_library",
            "description": "Upload a script to the Tactical RMM Script Library. Creates a new script entry. WARNING: Use only ASCII characters in scripts - special/Unicode characters can cause execution failures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the script"
                    },
                    "script_body": {
                        "type": "string",
                        "description": "The script code/content"
                    },
                    "shell": {
                        "type": "string",
                        "description": "Shell type to run the script",
                        "enum": ["powershell", "cmd", "python"],
                        "default": "powershell"
                    },
                    "default_timeout": {
                        "type": "integer",
                        "description": "Default timeout in seconds",
                        "default": 90
                    },
                    "args": {
                        "type": "array",
                        "description": "Default arguments for the script",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "env_vars": {
                        "type": "array",
                        "description": "Environment variables for the script",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "run_as_user": {
                        "type": "boolean",
                        "description": "Run as logged-in user instead of SYSTEM",
                        "default": False
                    }
                },
                "required": ["name", "script_body"]
            }
        },
        {
            "name": "trmm_upload_local_script_to_library",
            "description": "Upload a local script from the scripts directory to the TRMM Script Library. WARNING: Use only ASCII characters in scripts - special/Unicode characters can cause execution failures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the local script (e.g., 'powershell/disk_cleanup.ps1')"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the script in the library (optional, uses filename if not provided)"
                    },
                    "default_timeout": {
                        "type": "integer",
                        "description": "Default timeout in seconds",
                        "default": 90
                    }
                },
                "required": ["script_path"]
            }
        }
    ]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle Script Library management tool calls"""
    client = TRMMClient()
    
    if name == "trmm_list_library_scripts":
        result = client.get("/scripts/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_library_script":
        script_id = arguments["script_id"]
        result = client.get(f"/scripts/{script_id}/")
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_upload_script_to_library":
        payload = {
            "name": arguments["name"],
            "script_body": arguments["script_body"],
            "shell": arguments.get("shell", "powershell"),
            "default_timeout": arguments.get("default_timeout", 90),
            "args": arguments.get("args", []),
            "env_vars": arguments.get("env_vars", []),
            "run_as_user": arguments.get("run_as_user", False)
        }
        
        result = client.post("/scripts/", data=payload)
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_upload_local_script_to_library":
        script_path = arguments["script_path"]
        
        try:
            from . import local_scripts
            
            script_content = local_scripts._read_script(script_path)
            shell = local_scripts._detect_shell_from_path(script_path)
            
            if "name" in arguments:
                name = arguments["name"]
            else:
                name = Path(script_path).stem
            
            payload = {
                "name": name,
                "script_body": script_content,
                "shell": shell,
                "default_timeout": arguments.get("default_timeout", 90),
                "args": [],
                "env_vars": [],
                "run_as_user": False
            }
            
            result = client.post("/scripts/", data=payload)
            
            response = {
                "status": "success",
                "local_script_path": script_path,
                "library_script": result,
                "message": f"Script '{name}' uploaded to library"
            }
            
            return [{"type": "text", "text": str(response)}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error: {str(e)}"}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
