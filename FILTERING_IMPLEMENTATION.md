# Agent Filtering Implementation

## Overview
Added comprehensive filtering capabilities to all bulk operations and agent listing tools to dramatically reduce token usage when working with subsets of agents.

## Changes Made

### 1. Agent Module (`src/modules/agents.py`)
**Tool Updated:** `trmm_list_agents`

**New Parameters:**
- `client_name` (string, optional) - Filter by client name
- `site_name` (string, optional) - Filter by site name  
- `status` (string, optional) - Filter by online/offline status
- `monitoring_type` (string, optional) - Filter by workstation/server

**Response Format:**
```json
{
  "total_agents": 150,
  "filtered_agents": 12,
  "filters_applied": {
    "client_name": "Acme Corp",
    "status": "online"
  },
  "agents": [...]
}
```

### 2. Windows Updates Module (`src/modules/windows_updates.py`)
**Tool Updated:** `trmm_scan_all_agents_updates`

**New Parameters:**
- `client_name` (string, optional) - Filter by client name
- `site_name` (string, optional) - Filter by site name
- `status` (string, optional, default: "online") - Filter by status
- `monitoring_type` (string, optional) - Filter by workstation/server

**Response Format:**
```json
{
  "total_agents": 150,
  "filtered_agents": 12,
  "scanned_agents": 12,
  "filters_applied": {...},
  "results": [...]
}
```

### 3. Software Module (`src/modules/software.py`)
**Tools Updated:** 
- `trmm_get_all_software`
- `trmm_refresh_all_software`

**New Parameters (both tools):**
- `client_name` (string, optional) - Filter by client name
- `site_name` (string, optional) - Filter by site name
- `status` (string, optional) - Filter by status
- `monitoring_type` (string, optional) - Filter by workstation/server

**Special Note:** `trmm_refresh_all_software` defaults to `status="online"` to avoid attempting refreshes on offline agents.

**Response Format:**
```json
{
  "total_agents": 150,
  "filtered_agents": 12,
  "filters_applied": {...},
  "software_data": [...] // or "results": [...]
}
```

## How It Works

1. **API Call:** Tools fetch agents with `detail=true` to get all metadata (client_name, site_name, status, monitoring_type)
2. **Client-Side Filtering:** Python filters the results before returning to MCP
3. **Token Savings:** Only filtered agents are included in the response to Claude

## Usage Examples

### List agents for a specific client
```
Show me all agents for client "Acme Corp"
```

### Scan Windows updates for a specific site
```
Run Windows update scan on all online workstations in the "London Office" site
```

### Get software for servers only
```
Get software inventory for all servers in the "DataCenter" site
```

### Refresh software for a client
```
Refresh software inventory for all online agents at "Smith & Co"
```

## Token Savings Example

**Before:** Listing all agents would return 150 agents, using ~50,000 tokens

**After:** Listing agents for "Acme Corp" returns only 12 agents, using ~4,000 tokens

**Savings:** ~92% reduction in tokens for filtered queries

## Backward Compatibility

All filtering parameters are optional. If no filters are provided:
- Tools work exactly as before
- Return all agents (for listing)
- Process all agents (for bulk operations)

## Filter Logic

- All filters use **case-insensitive** matching
- Filters are **AND** conditions (all specified filters must match)
- Empty/null filter values are ignored
- Status filter in `trmm_refresh_all_software` defaults to "online" to prevent unnecessary API calls

## Response Structure Benefits

New response format provides:
1. **Summary statistics** - See how many agents matched your filters
2. **Filter confirmation** - See exactly what filters were applied
3. **Filtered data only** - Only matching agents consume tokens
4. **Context preservation** - Client/site names included in results for clarity
