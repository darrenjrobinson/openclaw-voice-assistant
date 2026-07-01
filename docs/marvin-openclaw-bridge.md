# Marvin Home Assistant → OpenClaw Text Bridge Guide

This guide documents the Home Assistant side of the Marvin voice assistant bridge to OpenClaw.

## 1. Install via HACS

1. Open **HACS** in Home Assistant.
2. Open the menu → **Custom repositories**.
3. Add this repository URL.
4. Category: **Integration**.
5. Install **OpenClaw Conversation AlfredPatch**.
6. Restart Home Assistant.

## 2. Add the integration

Go to **Settings → Devices & Services → Add Integration** and search for:

```text
OpenClaw Conversation AlfredPatch
```

Use these values for the Marvin LAN build:

| Field | Value |
|---|---|
| OpenClaw URL | `http://192.168.1.37:18789` |
| Gateway Token | Existing OpenClaw gateway token — do not paste into docs |
| Verify SSL | `false` / unchecked |

Use `http://127.0.0.1:18789` only from the OpenClaw host/WSL itself. Home Assistant and the ReSpeaker should use the LAN route.

## 3. Add a conversation agent subentry

After the base integration is added:

1. Open the integration entry.
2. Click **Add** under conversation agents.
3. Configure:

| Field | First smoke test | Recommended final |
|---|---|---|
| Name | `OpenClaw Marvin Bridge` | `OpenClaw Alfred Bridge` |
| HA MCP Server URL | Leave/enter HA MCP URL if device control is required | Same |
| Agent ID | `main` | `alfred` |
| Model Override | blank | blank |
| Session Key | `agent:main:homeassistant` | `agent:alfred:homeassistant` |
| Context threshold | default | default |

Leave **Model Override** blank unless deliberately testing a provider/model. With the override blank, this fork sends `model: openclaw:<agent_id>`.

## 4. Attach to the Assist pipeline

In Home Assistant:

1. Go to **Settings → Voice assistants**.
2. Edit the `Marvin` pipeline.
3. Set **Conversation agent** to the OpenClaw Conversation AlfredPatch agent created above.
4. Keep the existing local components:
   - STT: Whisper / faster-whisper
   - TTS: Piper `en_GB-alan-medium`
   - Wake word: openWakeWord `okay_nabu`

## 5. Validate OpenClaw before configuring HA

From a shell that can reach OpenClaw:

```bash
export OPENCLAW_URL="http://192.168.1.37:18789"
export OPENCLAW_TOKEN="<gateway token>"
python3 scripts/openclaw_smoke_test.py
```

Expected results:

```text
/v1/models: HTTP 200
/v1/chat/completions: HTTP 200
```

The model list may show:

```text
openclaw
openclaw/default
openclaw/main
```

That is fine. The chat completions endpoint has also been validated with colon routing:

```text
openclaw:main
```

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` | Wrong/missing gateway token | Re-enter Gateway Token |
| `Connection refused` | Wrong URL, gateway down, firewall/routing issue | Use `http://192.168.1.37:18789` from LAN; confirm OpenClaw is running |
| HA can reach `/v1/models` but conversation fails | Bad model/agent routing or bad request payload | Test with `scripts/openclaw_smoke_test.py`; start with Agent ID `main` |
| Pipeline replies from wrong assistant | Satellite still bound to `preferred` pipeline/agent | Re-select the conversation agent and pipeline after any rename |
| Wake word detected but no useful reply | Conversation agent not attached to pipeline | Edit `Marvin` pipeline and choose AlfredPatch agent |
| Wake stream flaps open/closed | Satellite audio issue, not this integration | Check `journalctl -u wyoming-satellite -f` on ReSpeaker |
| OpenClaw says tool unavailable | Agent prompt/tool policy issue | Use dedicated `alfred` agent with only required HA tools |

## 7. Security notes

- Keep the OpenClaw gateway token out of Git.
- Use the LAN endpoint only on trusted networks.
- Do not expose OpenClaw Gateway or the ReSpeaker Wyoming port directly to the internet.
- Prefer a dedicated Home Assistant/OpenClaw agent instead of routing HA traffic into the main Telegram session.
