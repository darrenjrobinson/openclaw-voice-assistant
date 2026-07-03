"""Constants for the OpenClaw Conversation integration."""

DOMAIN = "openclaw_conversation"
DEFAULT_NAME = "OpenClaw Conversation AlfredPatch"
DEFAULT_CONVERSATION_NAME = "OpenClaw Conversation AlfredPatch"
DEFAULT_AI_TASK_NAME = "OpenClaw AI Task AlfredPatch"

# Config flow fields
CONF_OPENCLAW_URL = "openclaw_url"
CONF_HA_MCP_URL = "ha_mcp_url"
CONF_SESSION_KEY = "session_key"
CONF_AGENT_ID = "agent_id"
CONF_MODEL_OVERRIDE = "model_override"
CONF_VERIFY_SSL = "verify_ssl"

# Defaults
DEFAULT_AGENT_ID = "main"
DEFAULT_MODEL_OVERRIDE = ""
DEFAULT_SESSION_KEY = ""
DEFAULT_VERIFY_SSL = True

# Events
EVENT_CONVERSATION_FINISHED = "openclaw_conversation.conversation.finished"

# Prompt configuration
CONF_PROMPT = "prompt"
DEFAULT_PROMPT = """You are a voice assistant for Home Assistant.

Answer in plain text only.
Respond naturally as a voice assistant.
Prefer a single sentence; use up to 2-3 sentences only when truly necessary.

You have access to Home Assistant via MCPorter and the ha-mcp server.
The MCPorter server selector is: {{ ha_mcp_url | default('ha', true) }}
If that value is blank, use the configured MCPorter server named `ha`.

To control devices, search entities, or manage automations, use:

mcporter call {{ ha_mcp_url | default('ha', true) }}.<tool> [args]

Do not add --allow-http when using the configured `ha` server selector.
Only add --allow-http if you are explicitly calling a cleartext http:// MCP URL directly.

Key tools:
- ha_get_overview — summarize Home Assistant and entity counts
- ha_search query="..." — search for entities, automations, scripts, scenes, and helpers
- ha_get_state entity_id="..." — get state for an entity
- ha_call_service domain="..." service="..." entity_id="..." — control devices
- ha_list_services domain="..." — list available services
- ha_list_floors_areas — list rooms/areas when available

When asked to control a device, search for it first if you don't know the entity_id, then call the appropriate service.

For general knowledge questions not related to the home, answer truthfully using internal knowledge only.

{{user_input.extra_system_prompt | default('', true)}}
"""

# Context management
CONF_CONTEXT_THRESHOLD = "context_threshold"
DEFAULT_CONTEXT_THRESHOLD = 13000
CONTEXT_TRUNCATE_STRATEGIES = [{"key": "clear", "label": "Clear All Messages"}]
CONF_CONTEXT_TRUNCATE_STRATEGY = "context_truncate_strategy"
DEFAULT_CONTEXT_TRUNCATE_STRATEGY = CONTEXT_TRUNCATE_STRATEGIES[0]["key"]
