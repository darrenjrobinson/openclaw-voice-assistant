# OpenClaw Voice Assistant

Home Assistant local voice pipeline and OpenClaw conversation bridge for Marvin-style voice assistants.

This repository packages a Home Assistant custom integration derived from the OpenClaw Conversation / AlfredPatch lineage, with public-ready documentation, smoke-test tooling, and notes for wiring a local voice satellite through Home Assistant Assist to OpenClaw.

## What it does

The integration sends Home Assistant conversation turns to the OpenClaw OpenAI-compatible `/v1/chat/completions` endpoint and supports explicit OpenClaw agent routing.

```text
Voice satellite / Assist input
  → Home Assistant Assist pipeline
  → OpenClaw Conversation AlfredPatch
  → OpenClaw Gateway /v1/chat/completions
  → OpenClaw agent/session
```

Useful when you want a local Home Assistant voice assistant backed by an OpenClaw agent instead of a generic cloud assistant. Because apparently light switches now require distributed systems. Obviously.

## Why this fork exists

The important AlfredPatch behaviour is custom OpenClaw agent routing.

Instead of always sending a static model value:

```json
{
  "model": "openclaw"
}
```

this fork can route requests with the configured Agent ID:

```json
{
  "model": "openclaw:<agent_id>"
}
```

For example:

```json
{
  "model": "openclaw:alfred"
}
```

That lets Home Assistant target a dedicated house/voice agent with its own prompt, tools, session key, and model settings rather than polluting your default OpenClaw chat session.

## Features

- Home Assistant conversation agent backed by OpenClaw
- Optional AI Task entity support
- Configurable OpenClaw URL and Gateway token
- Configurable Agent ID and stable Session Key
- Optional explicit Model Override for testing
- OpenClaw gateway smoke-test script
- Documentation for Home Assistant Assist, HACS, and ReSpeaker/Wyoming-style satellite deployments

## Installation

### HACS custom repository

1. Open **HACS** in Home Assistant.
2. Open the menu → **Custom repositories**.
3. Add this repository URL:

   ```text
   https://github.com/darrenjrobinson/openclaw-voice-assistant
   ```

4. Category: **Integration**.
5. Install **OpenClaw Conversation AlfredPatch**.
6. Restart Home Assistant.

### Manual install

1. Copy `custom_components/openclaw_conversation/` to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Prerequisites

Before configuring this integration, you need:

1. **OpenClaw** installed and running.
2. A Home Assistant Assist pipeline.
3. Optional: **[ha-mcp](https://homeassistant-ai.github.io/ha-mcp/)** if you want the OpenClaw agent to control Home Assistant entities.
4. Optional: **[mcporter](http://mcporter.dev/)** on the OpenClaw host if your prompt/tools use MCP via command calls.

See [docs/ha-mcp-setup.md](docs/ha-mcp-setup.md) for one ha-mcp setup path.

## Configuration

### 1. Add the base integration

In Home Assistant:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **OpenClaw Conversation AlfredPatch**.
3. Enter your OpenClaw server details:

| Option | Description |
|---|---|
| OpenClaw URL | Base URL for your OpenClaw Gateway, for example `http://<openclaw-host>:18789` |
| Gateway Token | Your OpenClaw Gateway bearer token |
| Verify SSL | Disable only for trusted HTTP/LAN or self-signed certificate deployments |

> Do not commit Gateway tokens, ha-mcp private URLs, or Home Assistant long-lived access tokens. The machines are already judgemental enough without leaking secrets into Git.

### 2. Add a conversation agent

After adding the integration:

1. Open the integration entry.
2. Click **Add** under **Conversation agents**.
3. Configure the agent.

| Option | Description |
|---|---|
| HA MCP Server URL | Optional/private ha-mcp URL if the agent should control Home Assistant |
| Prompt Template | System prompt with Jinja2 template support |
| Agent ID | OpenClaw agent to use; default is `main` |
| Model Override | Optional explicit provider/model for testing; normally leave blank |
| Session Key | Optional stable session key, for example `agent:alfred:homeassistant` |
| Context Threshold | Token threshold before context truncation |
| Context truncation strategy | Currently supports clearing old messages |

### Model selection priority

Conversation requests choose the model in this order:

1. `Model Override`, if set.
2. `openclaw:<agent_id>`, if Agent ID is set.
3. `openclaw` fallback.

Operationally, use a dedicated OpenClaw agent for Home Assistant voice traffic and leave Model Override blank unless you are deliberately testing routing.

## Attach to an Assist pipeline

1. Go to **Settings → Voice assistants**.
2. Edit or create an Assist pipeline.
3. Set **Conversation agent** to the OpenClaw Conversation AlfredPatch agent.
4. Keep your preferred STT, TTS, and wake-word components.

See [docs/marvin-openclaw-bridge.md](docs/marvin-openclaw-bridge.md) for a fuller bridge guide.

## Smoke test OpenClaw

From a shell that can reach OpenClaw:

```bash
export OPENCLAW_URL="http://<openclaw-host>:18789"
export OPENCLAW_TOKEN="<gateway-token>"
export OPENCLAW_MODEL="openclaw:main"
python3 scripts/openclaw_smoke_test.py
```

Expected result:

```text
/v1/models: HTTP 200
/v1/chat/completions: HTTP 200
Response: bridge-ok
OK
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` | Wrong/missing Gateway token | Re-enter the token in the integration config |
| Connection refused | Wrong URL, gateway down, firewall/routing issue | Confirm the OpenClaw host and port are reachable from Home Assistant |
| `/v1/models` works but conversation fails | Bad model/agent routing or payload issue | Run `scripts/openclaw_smoke_test.py`; start with Agent ID `main` |
| Pipeline replies from wrong assistant | Assist pipeline still points at another conversation agent | Re-select the OpenClaw Conversation AlfredPatch agent |
| Wake word detected but no useful reply | Conversation agent not attached to the pipeline | Edit the Assist pipeline and choose the OpenClaw agent |
| OpenClaw says tool unavailable | Agent prompt/tool policy issue | Use a dedicated voice/house agent with only the required tools |


## CI

The remaining GitHub Actions workflow runs Home Assistant/HACS validation on pushes and pull requests. Claude Code workflows are intentionally not enabled in this public fork because they require repository secrets and broad write permissions; turn them back on only if you understand the blast radius. Which, historically, is where civilisation begins to wobble.

## Public safety checklist

Before publishing your own fork, check that you have not committed:

- Gateway tokens or Authorization headers
- Home Assistant long-lived access tokens
- ha-mcp private URLs
- Real public hostnames unless intentional
- Internal IPs, entity IDs, or room names you consider private
- Personal assistant prompts containing private context

## Repository map

- [AS_BUILT.md](AS_BUILT.md) — Sanitised reference architecture and deployment notes
- [docs/marvin-openclaw-bridge.md](docs/marvin-openclaw-bridge.md) — Home Assistant/OpenClaw bridge configuration guide
- [docs/ha-mcp-setup.md](docs/ha-mcp-setup.md) — ha-mcp setup notes
- [scripts/openclaw_smoke_test.py](scripts/openclaw_smoke_test.py) — OpenClaw endpoint smoke test
- [NOTICE.md](NOTICE.md) — upstream lineage and provenance

## License and credits

This project retains the upstream [Universal Permissive License v1.0](LICENSE).

Based on [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation) by [@jekalmin](https://github.com/jekalmin), the original OpenClaw Conversation integration by [@Djelibeybi](https://github.com/Djelibeybi), and the AlfredPatch fork lineage.
