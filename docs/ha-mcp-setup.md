# Using OpenClaw with ha-mcp via mcporter

This guide explains how to give your OpenClaw agent direct access to Home Assistant using the [ha-mcp](https://homeassistant-ai.github.io/ha-mcp/) server and the [mcporter](http://mcporter.dev/) CLI.

## Overview

With this setup, your OpenClaw agent can:
- Search and control any HA entity
- Create, edit, and debug automations
- Manage dashboards, scripts, helpers, and blueprints
- Query history and statistics
- Manage HACS packages
- And much more (93 tools in total)

## Prerequisites

- OpenClaw installed and running
- Home Assistant (any installation type)
- Node.js (for mcporter)

---

## Human Setup

These steps are done by you, the human, to prepare the infrastructure.

### Step 1: Install ha-mcp on Home Assistant

The ha-mcp server runs as a Home Assistant add-on or standalone container.

### Option A: HACS Add-on (Recommended)

1. Add the ha-mcp repository to HACS
2. Install the "HA-MCP Server" add-on
3. Start the add-on
4. Note the URL shown in the add-on logs (e.g., `http://homeassistant.local:9583/private_XXXXX`)

### Option B: Docker

```bash
docker run -d \
  -e HA_URL=http://homeassistant.local:8123 \
  -e HA_TOKEN=your_long_lived_access_token \
  -p 9583:9583 \
  ghcr.io/homeassistant-ai/ha-mcp
```

### Step 2: Install mcporter

mcporter is a CLI tool for interacting with MCP servers. **Install it on the same machine as your OpenClaw agent** so the agent can execute mcporter commands directly.

```bash
npm install -g mcporter
```

Verify installation:

```bash
mcporter --version
```

> **Note:** If your OpenClaw agent runs in a container or on a different host, ensure mcporter is installed there, not on your local machine.

### Step 3: Test the Connection

List available tools from your ha-mcp server:

```bash
mcporter list http://homeassistant.local:9583/private_XXXXX --allow-http
```

You should see 90+ tools listed with descriptions.

---

## Agent Setup

Once the infrastructure is ready, configure the OpenClaw Conversation integration with your ha-mcp URL.

### Step 4: Configure the Integration

1. Go to **Settings** → **Devices & Services**
2. Find your OpenClaw Conversation integration
3. Click **Configure** on the conversation agent
4. Enter your ha-mcp URL in the **HA MCP Server URL** field

The default prompt template will automatically use this URL for mcporter commands.

---

## Usage Examples

These are examples of what your agent can now do.

### Search for entities

```bash
mcporter call http://homeassistant.local:9583/private_XXXXX.ha_search_entities \
  --allow-http query="kitchen light"
```

### Turn on a light

```bash
mcporter call http://homeassistant.local:9583/private_XXXXX.ha_call_service \
  --allow-http domain=light service=turn_on entity_id=light.kitchen
```

### List all areas

```bash
mcporter call http://homeassistant.local:9583/private_XXXXX.ha_config_list_areas \
  --allow-http
```

### Get automation details

```bash
mcporter call http://homeassistant.local:9583/private_XXXXX.ha_config_get_automation \
  --allow-http automation_id=automation.morning_lights
```

### Create a new automation

```bash
mcporter call http://homeassistant.local:9583/private_XXXXX.ha_config_set_automation \
  --allow-http --args '{
    "alias": "Turn on porch light at sunset",
    "trigger": [{"platform": "sun", "event": "sunset"}],
    "action": [{"service": "light.turn_on", "target": {"entity_id": "light.porch"}}]
  }'
```

## Security Notes

- The ha-mcp URL contains a private token — treat it like a password
- Use `--allow-http` only for local/trusted networks
- For remote access, set up ha-mcp behind HTTPS (e.g., via Tailscale or a reverse proxy)
- **Home Assistant does not have granular user permissions** — any authenticated user has full admin access. This means your agent will have full control of HA. Plan accordingly.

## Troubleshooting

### "HTTP endpoints require --allow-http"

Add `--allow-http` to your mcporter command. This is required for non-HTTPS URLs.

### Connection refused

- Verify ha-mcp is running: check the add-on logs or container status
- Verify the URL is correct and accessible from your OpenClaw host
- Check firewall rules if HA and OpenClaw are on different machines

### Tool not found

Use `mcporter list <url> --allow-http` to see all available tools and their exact names.

## What's Next?

Once native MCP support lands in OpenClaw, you'll be able to configure ha-mcp directly without needing mcporter as an intermediary. Until then, this approach works reliably.
