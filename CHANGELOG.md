# Changelog

## v1.1.5

- Added configurable OpenClaw request timeout for Conversation agent subentries.
- Raised the default streaming response timeout from 60 seconds to 300 seconds for long-running voice tasks.
- Kept connection timeout at 10 seconds so unreachable gateways still fail quickly.

## v1.1.4

- Fixed Home Assistant config subentry flows that could open directly at `init` and crash with `Config flow could not be loaded: unknown error` before `self.options` was initialised.
- Changed the HA MCP field from URL-only to free text so it can accept a MCPorter server selector such as `ha`.
- Updated the default prompt for MCPorter selector mode:
  - uses `mcporter call ha.<tool>` style calls
  - removes `--allow-http` for configured selectors
  - updates ha-mcp tool hints to current names such as `ha_search`, `ha_get_overview`, `ha_get_state`, and `ha_call_service`
- Added known-good ESP-S3-Box → Home Assistant → OpenClaw working configuration documentation.
- Updated ha-mcp/MCPorter setup docs to use a stdio wrapper that reads Home Assistant credentials from environment variables instead of embedding tokens in config.

## v1.1.3

- Public repository readiness pass:
  - sanitised live LAN/deployment values from public docs
  - updated HACS and Home Assistant metadata to this repository
  - added SECURITY.md with disclosure and deployment guidance
  - refreshed README for HACS installation and OpenClaw agent routing
  - removed Claude Code workflows that require repository secrets and should not auto-run on a public fork

## v1.1.2

- Added debug logging for effective model selection in conversation requests:
  - logs source (`override` | `agent` | `default`)
  - logs selected model, agent id, and session key
- README updates:
  - documented `Model Override` in Agent Configuration table
  - documented model selection priority and operational recommendation

## v1.1.1

- Added optional `Model Override` field for Conversation agent subentry.
- Model selection priority implemented:
  1. model override
  2. `openclaw:<agent_id>`
  3. `openclaw`
- Added AlfredPatch troubleshooting and migration notes in README.

## v1.1.0

- AlfredPatch baseline known-good release.
- Added custom agent routing support via `openclaw:<agent_id>`.
- Added AlfredPatch branding in integration metadata and defaults.
