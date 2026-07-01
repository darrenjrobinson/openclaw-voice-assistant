# Marvin Voice Assistant — OpenClaw Conversation Bridge As-built

This repository is the Home Assistant custom integration bridge that lets the **Marvin** Assist pipeline send conversation text to **OpenClaw** through the OpenAI-compatible chat completions endpoint.

It is based on `core-runtime/openclaw_conversation` / **OpenClaw Conversation AlfredPatch**.

## Role in the stack

```text
ReSpeaker Core v2 microphone
  → wyoming-satellite on 192.168.6.183:10700
  → Home Assistant Assist pipeline "Marvin"
  → OpenClaw Conversation AlfredPatch
  → OpenClaw Gateway /v1/chat/completions
  → OpenClaw agent/session
```

The voice satellite handles audio transport only. Home Assistant handles wake word, STT, pipeline routing, and TTS. This integration supplies the **conversation agent** that turns recognised text into an OpenClaw chat-completions request.

## As-built values

| Setting | Value |
|---|---|
| Home Assistant pipeline | `Marvin` |
| Satellite | ReSpeaker Core v2 |
| Satellite endpoint | `192.168.6.183:10700` |
| Satellite entity | `assist_satellite.office_respeaker_core_v2` |
| Wake word | `okay_nabu` via openWakeWord |
| STT | Whisper / faster-whisper add-on |
| TTS | Piper `en_GB-alan-medium` |
| OpenClaw LAN URL | `http://192.168.1.37:18789` |
| OpenClaw WSL-local URL | `http://127.0.0.1:18789` |
| Initial Agent ID | `main` |
| Recommended production Agent ID | `alfred` |
| Recommended session key | `agent:alfred:homeassistant` |
| Verify SSL | `false` for HTTP/LAN |

## Why this fork

The useful AlfredPatch behaviour is that the integration routes requests with:

```json
{
  "model": "openclaw:<agent_id>"
}
```

For example:

```json
{
  "model": "openclaw:main"
}
```

or later:

```json
{
  "model": "openclaw:alfred"
}
```

The local OpenClaw Gateway has been validated to accept `openclaw:main` on `/v1/chat/completions`, even though `/v1/models` currently lists slash-style names such as `openclaw/main`.

## Operational recommendation

Use `main` only for the first smoke test. Once the path is proven, create a dedicated OpenClaw agent such as `alfred` and bind Home Assistant to that agent/session. Home automation chatter should not pollute the main Telegram session, because even an android deserves some boundaries.
