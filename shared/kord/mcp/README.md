# Kord MCP

MCP server for logical agent discovery and delegation through `kord-api`.

## Tools

- `list_agents`
  - List logical agents by default.
  - Set `variants: true` to list explicit deployment variants.
- `get_agent`
  - Fetch one logical agent or one explicit variant.
- `delegate`
  - Primary request tool.
  - Prompt a logical agent or explicit variant.
  - Supports `variant`, `backend_model`, `working_dir`, `session_id`, `async`, and `stream`.
- `resume_request`
  - Resume a prior request by request id.
  - Use `stream: true` to read the normalized transcript snapshot.
- `get_request`
  - Request summary/status. Prefer `resume_request` for normal use.
- `get_request_events`
  - Debug-only raw event timeline.
- `get_e2e_logs`
  - Debug-only end-to-end pod and API logs.

## Environment

- `KORD_API_URL`
  Base URL for `kord-api`.
- `KORD_API_KEY`
  API key for authenticated access.

## Transport

The server uses stdio transport and is intended to be spawned by an MCP client.
