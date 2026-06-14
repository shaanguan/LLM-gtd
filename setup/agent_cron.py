#!/usr/bin/env python3
"""
Agent cron job specs for LLM-GTD.

Platform-neutral job definitions. Platform-specific CLI examples are generated
only when requested via --platform; generic is the default.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AgentCronJob:
    key: str
    name: str
    schedule: str
    trigger: str
    flow: str


def build_runtime_prompt(vault_path: str, trigger: str, flow: str) -> str:
    vault = str(Path(vault_path).expanduser().resolve())
    return (
        "LLM-GTD scheduled runtime task.\n"
        f"Vault path: {vault}\n"
        f"Read {vault}/AGENTS.md first (or {vault}/CLAUDE.md if AGENTS.md is absent) and follow it exactly.\n"
        f"Run the {flow} flow from vault data only. Do not invent tasks or deadlines.\n"
        f"Equivalent user trigger: {trigger}\n"
        "Before reporting, run export_dashboard.py if vault files changed.\n"
        "Keep the delivery concise."
    )


def default_jobs(
    vault_path: str,
    morning: str = "30 10 * * *",
    evening: str = "30 22 * * *",
    weekly: str = "0 21 * * 0",
) -> list[AgentCronJob]:
    return [
        AgentCronJob(
            key="morning",
            name="GTD Morning Brief",
            schedule=morning,
            trigger="morning / 早",
            flow="morning brief",
        ),
        AgentCronJob(
            key="evening",
            name="GTD Evening Review",
            schedule=evening,
            trigger="review / 回顾",
            flow="evening review",
        ),
        AgentCronJob(
            key="weekly",
            name="GTD Weekly Review",
            schedule=weekly,
            trigger="weekly / 周回顾",
            flow="weekly review",
        ),
    ]


def hermes_cli_commands(vault_path: str, timezone: str = "Asia/Shanghai") -> list[str]:
    commands = []
    for job in default_jobs(vault_path):
        prompt = build_runtime_prompt(vault_path, job.trigger, job.flow)
        prompt_escaped = prompt.replace('"', '\\"')
        commands.append(
            f'hermes cron create "{job.schedule}" "{prompt_escaped}" '
            f'--skill llm-gtd --name "{job.name}" --deliver origin'
        )
    return commands


def hermes_cronjob_tool_specs(vault_path: str) -> list[dict[str, str]]:
    specs = []
    for job in default_jobs(vault_path):
        specs.append({
            "name": job.name,
            "schedule": job.schedule,
            "skill": "llm-gtd",
            "deliver": "origin",
            "prompt": build_runtime_prompt(vault_path, job.trigger, job.flow),
        })
    return specs


def openclaw_cli_commands(vault_path: str, timezone: str = "Asia/Shanghai") -> list[str]:
    commands = []
    for job in default_jobs(vault_path):
        prompt = build_runtime_prompt(vault_path, job.trigger, job.flow)
        prompt_escaped = prompt.replace('"', '\\"')
        commands.append(
            f'openclaw cron add --name "{job.name}" --cron "{job.schedule}" --tz "{timezone}" '
            f'--session isolated --message "{prompt_escaped}" --announce'
        )
    return commands


def write_agent_cron_guide(vault_path: Path, platform: str = "generic") -> Path:
    vault = str(vault_path.expanduser().resolve())
    guide = vault_path / ".llm-gtd" / "agent-cron-guide.md"
    lines = [
        "# LLM-GTD Agent Cron Guide",
        "",
        "These jobs wake your Agent for morning brief, evening review, and weekly review.",
        "They are separate from macOS launchd jobs (Dashboard refresh / git snapshot).",
        "",
        f"Vault: `{vault}`",
        f"Platform: `{platform}`",
        "",
        "## Required jobs",
        "",
    ]
    for job in default_jobs(vault):
        lines.extend([
            f"### {job.name}",
            f"- Schedule: `{job.schedule}`",
            f"- Trigger: `{job.trigger}`",
            f"- Prompt:",
            "```text",
            build_runtime_prompt(vault, job.trigger, job.flow),
            "```",
            "",
        ])

    if platform == "hermes":
        lines.extend([
            "## Hermes",
            "",
            "Prefer the Hermes `cronjob` tool in chat. Create one job per entry below using the given schedule, prompt, skill, and delivery target.",
            "",
            "```json",
            json.dumps(hermes_cronjob_tool_specs(vault), indent=2, ensure_ascii=False),
            "```",
            "",
            "If your Hermes installation also exposes a CLI, these commands are equivalent examples:",
            "",
        ])
        lines.extend(f"- `{cmd}`" for cmd in hermes_cli_commands(vault))
        lines.extend([
            "",
            "Verify: `hermes cron list`",
            "Hermes gateway must be running for jobs to fire: `hermes gateway`",
        ])
    elif platform == "openclaw":
        lines.extend(["## OpenClaw CLI", ""])
        lines.extend(f"- `{cmd}`" for cmd in openclaw_cli_commands(vault))
        lines.extend([
            "",
            "Verify: `openclaw cron list`",
            "OpenClaw gateway/cron must be enabled in `~/.openclaw/cron/jobs.json`.",
        ])
    else:
        lines.extend([
            "## Generic (platform-neutral)",
            "",
            "Register equivalent agent cron jobs in your platform scheduler.",
            "Each prompt must be self-contained and load the `llm-gtd` skill or vault instructions.",
            "",
            "Known platform examples (use what applies to you):",
            "",
            "### Hermes",
            "",
            "Prefer the Hermes `cronjob` tool with the job data from `agent_cron.py --json`.",
            "Use the CLI examples only when your Hermes install exposes `hermes cron`.",
            "",
        ])
        lines.extend(f"- `{cmd}`" for cmd in hermes_cli_commands(vault))
        lines.extend([
            "",
            "Verify: `hermes cron list`",
            "",
            "### OpenClaw",
            "",
        ])
        lines.extend(f"- `{cmd}`" for cmd in openclaw_cli_commands(vault))
        lines.extend([
            "",
            "Verify: `openclaw cron list`",
            "",
            "If your platform has no scheduler, use on-demand triggers: `早`, `回顾`, `周回顾`.",
        ])

    guide.parent.mkdir(parents=True, exist_ok=True)
    guide.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return guide


def detect_agent_cron_status(platform: str) -> dict[str, str]:
    """Best-effort detection via platform CLIs. Returns per-job status."""
    statuses = {job.key: "unknown" for job in default_jobs("/tmp")}
    output = ""

    if platform == "hermes":
        try:
            result = subprocess.run(
                ["hermes", "cron", "list"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            output = result.stdout.lower()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {key: "cli_unavailable" for key in statuses}
    elif platform == "openclaw":
        try:
            result = subprocess.run(
                ["openclaw", "cron", "list"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            output = result.stdout.lower()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {key: "cli_unavailable" for key in statuses}
    else:
        return statuses

    for job in default_jobs("/tmp"):
        if job.name.lower() in output or job.key in output:
            statuses[job.key] = "ok"
        else:
            statuses[job.key] = "missing"
    return statuses


def summarize_agent_cron(platform: str) -> str:
    statuses = detect_agent_cron_status(platform)
    if all(value == "cli_unavailable" for value in statuses.values()):
        return "manual_verify"
    if all(value == "ok" for value in statuses.values()):
        return "ok"
    if any(value == "ok" for value in statuses.values()):
        return "partial"
    if any(value == "missing" for value in statuses.values()):
        return "missing"
    return "unknown"


def jobs_json(vault_path: str, platform: str) -> str:
    payload = {
        "platform": platform,
        "vault_path": str(Path(vault_path).expanduser().resolve()),
        "jobs": [
            {
                "key": job.key,
                "name": job.name,
                "schedule": job.schedule,
                "trigger": job.trigger,
                "prompt": build_runtime_prompt(vault_path, job.trigger, job.flow),
            }
            for job in default_jobs(vault_path)
        ],
        "hermes_cli": hermes_cli_commands(vault_path),
        "hermes_cronjob_tool": hermes_cronjob_tool_specs(vault_path),
        "openclaw_cli": openclaw_cli_commands(vault_path),
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="LLM-GTD agent cron helpers")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--platform", default="generic", choices=["generic", "hermes", "openclaw", "cursor", "claude"])
    parser.add_argument("--write-guide", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--detect", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if args.write_guide:
        path = write_agent_cron_guide(vault, args.platform)
        print(path)
    if args.json:
        print(jobs_json(str(vault), args.platform))
    if args.detect:
        print(summarize_agent_cron(args.platform))
    if not (args.write_guide or args.json or args.detect):
        print(jobs_json(str(vault), args.platform))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
