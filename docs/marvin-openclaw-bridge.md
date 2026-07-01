# Marvin Home Assistant → OpenClaw Text Bridge Guide

This guide documents the Home Assistant side of a local voice assistant bridge to OpenClaw.

## 1. Install via HACS

1. Open **HACS** in Home Assistant.
2. Open the menu → **Custom repositories**.
3. Add this repository URL:

   ```text
   https://github.com/darrenjrobinson/openclaw-voice-assistant
   ```

4. Category: **Integration**.
5. Install **OpenClaw Conversation AlfredPatch**.
6. Restart Home Assistant.

## 2. Add the integration

Go to **Settings → Devices & Services → Add Integration** and search for:

```text
OpenClaw Conversation AlfredPatch
```

Use values like these, replacing placeholders with your own deployment details:

| Field | Value |
|---|---|
| OpenClaw URL | `http://<openclaw-host>:18789` |
| Gateway Token | Existing OpenClaw Gateway token — do not paste into docs |
| Verify SSL | `false` / unchecked for trusted HTTP/LAN only |

Use `http://127.0.0.1:18789` only from the OpenClaw host itself. Home Assistant and satellites usually need a LAN-routable address.

## 3. Add a conversation agent subentry

After the base integration is added:

1. Open the integration entry.
2. Click **Add** under conversation agents.
3. Configure:

| Field | First smoke test | Recommended final |
|---|---|---|
| Name | `OpenClaw Voice Bridge` | `OpenClaw House Agent` |
| HA MCP Server URL | Leave blank or enter a private ha-mcp URL if device control is required | Same |
| Agent ID | `main` | `alfred` or another dedicated voice agent |
| Model Override | blank | blank |
| Session Key | `agent:main:homeassistant` | `agent:alfred:homeassistant` |
| Context threshold | default | default |

Leave **Model Override** blank unless deliberately testing a provider/model. With the override blank, this fork sends `model: openclaw:<agent_id>`.

## 4. Attach to the Assist pipeline

In Home Assistant:

1. Go to **Settings → Voice assistants**.
2. Edit your chosen Assist pipeline.
3. Set **Conversation agent** to the OpenClaw Conversation AlfredPatch agent created above.
4. Keep your preferred local components, for example:
   - STT: Whisper / faster-whisper
   - TTS: Piper
   - Wake word: openWakeWord model selected in the pipeline

## 5. Validate OpenClaw before configuring HA

From a shell that can reach OpenClaw:

```bash
export OPENCLAW_URL="http://<openclaw-host>:18789"
export OPENCLAW_TOKEN="<gateway token>"
python3 scripts/openclaw_smoke_test.py
```

Expected results:

```text
/v1/models: HTTP 200
/v1/chat/completions: HTTP 200
```

The model list may show slash-style IDs such as:

```text
openclaw
openclaw/default
openclaw/main
```

That is fine. The chat completions endpoint can also accept colon routing such as:

