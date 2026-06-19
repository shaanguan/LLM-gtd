# Scheduler Plugin

Optional Agent framework scheduler adapter.

Current compatibility entrypoint:

- `tools/setup/agent_cron.py`

This plugin generates guidance or adapter payloads for framework-provided scheduler capabilities. It must not claim that jobs were registered unless the active Agent framework tool verifies them.

