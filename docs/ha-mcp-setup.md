# Using OpenClaw with ha-mcp via MCPorter

This guide explains how to give an OpenClaw agent access to Home Assistant using [ha-mcp](https://homeassistant-ai.github.io/ha-mcp/) and [MCPorter](https://github.com/openclaw/mcporter).

## Working pattern

The current recommended pattern is:

```text
OpenClaw agent
  → shell command
  → mcporter call ha.<tool>
  → MCPorter configured server `ha`
  → ha-mcp stdio server
  → Home Assistant APIs
```

The Home Assistant Conversation integration stores the MCPorter selector `ha` in the **HA MCP server selector or URL** field. The prompt then tells OpenClaw to call:

```bash
mcporter call ha.<tool> [args]
```

Do **not** add `--allow-http` when calling the configured `ha` selector. Use `--allow-http` only when calling a direct cleartext `http://...` MCP URL.

## Prerequisites

- OpenClaw installed and running.
- Home Assistant reachable from the OpenClaw host.
- A Home Assistant long-lived access token.
- `uv` / `uvx` on the OpenClaw host.
- `mcporter` on the OpenClaw host.

## Environment variables

Store Home Assistant connection details outside the repository. Store these in a local environment file outside the repository, for example `<openclaw-env-file>`:

```bash
HOMEASSISTANT_URL=<home-assistant-url>
HOMEASSISTANT_TOKEN=<home-assistant-long-lived-access-token>
```

Never commit the token.

## Install runtime tools

```bash
python3 -m pip install --break-system-packages 'uv>=0.5'
npm install -g mcporter
```

`ha-mcp` requires Python 3.13. `uvx --python 3.13 ...` can download/use a managed Python 3.13 runtime if the system Python is older.

## Create a ha-mcp stdio wrapper

Create a wrapper on the OpenClaw host, for example at `<openclaw-workspace>/bin/ha-mcp-stdio`:

```bash
mkdir -p <openclaw-workspace>/bin
cat > <openclaw-workspace>/bin/ha-mcp-stdio <<'SH'
#!/usr/bin/env bash
set -euo pipefail
set -a
source <openclaw-env-file>
set +a
exec /usr/local/bin/uvx --python 3.13 --from ha-mcp@7.9.0 ha-mcp
SH
chmod 700 <openclaw-workspace>/bin/ha-mcp-stdio
```

The wrapper reads secrets at runtime so MCPorter config does not contain the Home Assistant token.

## Register the MCPorter server

```bash
mcporter config add ha \
  --command <openclaw-workspace>/bin/ha-mcp-stdio \
  --description "Home Assistant MCP via ha-mcp stdio wrapper" \
  --scope home
```

Inspect it:

```bash
mcporter config get ha --json
```

## Verify the bridge

```bash
mcporter list ha --status --json --timeout 120000
```

Expected: counts show one `ok` server and the `ha` server status is `ok`.

```bash
mcporter call ha.ha_get_overview --timeout 120000 --output json
```

Expected: Home Assistant summary data including version, entity count, domain count, service count, and area count.

## Useful tools

Run this to see all available tools:

```bash
mcporter list ha --brief --timeout 120000
```

Common tools:

| Tool | Purpose |
|---|---|
| `ha_get_overview` | Summarise Home Assistant and entity counts |
| `ha_search` | Search entities, automations, scripts, scenes, helpers |
| `ha_get_state` | Get state/attributes for an entity |
| `ha_call_service` | Call a Home Assistant service, e.g. turn on a light |
| `ha_list_services` | List available services |
| `ha_list_floors_areas` | List floors/areas |
| `ha_get_logs` | Read recent Home Assistant logs |
| `ha_get_integration` | Inspect integration/config-entry state |

Example calls:

```bash
mcporter call ha.ha_search query="kitchen light" limit=10
mcporter call ha.ha_get_state entity_id="light.kitchen"
mcporter call ha.ha_call_service domain="light" service="turn_on" entity_id="light.kitchen"
```

## Configure OpenClaw Conversation

In the Home Assistant `OpenClaw Conversation AlfredPatch` conversation subentry:

| Field | Value |
|---|---|
| HA MCP server selector or URL | `ha` |
| Agent ID | `main` for first smoke test; later a dedicated agent such as `alfred` |
| Model Override | blank |
| Session Key | `agent:main:homeassistant` for first smoke test |

Prompt pattern:

```text
To query or control Home Assistant, use mcporter like this:

mcporter call ha.<tool> [args]

Do not use --allow-http with the ha selector.
```

## Optional HTTP URL mode

If a client cannot use MCPorter configured server selectors and truly needs an MCP URL, run `ha-mcp-web`:

```bash
set -a
source <openclaw-env-file>
set +a
export MCP_HOST=127.0.0.1
export MCP_PORT=8086
export MCP_SECRET_PATH=/mcp
uvx --python 3.13 --from ha-mcp@7.9.0 ha-mcp-web
```

Local URL:

```text
http://127.0.0.1:8086/mcp
```

Only use this URL from the OpenClaw host itself. Do not expose this endpoint publicly.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Ad-hoc servers require either --http-url or --stdio` | Used `--allow-http` with configured selector `ha` | Remove `--allow-http` |
| `ha` is rejected as a URL in the HA UI | Old integration field still enforces URL selector | Update to v1.1.4+ or use URL mode temporarily |
| Tool not found | Prompt lists stale ha-mcp tool names | Use `mcporter list ha --brief`; current search tool is `ha_search`, not `ha_search_entities` |
| Auth failure | Bad `HOMEASSISTANT_TOKEN` | Regenerate/reload long-lived access token |
| HA API unreachable | Wrong `HOMEASSISTANT_URL` or network path | Confirm `curl -H "Authorization: Bearer ..." $HOMEASSISTANT_URL/api/` returns 200 |
| ha-mcp requires Python 3.13 | System Python too old | Use `uvx --python 3.13 --from ha-mcp@7.9.0 ha-mcp` |

## Security notes

- Keep `HOMEASSISTANT_TOKEN` out of Git.
- Keep OpenClaw Gateway tokens out of Git.
- Prefer MCPorter stdio selector mode over exposing a network MCP endpoint.
- If HTTP mode is required, bind to `127.0.0.1` unless you have a specific protected network design.
- Do not expose OpenClaw, ha-mcp, or Home Assistant long-lived-token backed services directly to the internet.
