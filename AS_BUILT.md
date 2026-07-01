# Marvin Voice Assistant — OpenClaw Conversation Bridge As-built

This repository contains the Home Assistant custom integration bridge that lets a local Assist pipeline send conversation text to **OpenClaw** through the OpenAI-compatible chat-completions endpoint.

It is based on the `openclaw_conversation` lineage and the **OpenClaw Conversation AlfredPatch** routing behaviour.

## Role in the stack

```text
Voice satellite microphone
  → Wyoming satellite or other Home Assistant Assist input
  → Home Assistant Assist pipeline
  → OpenClaw Conversation AlfredPatch
  → OpenClaw Gateway /v1/chat/completions
  → OpenClaw agent/session
```

The voice satellite handles audio transport only. Home Assistant handles wake word, STT, pipeline routing, and TTS. This integration supplies the **conversation agent** that turns recognised text into an OpenClaw chat-completions request.

## Reference values

These are intentionally generic so the public repository does not leak a live LAN layout. Replace them with your own values during deployment.

| Setting | Example value |
|---|---|
| Home Assistant pipeline | `Marvin` |
| Satellite | ReSpeaker Core v2 or another Wyoming-compatible satellite |
| Satellite endpoint | `<satellite-host>:10700` |
| Satellite entity | `assist_satellite.<your_satellite>` |
| Wake word | `ok_nabu` / your selected openWakeWord model |
| STT | Whisper / faster-whisper add-on |
| TTS | Piper or another Home Assistant TTS engine |
| OpenClaw LAN URL | `http://<openclaw-host>:18789` |
| OpenClaw local URL | `http://127.0.0.1:18789` when testing on the OpenClaw host |
| Initial Agent ID | `main` |
| Recommended production Agent ID | `alfred` or another dedicated voice agent |
| Recommended session key | `agent:alfred:homeassistant` |
| Verify SSL | `false` only for trusted HTTP/LAN deployments |

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

OpenClaw may list slash-style model names such as `openclaw/main` from `/v1/models`, while the chat completions endpoint can still accept the colon routing form used by this integration.

## Operational recommendation

Use `main` only for the first smoke test. Once the path is proven, create a dedicated OpenClaw agent such as `alfred` and bind Home Assistant to that agent/session. Home automation chatter should not pollute the main chat session, because even an android deserves some boundaries.
