# Changelog

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
