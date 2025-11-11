"""
Local script management tools for Tactical RMM MCP Server
Manages scripts stored in the local scripts/ directory
"""
import os
from typing import Any, Dict, List
from pathlib import Path
from .client import TRMMClient


# Map file extensions to shell types
EXTENSION_MAP = {
    '.ps1': 'powershell',
    '.py': 'python',
    '.sh': 'bash',
    '.cmd': 'cmd',
    '.bat': 'cmd'
}

# Get the scripts directory path relative to project root
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"


def get_tools():
    """Return list of local script management MCP tools"""
    return [
        {
            "name": "trmm_list_local_scripts",
            "description": "List all scripts stored in the local scripts directory, organized by type (powershell, python, bash, cmd)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_type": {
                        "type": "string",
                        "description": "Filter by script type (optional)",
                        "enum": ["powershell", "python", "bash", "cmd", "all"],
                        "default": "all"
                    }
                }
            }
        },
        {
            "name": "trmm_get_local_script",
            "description": "Read the content of a specific local script. Use the path returned from trmm_list_local_scripts (e.g., 'powershell/script_name.ps1')",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the script relative to scripts directory (e.g., 'powershell/disk_cleanup.ps1')"
                    }
                },
                "required": ["script_path"]
            }
        },
        {
            "name": "trmm_deploy_local_script",
            "description": "Deploy a local script to agents. Can target specific agents, all agents in a site, or all agents for a client. Specify one of: agent_ids, site_name, or client_name. WARNING: Use only ASCII characters in scripts - special/Unicode characters can cause execution failures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the script relative to scripts directory (e.g., 'powershell/disk_cleanup.ps1')"
                    },
                    "agent_ids": {
                        "type": "array",
                        "description": "Array of agent IDs to deploy the script to (use this OR site_name OR client_name)",
                        "items": {"type": "string"}
                    },
                    "site_name": {
                        "type": "string",
                        "description": "Name of the site - deploys to all agents in this site (use this OR agent_ids OR client_name)"
                    },
                    "client_name": {
                        "type": "string",
                        "description": "Name of the client - deploys to all agents for this client (use this OR agent_ids OR site_name)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 90)",
                        "default": 90
                    },
                    "args": {
                        "type": "array",
                        "description": "Array of arguments to pass to the script",
                        "items": {"type": "string"},
                        "default": []
                    }
                },
                "required": ["script_path"]
            }
        },
        {
            "name": "trmm_save_local_script",
            "description": "Save or update a script in the local scripts directory. The script will be saved in the appropriate subdirectory based on the shell type. WARNING: Use only ASCII characters in scripts - special/Unicode characters can cause execution failures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name of the script file (e.g., 'disk_cleanup.ps1', 'system_info.py')"
                    },
                    "script_content": {
                        "type": "string",
                        "description": "The content of the script"
                    },
                    "shell_type": {
                        "type": "string",
                        "description": "Type of shell/script",
                        "enum": ["powershell", "python", "bash", "cmd"]
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if script already exists (default: false)",
                        "default": False
                    }
                },
                "required": ["script_name", "script_content", "shell_type"]
            }
        },
        {
            "name": "trmm_delete_local_script",
            "description": "Delete a script from the local scripts directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the script relative to scripts directory (e.g., 'powershell/disk_cleanup.ps1')"
                    }
                },
                "required": ["script_path"]
            }
        }
    ]


