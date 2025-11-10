# Local Scripts Directory

This directory contains custom scripts that can be deployed to Tactical RMM agents via the MCP server.

## Directory Structure

```
scripts/
├── powershell/     # PowerShell scripts (.ps1)
├── python/         # Python scripts (.py)
├── bash/          # Bash scripts (.sh)
└── cmd/           # CMD/Batch scripts (.cmd, .bat)
```

## Usage

### List Available Scripts
```
"List my local scripts"
"Show me all PowerShell scripts"
```

### View Script Content
```
"Show me the content of powershell/disk_cleanup.ps1"
```

### Deploy a Script
```
"Deploy powershell/disk_cleanup.ps1 to agent ABC123"
"Run python/system_info.py on agents ABC123 and XYZ456"
```

### Save a New Script
```
"Save this PowerShell script as 'get_services' in the local scripts"
```

### Delete a Script
```
"Delete the script powershell/old_script.ps1"
```

## Script Organization

- Scripts are automatically organized by type in subdirectories
- File extensions determine the shell type for execution:
  - `.ps1` → PowerShell
  - `.py` → Python
  - `.sh` → Bash
  - `.cmd`, `.bat` → CMD
- Scripts are stored on disk and only read when needed (token-efficient!)

## Security

- Scripts are isolated within the `scripts/` directory
- Path validation prevents directory traversal attacks
- Scripts are never exposed in the context window unless explicitly requested

## Tips

- Use descriptive names for your scripts
- Include comments in your scripts for documentation
- Test scripts on a single agent before deploying to multiple agents
- Keep commonly used scripts organized by category/function
