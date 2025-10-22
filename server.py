#!/usr/bin/env python3
"""
Tactical RMM MCP Server

This MCP server provides tools to interact with Tactical RMM API
"""
import asyncio
import logging
import os
from typing import Any, Sequence
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import Tool, TextContent

# Import all module handlers
from src.modules import agents, scripts, windows_updates, software, tasks, custom_fields, audit_logs, clients

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "trmm_mcp.log")

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("trmm-mcp-server")

# Collect all tools from modules
ALL_MODULES = [
    agents,
    scripts,
    windows_updates,
    software,
    tasks,
    custom_fields,
    audit_logs,
    clients
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Tactical RMM tools"""
    tools = []
    
    for module in ALL_MODULES:
        module_tools = module.get_tools()
        for tool_def in module_tools:
            tools.append(Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                inputSchema=tool_def["inputSchema"]
            ))
    
    logger.info(f"Listed {len(tools)} tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls by routing to appropriate module"""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        # Route to appropriate module based on tool name prefix
        if name.startswith("trmm_"):
            # Try each module's handler
            for module in ALL_MODULES:
                # Check if this module has the tool
                module_tool_names = [t["name"] for t in module.get_tools()]
                if name in module_tool_names:
                    result = await module.handle_tool_call(name, arguments)
                    logger.info(f"Tool {name} executed successfully")
                    return result
        
        # If we get here, tool wasn't found
        error_msg = f"Unknown tool: {name}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
        
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for the MCP server"""
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting Tactical RMM MCP Server")
    
    # Verify environment variables are set
    if not os.getenv("TRMM_API_URL") or not os.getenv("TRMM_API_KEY"):
        logger.error("TRMM_API_URL and TRMM_API_KEY must be set in .env file")
        raise ValueError("Missing required environment variables")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