def _list_scripts_in_directory(base_dir: Path, script_type: str = "all") -> List[Dict[str, Any]]:
    """Helper function to list scripts in a directory"""
    scripts = []
    
    # Determine which directories to scan
    if script_type == "all":
        subdirs = ["powershell", "python", "bash", "cmd"]
    else:
        subdirs = [script_type]
    
    for subdir in subdirs:
        dir_path = base_dir / subdir
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                # Get file extension to verify it matches the directory
                ext = file_path.suffix.lower()
                expected_shell = EXTENSION_MAP.get(ext, "unknown")
                
                scripts.append({
                    "name": file_path.name,
                    "path": f"{subdir}/{file_path.name}",
                    "type": subdir,
                    "extension": ext,
                    "size_bytes": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
    
    return scripts


def _read_script(script_path: str) -> str:
    """Helper function to read a script file"""
    full_path = SCRIPTS_DIR / script_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    if not full_path.is_file():
        raise ValueError(f"Path is not a file: {script_path}")
    
    # Security check: ensure the path is within scripts directory
    if not str(full_path.resolve()).startswith(str(SCRIPTS_DIR.resolve())):
        raise ValueError(f"Invalid script path: {script_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()


def _detect_shell_from_path(script_path: str) -> str:
    """Detect shell type from script path or extension"""
    ext = Path(script_path).suffix.lower()
    return EXTENSION_MAP.get(ext, "powershell")  # Default to powershell


def _resolve_agents_from_target(
    agent_ids: List[str] = None,
    site_name: str = None,
    client_name: str = None
) -> List[str]:
    """
    Resolve agent IDs from various targeting options.
    Returns a list of agent IDs to deploy to.
    """
    client = TRMMClient()
    
    # If agent_ids provided directly, use them
    if agent_ids:
        return agent_ids
    
    # Get all agents with details
    agents = client.get("/agents/", params={"detail": "true"})
    
    # Filter by site_name if provided
    if site_name:
        filtered_agents = [
            agent["agent_id"] 
            for agent in agents 
            if agent.get("site_name", "").lower() == site_name.lower()
        ]
        if not filtered_agents:
            raise ValueError(f"No agents found for site: {site_name}")
        return filtered_agents
    
    # Filter by client_name if provided
    if client_name:
        filtered_agents = [
            agent["agent_id"] 
            for agent in agents 
            if agent.get("client_name", "").lower() == client_name.lower()
        ]
        if not filtered_agents:
            raise ValueError(f"No agents found for client: {client_name}")
        return filtered_agents
    
    # If we get here, no targeting was specified
    raise ValueError("Must specify one of: agent_ids, site_name, or client_name")


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle local script management tool calls"""
    
    if name == "trmm_list_local_scripts":
        script_type = arguments.get("script_type", "all")
        scripts = _list_scripts_in_directory(SCRIPTS_DIR, script_type)
        
        # Format output nicely
        if not scripts:
            return [{"type": "text", "text": f"No scripts found in {SCRIPTS_DIR}"}]
        
        result = {
            "scripts_directory": str(SCRIPTS_DIR),
            "total_scripts": len(scripts),
            "scripts": scripts
        }
        return [{"type": "text", "text": str(result)}]
    
    elif name == "trmm_get_local_script":
        script_path = arguments["script_path"]
        
        try:
            content = _read_script(script_path)
            result = {
                "script_path": script_path,
                "content": content,
                "size_bytes": len(content.encode('utf-8'))
            }
            return [{"type": "text", "text": str(result)}]
        except Exception as e:
            return [{"type": "text", "text": f"Error reading script: {str(e)}"}]
    
    elif name == "trmm_deploy_local_script":
        script_path = arguments["script_path"]
        timeout = arguments.get("timeout", 90)
        args = arguments.get("args", [])
        
        # Extract targeting parameters
        agent_ids = arguments.get("agent_ids")
        site_name = arguments.get("site_name")
        client_name = arguments.get("client_name")
        
        try:
            # Resolve which agents to target
            target_agent_ids = _resolve_agents_from_target(
                agent_ids=agent_ids,
                site_name=site_name,
                client_name=client_name
            )
            
            # Read the script content
            script_content = _read_script(script_path)
            
            # Detect shell type
            shell = _detect_shell_from_path(script_path)
            
            # Deploy to each agent
            client = TRMMClient()
            results = []
            
            for agent_id in target_agent_ids:
                try:
                    payload = {
                        "code": script_content,
                        "shell": shell,
                        "timeout": timeout,
                        "args": args
                    }
                    result = client.post(f"/scripts/{agent_id}/test/", data=payload)
                    results.append({
                        "agent_id": agent_id,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "agent_id": agent_id,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Build response with targeting info
            response = {
                "script_path": script_path,
                "shell_type": shell,
                "agents_targeted": len(target_agent_ids),
                "results": results
            }
            
            # Add targeting details
            if site_name:
                response["target_type"] = "site"
                response["target_name"] = site_name
            elif client_name:
                response["target_type"] = "client"
                response["target_name"] = client_name
            else:
                response["target_type"] = "specific_agents"
            
            return [{"type": "text", "text": str(response)}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error deploying script: {str(e)}"}]
    
    elif name == "trmm_save_local_script":
        script_name = arguments["script_name"]
        script_content = arguments["script_content"]
        shell_type = arguments["shell_type"]
        overwrite = arguments.get("overwrite", False)
        
        try:
            # Ensure the subdirectory exists
            target_dir = SCRIPTS_DIR / shell_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Full path to the script
            script_path = target_dir / script_name
            
            # Check if file exists and overwrite is False
            if script_path.exists() and not overwrite:
                return [{"type": "text", "text": f"Error: Script already exists at {shell_type}/{script_name}. Use overwrite=true to replace it."}]
            
            # Write the script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            result = {
                "status": "success",
                "script_path": f"{shell_type}/{script_name}",
                "full_path": str(script_path),
                "size_bytes": len(script_content.encode('utf-8')),
                "action": "overwritten" if script_path.exists() else "created"
            }
            return [{"type": "text", "text": str(result)}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error saving script: {str(e)}"}]
    
    elif name == "trmm_delete_local_script":
        script_path = arguments["script_path"]
        
        try:
            full_path = SCRIPTS_DIR / script_path
            
            if not full_path.exists():
                return [{"type": "text", "text": f"Error: Script not found: {script_path}"}]
            
            # Security check
            if not str(full_path.resolve()).startswith(str(SCRIPTS_DIR.resolve())):
                return [{"type": "text", "text": f"Error: Invalid script path: {script_path}"}]
            
            # Delete the file
            full_path.unlink()
            
            result = {
                "status": "success",
                "deleted_script": script_path,
                "message": f"Script {script_path} has been deleted"
            }
            return [{"type": "text", "text": str(result)}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error deleting script: {str(e)}"}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]
