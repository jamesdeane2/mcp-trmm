![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-compatible-purple)

# Tactical RMM MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the Tactical RMM API, enabling AI assistants to manage and interact with your Tactical RMM deployment.

## Features

### Agent Management
- List all agents with optional detailed information
- Get specific agent details
- Update agent custom fields
- Get agent tasks and their results

### Script Execution
- Run scripts from the Script Library on agents
- Execute ad-hoc commands and scripts
- Support for PowerShell, CMD, and Python shells
- Configure timeout, arguments, and execution context

### Windows Updates
- Trigger Windows Update scans on specific agents
- Scan all agents for updates (bulk operation)

### Software Inventory
- Get installed software for specific agents
- Retrieve software inventory for all agents
- Refresh software inventory on demand

### Task Management
- List all configured automated tasks
- Create collector tasks with custom field integration
- Get task execution results

### Custom Fields
- List all custom fields (filterable by model type)
- Create new custom fields
- Get custom field values for agents

### Audit Logs
- Query audit logs with pagination
- Filter by agent ID and action type
- Sort and organize audit trail data

### Client Management
- List all clients and sites

## Installation

1. Clone or download this repository to `/path/to/mcp-trmm`

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Edit `.env` with your Tactical RMM details:
```env
TRMM_API_URL=https://api.yourdomain.com
TRMM_API_KEY=your-api-key-here
TRMM_BETA_API_ENABLED=false
LOG_LEVEL=INFO
LOG_FILE=trmm_mcp.log
```

## Getting Your API Key

1. Log in to your Tactical RMM web interface
2. Navigate to **Settings > Global Settings > API Keys**
3. Click **Generate API Key**
4. Select the user account (this determines permissions)
5. Copy the generated key to your `.env` file

⚠️ **Important**: API keys bypass 2FA authentication. Keep them secure!

## Configuration with Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "trmm": {
      "command": "python",
      "args": [
        "/path/to/mcp-trmm/server.py"
      ]
    }
  }
}
```

Then restart Claude Desktop.

## Available Tools

### Agent Operations
- `trmm_list_agents` - List all agents
- `trmm_get_agent` - Get specific agent details
- `trmm_update_agent_custom_fields` - Update agent custom fields
- `trmm_get_agent_tasks` - Get tasks for an agent

### Script Operations
- `trmm_run_script` - Run a script from the library
- `trmm_run_command` - Execute ad-hoc commands

### Windows Update Operations
- `trmm_scan_windows_updates` - Scan specific agent
- `trmm_scan_all_agents_updates` - Scan all agents

### Software Operations
- `trmm_get_agent_software` - Get software for specific agent
- `trmm_refresh_agent_software` - Refresh software inventory for agent
- `trmm_get_all_software` - Get software for all agents
- `trmm_refresh_all_software` - Refresh all agents' software

### Task Operations
- `trmm_list_tasks` - List all tasks
- `trmm_create_collector_task` - Create new collector task
- `trmm_get_task_results` - Get task results for agent

### Custom Field Operations
- `trmm_list_custom_fields` - List custom fields
- `trmm_create_custom_field` - Create new custom field
- `trmm_get_agent_custom_fields` - Get custom fields for agent

### Audit Log Operations
- `trmm_query_audit_logs` - Query audit logs with filters

### Client Operations
- `trmm_list_clients` - List all clients

## Usage Examples

### List All Agents
```
Can you show me all my Tactical RMM agents?
```

### Run a Script
```
Run script ID 89 on agent ABC123 with a 120 second timeout
```

### Get Software Inventory
```
What software is installed on agent XYZ456?
```

### Create a Collector Task
```
Create a daily collector task that runs script 121 at 8 AM and stores the output in custom field 14
```

### Query Audit Logs
```
Show me the last 50 audit log entries for modifications
```

## Project Structure

```
mcp-trmm/
├── server.py                          # Main MCP server entry point
├── src/
│   └── trmm_mcp/
│       ├── __init__.py
│       └── modules/
│           ├── __init__.py
│           ├── client.py              # Base API client
│           ├── agents.py              # Agent operations
│           ├── scripts.py             # Script execution
│           ├── windows_updates.py     # Windows Update operations
│           ├── software.py            # Software inventory
│           ├── tasks.py               # Task management
│           ├── custom_fields.py       # Custom field operations
│           ├── audit_logs.py          # Audit log queries
│           └── clients.py             # Client/site management
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Error Handling

All errors are logged to the file specified in `LOG_FILE` (default: `trmm_mcp.log`). The server uses comprehensive error handling and will return descriptive error messages when operations fail.

## API Endpoint Reference

This MCP server supports both the standard Tactical RMM API and the Beta v1 API (when enabled). Key endpoints include:

- `/agents/` - Agent operations
- `/scripts/{agent_id}/test/` - Ad-hoc script execution
- `/agents/{agent_id}/runscript/` - Run library scripts
- `/winupdate/{agent_id}/scan/` - Windows Update scans
- `/software/{agent_id}/` - Software inventory
- `/tasks/` - Task management
- `/core/customfields/` - Custom field operations
- `/logs/audit/` - Audit logs
- `/clients/` - Client/site listing

## Important Notes

⚠️ **Trailing Slashes**: The Tactical RMM API is sensitive to trailing slashes. This server handles them automatically.

⚠️ **Rate Limiting**: Be cautious with bulk operations (scan all agents, refresh all software) on large deployments.

⚠️ **Permissions**: API key permissions are inherited from the associated user account.

## Troubleshooting

### Server won't start
- Verify `.env` file exists and contains valid `TRMM_API_URL` and `TRMM_API_KEY`
- Check the log file for detailed error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Tools not appearing in Claude
- Restart Claude Desktop after configuration changes
- Check the configuration file path and JSON syntax
- Verify Python is accessible from the command line

### API errors
- Confirm your API key is valid and not expired
- Check that the API URL is correct (including https://)
- Verify the agent IDs, script IDs, and other parameters are correct
- Review the log file for detailed error information

## Development

### Adding New Tools

1. Create or modify a module in `src/trmm_mcp/modules/`
2. Implement `get_tools()` to return tool definitions
3. Implement `handle_tool_call(name, arguments)` to handle execution
4. Import the module in `server.py` and add to `ALL_MODULES`

### Testing

You can test individual API calls using the `TRMMClient` class:

```python
from src.trmm_mcp.modules.client import TRMMClient

client = TRMMClient()
agents = client.get("/agents/", params={"detail": "false"})
print(agents)
```

## License

This project is provided as-is for use with Tactical RMM deployments.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Resources

- [Tactical RMM Documentation](https://docs.tacticalrmm.com/)
- [Tactical RMM API Documentation](https://docs.tacticalrmm.com/api/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
