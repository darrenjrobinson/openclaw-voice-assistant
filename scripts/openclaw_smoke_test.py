#!/usr/bin/env python3
"""Smoke test an OpenClaw OpenAI-compatible chat completions endpoint.

Environment:
  OPENCLAW_URL     Base URL, e.g. http://127.0.0.1:18789 or http://<openclaw-host>:18789
  OPENCLAW_TOKEN   Gateway bearer token
  OPENCLAW_MODEL   Optional model, default openclaw:main
  OPENCLAW_AGENT   Optional x-openclaw-agent-id header, default main
  OPENCLAW_SESSION Optional x-openclaw-session-key header
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def request(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, str]:
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    agent = os.environ.get("OPENCLAW_AGENT", "main")
    session = os.environ.get("OPENCLAW_SESSION", "")
    if agent:
        headers["x-openclaw-agent-id"] = agent
    if session:
        headers["x-openclaw-session-key"] = session

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        text = err.read().decode("utf-8", errors="replace")
        return err.code, text
    except urllib.error.URLError as err:
        fail(f"cannot connect to {url}: {err}")


def main() -> int:
    base_url = os.environ.get("OPENCLAW_URL", "http://127.0.0.1:18789").rstrip("/")
    token = os.environ.get("OPENCLAW_TOKEN")
    model = os.environ.get("OPENCLAW_MODEL", "openclaw:main")

    if not token:
        fail("OPENCLAW_TOKEN is required")

    print(f"OpenClaw URL: {base_url}")
    print(f"Model: {model}")

    status, text = request("GET", f"{base_url}/v1/models", token)
    print(f"/v1/models: HTTP {status}")
    if status != 200:
        print(text[:1000])
        return 2

    try:
        models = json.loads(text).get("data", [])
        print("Models:", ", ".join(m.get("id", "<unknown>") for m in models))
    except json.JSONDecodeError:
        print("WARNING: /v1/models did not return JSON")

    body = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": "Reply with exactly: bridge-ok"},
            {"role": "user", "content": "OpenClaw bridge smoke test"},
        ],
    }
    status, text = request("POST", f"{base_url}/v1/chat/completions", token, body)
    print(f"/v1/chat/completions: HTTP {status}")
    if status != 200:
        print(text[:2000])
        return 3

    try:
        payload = json.loads(text)
        content = payload["choices"][0]["message"].get("content", "")
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as err:
        print(text[:2000])
        fail(f"unexpected chat completions response shape: {err}", 4)

    print("Response:", content.strip())
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
