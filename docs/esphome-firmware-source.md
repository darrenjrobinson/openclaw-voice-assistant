# ESPHome firmware source for the ESP32-S3-Box-3 satellite

The working ESP32-S3-Box-3 voice satellite was initially flashed with ESP Web Tools from the ESPHome wake-word voice assistant firmware project:

- Upstream source: https://github.com/esphome/wake-word-voice-assistants
- ESP Web Tools framework: https://github.com/esphome/esp-web-tools
- Relevant upstream YAML: `esp32-s3-box-3/esp32-s3-box-3.yaml`
- Relevant factory YAML: `esp32-s3-box-3/esp32-s3-box-3.factory.yaml`

That upstream repository contains the YAML, display assets, factory build workflow, and device-specific ESPHome configuration used for the stock Home Assistant ESP32-S3-Box-3 voice assistant image.

## OpenClaw firmware fork

OpenClaw/Marvin customisation work now lives in a separate firmware fork:

- OpenClaw firmware fork: https://github.com/darrenjrobinson/openclaw-wake-word-voice-assistants
- OpenClaw target YAML: `openclaw-esp32-s3-box-3/openclaw-esp32-s3-box-3.yaml`
- OpenClaw factory YAML: `openclaw-esp32-s3-box-3/openclaw-esp32-s3-box-3.factory.yaml`
- Custom display assets: `openclaw-assets/*.png`
- Custom wake-word model location: `wake-word-models/`

The fork keeps the upstream ESPHome voice-assistant structure but adds a repeatable personalisation path for:

- custom assistant screen imagery
- custom microWakeWord model manifests and TFLite files
- OpenClaw/Marvin defaults
- wake-word latency tuning notes
- a GitHub Actions build path for an OpenClaw ESP32-S3-Box-3 factory image

## ESPHome Dashboard import path

During development, import the OpenClaw YAML directly into ESPHome Dashboard:

```text
github://darrenjrobinson/openclaw-wake-word-voice-assistants/openclaw-esp32-s3-box-3/openclaw-esp32-s3-box-3.yaml@main
```

This lets the user adopt the device and customise YAML locally before compiling/flashing.

## Relationship to the conversation bridge

The firmware and the Home Assistant/OpenClaw conversation bridge are separate concerns:

```text
ESP32-S3-Box-3 firmware
  → Home Assistant Assist pipeline
  → OpenClaw Conversation AlfredPatch integration
  → OpenClaw agent
  → MCPorter `ha`
  → ha-mcp
  → Home Assistant APIs
```

The firmware controls wake word, audio transport, display state, and local ESPHome behaviour. The conversation bridge controls how transcribed text is routed to OpenClaw.

## Custom wake-word path

ESPHome uses the `micro_wake_word` component for on-device wake-word detection. Custom wake words should be trained as microWakeWord models and referenced from YAML, for example:

```yaml
micro_wake_word:
  models:
    - model: github://darrenjrobinson/openclaw-wake-word-voice-assistants/wake-word-models/marvin.json@main
```

Keep a known-good built-in wake word such as `hey_jarvis` enabled until the custom model is tested in the target room.

References:

- ESPHome micro_wake_word docs: https://esphome.io/components/micro_wake_word/
- microWakeWord training project: https://github.com/kahrendt/microWakeWord
- ESPHome model repository: https://github.com/esphome/micro-wake-word-models

## Custom display image path

The upstream YAML loads state images through substitutions such as:

```yaml
idle_illustration_file: https://github.com/.../idle_320_240.png
listening_illustration_file: https://github.com/.../listening_320_240.png
thinking_illustration_file: https://github.com/.../thinking_320_240.png
replying_illustration_file: https://github.com/.../replying_320_240.png
```

The OpenClaw firmware fork redirects these to `openclaw-assets/*.png`. Others can personalise the assistant by replacing those 320×240 PNGs or changing the substitution URLs.

## Post-response wake-word lag

The upstream ESP32-S3-Box-3 YAML already contains important sequencing in `voice_assistant.on_end`: it waits for announcements and speaker playback to finish before restarting on-device `micro_wake_word`.

If lag remains after TTS playback:

- keep current ESPHome / 240 MHz ESP32-S3 build settings
- keep `task_stack_in_psram: true` for `micro_wake_word`
- tune `sliding_window_size` and `probability_cutoff`
- avoid heavyweight display work during wake-word restart
- inspect whether the configured speaker/media-player path delays the `on_end` sequence

See also: `docs/esp-s3-box-wakeword-lag.md`.