```text
openclaw:main
```

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` | Wrong/missing Gateway token | Re-enter Gateway Token |
| `Connection refused` | Wrong URL, gateway down, firewall/routing issue | Use a LAN-routable OpenClaw URL; confirm OpenClaw is running |
| HA can reach `/v1/models` but conversation fails | Bad model/agent routing or bad request payload | Test with `scripts/openclaw_smoke_test.py`; start with Agent ID `main` |
| Pipeline replies from wrong assistant | Satellite/pipeline still bound to a different conversation agent | Re-select the conversation agent and pipeline after any rename |
| Wake word detected but no useful reply | Conversation agent not attached to pipeline | Edit the Assist pipeline and choose AlfredPatch agent |
| Wake stream flaps open/closed | Satellite audio issue, not this integration | Check the Wyoming satellite logs |
| OpenClaw says tool unavailable | Agent prompt/tool policy issue | Use a dedicated voice/house agent with only required HA tools |

## 7. Security notes

- Keep the OpenClaw Gateway token out of Git.
- Keep ha-mcp private URLs and Home Assistant long-lived access tokens out of Git.
- Use LAN HTTP endpoints only on trusted networks.
- Do not expose OpenClaw Gateway, ha-mcp, or a Wyoming satellite port directly to the internet.
- Prefer a dedicated Home Assistant/OpenClaw agent instead of routing HA traffic into a human-facing chat session.

## 8. ReSpeaker/Wyoming wake detection instrumentation

If a Wyoming satellite appears connected but the wake word never fires, local event hooks can prove whether Home Assistant is sending lifecycle events back to the satellite.

Example event hooks can log events such as:

```text
startup
streaming-start
streaming-stop
detect
detection
stt-start
stt-stop
transcript
synthesize
tts-start
tts-stop
error
```

Expected healthy wake sequence:

```text
startup
streaming-start
detect
detection
stt-start
stt-stop
transcript
synthesize
tts-start
tts-stop
```

If the sequence stops at `detect`, then:

- Home Assistant is connected to the satellite.
- Home Assistant has instructed the satellite to stream audio for wake detection.
- The satellite audio transport is alive.
- The wake engine did not recognise the phrase.

At that point, inspect the Home Assistant openWakeWord add-on logs. Confirm the loaded model ID exactly matches the pipeline wake word selection. Watch for:

```text
Loaded models: [...]
Receiving audio from client
Detected ...
```

### ReSpeaker mixer note

Some ReSpeaker images can boot with one microphone channel set much lower than the others. Before changing mixer settings, save backups:

```bash
mkdir -p ~/oc-backups
amixer -c 0 scontents > ~/oc-backups/amixer-scontents-before.txt
alsactl -f ~/oc-backups/asound-state-before.state store 0
```

Then inspect and adjust channel levels as appropriate for your hardware:

```bash
amixer -c 0 scontents
amixer -c 0 sset "CH1 volume" <value>
systemctl restart wyoming-satellite
```

### Wake model naming gotcha: `ok_nabu` vs `okay_nabu`

Home Assistant documentation often refers to **ok nabu** for the openWakeWord add-on. Some ESPHome/microWakeWord examples use `okay_nabu`. Do not assume these are interchangeable.

When debugging no-detection cases, use the openWakeWord add-on log as the source of truth:

```text
Loaded models: [...]
```

Then make the Assist pipeline streaming wake word match the loaded model/display entry exactly. A mismatch between `ok_nabu` and `okay_nabu` can leave the satellite connected and streaming forever with no `detection` event.

## 9. ReSpeaker playback fix: use `plughw` not `hw`

After wake detection and STT began working, the ReSpeaker still failed to play TTS audio with:

```text
aplay: set_params:1349: Channels count non available
```

The launcher was using the raw hardware device:

```bash
aplay -D hw:0,1 -r 22050 -f S16_LE -c 1 -t raw
```

That device rejected the mono/channel parameters. The fix was to use ALSA's plugin wrapper so it can perform the required conversion:

```bash
aplay -D plughw:0,1 -r 22050 -f S16_LE -c 1 -t raw
```

Applied in:

```text
/home/marvin/.config/wyoming-satellite/run.sh
```

Backup:

```text
/home/marvin/.config/wyoming-satellite/run.sh.bak.playback.20260701-111121
```

Post-fix validation showed a complete event sequence:

```text
detection input=okay_nabu
stt-start
stt-stop
transcript input=What is tomorrow going to bring?
synthesize input=Sorry, I am not aware of any device called tomorrow going to bring
tts-start
tts-stop
```

The journal showed playback started:

```text
Playing raw data 'stdin' : Signed 16 bit Little Endian, Rate 22050 Hz, Mono
```

…and the previous channel-count error did not repeat.

At this point the wake/STT/TTS transport path is functional. Remaining issues are conversation-agent semantics/routing, for example Home Assistant treating a general phrase as a device-control intent instead of passing it to the intended OpenClaw conversation agent.

