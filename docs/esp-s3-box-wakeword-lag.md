# ESP-S3-Box wake-word lag after TTS

This note covers the observed delay after a spoken response before `Hey Jarvis` / the configured wake word is recognised again.

## Status

The OpenClaw bridge is not the likely cause of this delay. Once the response has been generated and returned to Home Assistant, the lag is normally in the ESPHome/Home Assistant voice stack while it tears down playback and restarts wake-word listening.

## Why it happens

Common causes:

1. **No true duplex audio** on many ESP32-S3 voice builds. The microphone/wake-word pipeline is stopped during TTS playback and restarted afterwards.
2. **Wrong event sequencing**. Restarting `micro_wake_word` before playback fully finishes can make the device hear its own TTS output or fail to listen until the audio pipeline settles.
3. **Wake model warm-up**. `micro_wake_word` needs enough fresh audio frames to fill its sliding window before a detection can fire.
4. **CPU/RAM pressure**. Wake-word inference, I2S audio, Home Assistant API traffic, and display/UI tasks all contend for ESP32-S3 resources.

## Recommended ESPHome fixes

### 1. Restart wake word only after the pipeline/audio is finished

If using manual `micro_wake_word` start/stop, ensure wake word restarts only after the voice assistant is no longer running:

```yaml
voice_assistant:
  # ... existing config ...

  on_end:
    - wait_until:
        not:
          voice_assistant.is_running:
    - delay: 100ms
    - micro_wake_word.start:
```

If your configuration uses a `speaker:` component and supports `on_tts_stream_end`, prefer the more precise playback-finished event:

```yaml
voice_assistant:
  # ... existing config ...

  on_tts_stream_end:
    - micro_wake_word.start:
```

Use one clear ownership model. Do not let both Home Assistant and your automations fight over wake-word lifecycle.

### 2. Tune `micro_wake_word`

For lower latency, reduce the sliding window slightly and keep the cutoff high:

```yaml
micro_wake_word:
  task_stack_in_psram: true
  models:
    - model: okay_nabu
      sliding_window_size: 3
      probability_cutoff: 97%
```

Trade-off: lower `sliding_window_size` can increase false accepts. If that happens, raise the probability cutoff or return to the default window.

### 3. Use PSRAM for the wake-word task

On ESP32-S3-Box hardware with PSRAM, this can reduce internal RAM pressure:

```yaml
psram:

micro_wake_word:
  task_stack_in_psram: true
```

### 4. Use current ESPHome firmware

Keep ESPHome current. Later ESPHome releases include voice-assistant and ESP32-S3 performance improvements, including higher default CPU frequency on newer releases and improved speaker/media-player support.

If using a community S3-Box firmware, compare the current stable and development branches. Some community builds have reduced older ADF audio-stack overhead by moving to newer ESPHome speaker/media-player primitives.

## What not to change first

- Do not change OpenClaw conversation routing to solve this; the lag occurs after the response is returned and spoken.
- Do not lower STT/TTS quality before confirming wake-word lifecycle sequencing.
- Do not use `conversation_timeout` as a wake-word-lag fix. It controls conversation context lifetime, not how quickly wake listening resumes.

## Validation tests

After updating ESPHome YAML and flashing the device:

1. Say the wake word and ask a short question.
2. Start a stopwatch when TTS playback ends.
3. Immediately repeat the wake word every ~0.5 seconds.
4. Record the earliest successful detection time.

A good target is sub-second recovery after TTS ends. A 2–3 second dead zone usually indicates wake-word restart sequencing, audio pipeline teardown, or resource contention.

## References

- ESPHome `voice_assistant` docs: https://esphome.io/components/voice_assistant/
- ESPHome `micro_wake_word` docs: https://esphome.io/components/micro_wake_word/
- ESPHome issue #5127: https://github.com/esphome/issues/issues/5127
- ESPHome issue #6719: https://github.com/esphome/issues/issues/6719
- Home Assistant Voice Chapter 10: https://www.home-assistant.io/blog/2025/06/25/voice-chapter-10/
- BigBobbas ESP32-S3-Box3 firmware discussion: https://github.com/BigBobbas/ESP32-S3-Box3-Custom-ESPHome/discussions/135
