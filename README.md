# OpenClaw Conversation AlfredPatch

A Home Assistant custom component that uses [OpenClaw](https://openclaw.io) as the AI backend for conversation and AI task platforms.

## Why this fork exists (AlfredPatch)

This fork exists to support **custom OpenClaw agent routing** reliably (for example, a dedicated `alfred` house-butler agent instead of always using `main`).

### What changed and why it was necessary

The upstream integration sends chat requests with a static model value:

- ~~`"model": "openclaw"`~~
  - Comment: This can cause requests to fall back to default model behavior, even when `Agent ID` is set.

This fork routes requests using the configured Agent ID:

- `"model": "openclaw:<agent_id>"` (example: `openclaw:alfred`)
  - Comment: This aligns the OpenAI-compatible request with OpenClaw's agent routing so custom agents, prompts, tools, and model selections are actually applied.

### Scope of differences

- Keeps upstream behavior and docs **as-is** unless needed for this routing fix.
- Adds light branding in Home Assistant so you can identify this fork as **OpenClaw Conversation AlfredPatch**.

## Features

- Voice and text conversations with AI-powered responses
- Control Home Assistant devices through natural language via [ha-mcp](https://homeassistant-ai.github.io/ha-mcp/)
- AI Task entity for structured data generation

## Installation

## Migration from upstream (quick steps)

1. In HACS, remove/disable the upstream custom repository if you previously added it.
2. Add your AlfredPatch fork as a Custom Repository (category: Integration).
3. Install/update **OpenClaw Conversation AlfredPatch** from HACS.
4. Restart Home Assistant.
5. Open the integration and verify:
   - OpenClaw URL + Gateway Token are valid
   - `Agent ID` is set to your custom agent (example: `alfred`)
   - `Session Key` is stable (example: `agent:alfred:homeassistant`)

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → Custom repositories
3. ~~Add `https://github.com/Djelibeybi/openclaw_conversation` with category "Integration"~~
   - Comment: For AlfredPatch, add your fork URL instead (for example, `https://github.com/core-runtime/openclaw_conversation`).
4. ~~Search for "OpenClaw Conversation" and install~~
   - Comment: Search for **"OpenClaw Conversation AlfredPatch"** and install
5. Restart Home Assistant

### Manual

1. Copy `custom_components/openclaw_conversation/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Prerequisites

Before configuring this integration, you need:

1. **OpenClaw** installed and running
2. **[ha-mcp](https://homeassistant-ai.github.io/ha-mcp/)** server running (provides Home Assistant control to the agent)
3. **[mcporter](http://mcporter.dev/)** installed on the OpenClaw host

See the [ha-mcp setup guide](docs/ha-mcp-setup.md) for detailed installation instructions.

## Configuration

1. Go to **Settings** → **Devices & Services**
2. ~~Click **Add Integration** and search for "OpenClaw Conversation"~~
   - Comment: In this fork, search for **"OpenClaw Conversation AlfredPatch"**
3. Enter your OpenClaw server details:
   - **OpenClaw URL**: Your OpenClaw server URL (e.g., `http://localhost:18789`)
   - **Gateway Token**: Your OpenClaw Gateway token
   - **Verify SSL**: Uncheck if using `http://` URLs or self-signed certificates

> **Note:** You can generate a Gateway token by running `openclaw doctor --generate-gateway-token` on your OpenClaw instance. This will generate a token and save it to the gateway configuration.

> **SSL/TLS:** If your OpenClaw instance uses `http://` (not HTTPS) or a self-signed certificate, disable "Verify SSL" during setup. For remote access, we recommend using [Tailscale](https://tailscale.com/) or a valid certificate from [Let's Encrypt](https://letsencrypt.org/).

### Agent Configuration

After adding the integration, you need to add a conversation agent:

1. Click on the integration entry
2. Click **Add** under "Conversation agent"
3. Configure the agent with your settings:

| Option            | Description                                                                         |
| ----------------- | ----------------------------------------------------------------------------------- |
| HA MCP Server URL | Your ha-mcp server URL (e.g., `http://homeassistant.local:9583/private_XXXXX`)      |
| Prompt Template   | System prompt with Jinja2 template support                                          |
| Agent ID          | The agent to use (run `openclaw agents list` to see options, default: `main`)       |
| Session Key       | Optional key for session persistence (run `openclaw sessions list` to see sessions) |

> **Agent ID:** Run `openclaw agents list` on your OpenClaw instance to see all configured agents. Most users will use `main` (the default).

> **Session Key:** Setting a specific session key allows conversation context to persist between invocations (until it grows large enough to be auto-compacted). Run `openclaw sessions list` to see existing sessions. For example, `agent:main:homeassistant` creates a dedicated session for Home Assistant conversations.

## Usage

1. Go to **Settings** → **Voice Assistants**
2. Edit your assistant (or create a new one)
3. ~~Select "OpenClaw Conversation" as the **Conversation agent**~~
   - Comment: In this fork, select **"OpenClaw Conversation AlfredPatch"** as the Conversation agent

The agent uses [mcporter](http://mcporter.dev/) to communicate with Home Assistant via the [ha-mcp](https://homeassistant-ai.github.io/ha-mcp/) server. It can search for entities, control devices, manage automations, and more.

## Logging

Add to `configuration.yaml` to enable debug logging:

```yaml
logger:
  logs:
    custom_components.openclaw_conversation: debug
```

## License

This project is licensed under the [Universal Permissive License v1.0](LICENSE).

## Credits

Based on [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation) by [@jekalmin](https://github.com/jekalmin).
