# Security Policy

## Supported versions

This repository is a Home Assistant custom integration fork. The `main` branch is the supported branch unless a tagged release says otherwise.

## Reporting a vulnerability

Please report security issues privately to the repository owner rather than opening a public issue with exploitable details.

If you are adapting this integration for your own deployment, redact the following from issues, logs, screenshots, and pull requests:

- OpenClaw Gateway tokens
- Home Assistant long-lived access tokens
- ha-mcp private URLs
- Authorization headers
- Real externally reachable hostnames/IPs unless they are intentionally public
- Private assistant prompts containing personal context

## Deployment notes

- Do not expose OpenClaw Gateway, ha-mcp, or Wyoming satellite ports directly to the internet.
- Use trusted LAN, VPN, Tailscale, or HTTPS reverse proxy access patterns.
- Prefer a dedicated OpenClaw voice/home agent with the minimum tools needed for Home Assistant control.
- Treat voice assistants as command surfaces. If the agent can control doors, alarms, or power, configure it accordingly and test failure modes.
