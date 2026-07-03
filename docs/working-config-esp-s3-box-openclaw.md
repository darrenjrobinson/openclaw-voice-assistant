# Working configuration: ESP-S3-Box → Home Assistant → OpenClaw

This document records the known-good configuration used for the Marvin voice assistant bridge.

It deliberately avoids live secrets and uses placeholder hostnames/IPs. Replace placeholders with your own values.

## Verified architecture

```text
ESP-S3-Box
  → Home Assistant Assist pipeline
  → OpenClaw Conversation AlfredPatch conversation agent
  → OpenClaw Gateway /v1/chat/completions
  → OpenClaw agent/session
  → MCPorter server selector `ha`
  → ha-mcp stdio server
  → Home Assistant REST/WebSocket APIs
```

The ESP-S3-Box handles wake word and audio. Home Assistant handles STT/TTS and pipeline routing. OpenClaw handles conversation. ha-mcp, reached through MCPorter, gives the OpenClaw agent Home Assistant tool access.

## Home Assistant base integration

Install the integration as `OpenClaw Conversation AlfredPatch`.

Base integration values:

| Field | Value |
|---|---|
| OpenClaw URL | `http://<openclaw-lan-host>:18789` |
| Gateway Token | Existing OpenClaw Gateway bearer token |
| Verify SSL | Off/false for trusted HTTP LAN deployments |

Do not use `127.0.0.1` unless Home Assistant and OpenClaw are running on the same host/network namespace.

## Conversation subentry

Create a **Conversation agent** subentry, not an AI Task subentry.

Known-good values:

| Field | Value |
|---|---|
| Name | `OpenClaw Voice Bridge` |
| HA MCP server selector or URL | `ha` |
| Agent ID | `main` for first smoke test; later a dedicated agent such as `alfred` |
| Model Override | blank |
| Session Key | `agent:main:homeassistant` for first smoke test; later `agent:alfred:homeassistant` |
| Context Threshold | default |
| Context truncation strategy | default |

The `ha` value is a local MCPorter server selector on the OpenClaw host. It is not a Home Assistant URL.

## Correct prompt pattern

The prompt must use MCPorter selector syntax when the HA MCP field is `ha`:

```text
mcporter call ha.<tool> [args]
```

Do **not** add `--allow-http` when using the configured `ha` selector. `--allow-http` is only for direct cleartext HTTP MCP URLs.

Recommended tool hints:

```text
You are Marvin, a voice assistant connected to Home Assistant through OpenClaw.

Answer in plain text only.
Keep replies short and suitable for text-to-speech.

You have access to Home Assistant through MCPorter using the configured server selector:

ha

To query or control Home Assistant, use mcporter like this:

mcporter call ha.<tool> [args]

Do not use --allow-http with the ha selector.

Useful tools:
- ha_get_overview — summarize Home Assistant and entity counts
- ha_search query="..." — search for entities, automations, scripts, scenes, helpers
- ha_get_state entity_id="..." — get state for an entity
- ha_call_service domain="..." service="..." entity_id="..." — control devices
- ha_list_services domain="..." — list available services

When asked to control a device, search for the entity first if you do not already know the entity_id, then call the appropriate service.

For non-home questions, answer normally and briefly.
```

## OpenClaw host MCPorter setup

The working setup uses a wrapper script on the OpenClaw host:

```bash
#!/usr/bin/env bash
set -euo pipefail
set -a
source <openclaw-env-file>
set +a
exec /usr/local/bin/uvx --python 3.13 --from ha-mcp@7.9.0 ha-mcp
```

The environment file, stored outside this repository, must contain:

```bash
HOMEASSISTANT_URL=<home-assistant-url>
HOMEASSISTANT_TOKEN=<long-lived-access-token>
```

Do not commit these values.

MCPorter server definition:

```bash
mcporter config add ha \
  --command <openclaw-workspace>/bin/ha-mcp-stdio \
  --description "Home Assistant MCP via ha-mcp stdio wrapper" \
  --scope home
```

Verification commands:

```bash
mcporter list ha --status --json --timeout 120000
mcporter call ha.ha_get_overview --timeout 120000 --output json
```

Expected: the first command reports `ok`; the second returns Home Assistant summary data including entity/domain/service counts.

## Optional URL mode

If a client specifically requires an MCP URL rather than an MCPorter selector, run `ha-mcp-web` on the OpenClaw host:

```bash
export MCP_HOST=127.0.0.1
export MCP_PORT=8086
export MCP_SECRET_PATH=/mcp
uvx --python 3.13 --from ha-mcp@7.9.0 ha-mcp-web
```

Then the local URL is:

```text
http://127.0.0.1:8086/mcp
```

Only use this if the component/prompt is actually going to call that URL from the OpenClaw host. For the current working OpenClaw Conversation bridge, the preferred value remains `ha`.

## Assist pipeline

In Home Assistant:

1. Go to **Settings → Voice assistants**.
2. Edit the ESP-S3-Box pipeline.
3. Leave the working wake word, STT, and TTS settings alone.
4. Set **Conversation agent** to `OpenClaw Voice Bridge`.
5. Save/update the pipeline.

Known working state:

- ESP-S3-Box wakes with `Hey Jarvis`.
- A native HA test such as “what time is it” works before switching agents.
- After switching to the OpenClaw conversation agent, the pipeline can answer via OpenClaw.
- ha-mcp/MCPorter path can report Home Assistant entity counts.

## Smoke tests

After saving the pipeline:

```text
Hey Jarvis, what are you connected through?
```

Expected: mentions OpenClaw / Home Assistant bridge.

```text
Hey Jarvis, ask Marvin how many Home Assistant entities I have.
```

Expected: uses `ha_get_overview` through MCPorter/ha-mcp and reports an entity count.

```text
Hey Jarvis, ask Marvin what time it is.
```

Expected: proves the general conversation path still works.

## Known issue: post-response wake-word lag

The working configuration may have a delay after TTS playback before `Hey Jarvis` is accepted again. This appears to be an ESPHome/Assist wake-word restart/cooldown issue rather than an OpenClaw bridge issue.

Track likely fixes in the ESPHome voice assistant configuration:

- Ensure the voice assistant resumes wake-word listening immediately after TTS finishes.
- Inspect `on_tts_end`, `on_end`, and `on_error` automations for delayed restart logic.
- Avoid long media-player/speaker shutdown delays after playback.
- Prefer explicit wake-word restart after response playback if ESPHome config supports it.

Do not change the OpenClaw bridge to solve this unless logs show the conversation stream is not completing.
