# Kord MCP

MCP server for logical agent discovery and delegation through `kord-api`.

## Tools

- `list_agents`
  - List logical agents by default.
  - Set `variants: true` to list explicit deployment variants.
- `get_agent`
  - Fetch one logical agent or one explicit variant.
- `delegate`
  - Prompt a logical agent or explicit variant.
  - Supports `variant`, `backend_model`, `working_dir`, `session_id`, and `async`.
- `get_request`
  - Check async request status.

## Environment

- `KORD_API_URL`
  Base URL for `kord-api`.
- `KORD_API_KEY`
  API key for authenticated access.

## Transport

The server uses stdio transport and is intended to be spawned by an MCP client.
