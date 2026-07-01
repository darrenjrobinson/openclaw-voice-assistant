# Notice and Provenance

This project, **OpenClaw Voice Assistant**, is derived from the OpenClaw Home Assistant conversation integration lineage below.

## Upstream lineage

- Original project: <https://github.com/Djelibeybi/openclaw_conversation>
- AlfredPatch fork used as the initial base: <https://github.com/core-runtime/openclaw_conversation>
- Marvin/OpenClaw Voice Assistant repository: <https://github.com/darrenjrobinson/openclaw-voice-assistant>

## Why this repository exists

This repository is the canonical home for the Marvin/OpenClaw voice assistant build: a Home Assistant local voice pipeline connected to OpenClaw through the OpenAI-compatible chat-completions gateway.

The base AlfredPatch fork was selected because it supports OpenClaw agent routing by sending:

```json
{
  "model": "openclaw:<agent_id>"
}
```

That behaviour lets Home Assistant target a dedicated OpenClaw house/voice agent instead of falling back to the default or main session.

## Marvin customisations

This repository adds and will continue to maintain:

- Marvin voice assistant as-built documentation.
- Home Assistant / HACS configuration guidance.
- OpenClaw gateway smoke-test tooling.
- Deployment notes for ReSpeaker Core v2 and future satellites.
- Future customisations for dedicated OpenClaw voice/house agents.

## License

The original license is retained. See `LICENSE`.
