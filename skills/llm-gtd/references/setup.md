# Setup Playbook

**Trigger:** user says `设置 GTD` / `setup GTD` with no extra context → start Step 0 immediately.

Setup is **Agent-only**: ask in chat, pass flags to `init.py`. There is no terminal questionnaire.

Default to **core setup**. Core setup installs the GTD vault contract and Agent instructions. Capture, render, scheduler, messaging, online-doc, automation, backup, and health-check providers can be injected externally or installed as optional provider examples.

## Step 0 — Detect existing installation

```bash
ls ~/Documents/GTD/AGENTS.md ~/Documents/GTD/CLAUDE.md 2>/dev/null
ls "$GTD_VAULT/AGENTS.md" "$GTD_VAULT/CLAUDE.md" 2>/dev/null
```

If found → ask: "已有 LLM-GTD（路径 …）。要 **重跑 setup**（保留 00~07 数据）还是 **健康检查**？" Health check → `doctor.py --json`. Re-run → continue.

Clone repo if missing (store as `$REPO_PATH`):

```bash
git clone https://github.com/shaanguan/LLM-gtd.git ~/LLM-gtd
```

## Step 1 — Preferences (keep it short)

**Round 1 — ask in one message (required before `init.py`):**

1. **Vault 路径？** 默认 `~/Documents/GTD`
2. **使用方式？** `desktop-workspace` 或 `remote-im`（remote-im 主要面向 OpenClaw / Hermes Agent 这类远程 Agent）
3. **是否现在启用可选能力？** capture / render / scheduler / online docs / messaging / backup / automation 可稍后单独注入
4. **「全部默认」可以吗？** — 默认 core setup，稍后按需装工具

**Round 2 — only if user did NOT say `全部默认` / `use defaults`:**

- messaging / 在线文档 provider？没有就选 none；具体 provider 以后也可注入
- 改早报/晚报/周回顾时间？（默认 10:30 / 22:30 / Sun 21:00）
- 要 OKR 吗？（默认开）
- 要单独跟踪 side project 吗？（默认否；若是要问项目名）
- AGENTS.md 里显示的名字/角色？（默认 User / Knowledge Worker）
- 现在启用哪些 capability？capture / render / scheduler / online_docs / messaging / backup / automation

**Never ask — infer automatically:**

- `--agent-platform` → detect current host when possible (`openclaw` / `hermes` / `cursor` / `claude` / `generic`)
- knowledge base → on (default)
- doc sync → off when IM = 暂不接入 / none

## Step 2 — One-click `init.py`

Core setup:

```bash
python3 "$REPO_PATH/tools/setup/init.py" \
  --vault "$VAULT_PATH" \
  --agent-platform "<detected>" \
  --im-platform "<feishu|dingtalk|telegram|wecom|wechat|none>" \
  --morning-time "<HH:MM>" \
  --evening-time "<HH:MM>" \
  --weekly-time "<e.g. Sun 21:00>" \
  --user-name "<name>" \
  --user-role "<role>" \
  --core-only
```

Add when needed: `--disable-okr`, `--disable-doc-sync`, `--enable-side-project`, `--side-project-name "<name>"`.

If the user explicitly wants the bundled provider examples, omit `--core-only` and add only the requested provider flags, such as `--install-quickcapture`.

## Step 3 — QUICKSTART + optional capability providers

1. Confirm `QUICKSTART.html` opened (`init.py` runs `open` on macOS). If headless, tell user to open `$VAULT_PATH/QUICKSTART.html`.
2. If the user chose a bundled local automation provider, verify that provider:

```bash
python3 "$REPO_PATH/tools/setup/create_launchd.py" --vault "$VAULT_PATH" --verify
launchctl list | grep llm-gtd
```

If verify fails, retry install once; then report the provider state accurately.

3. Tell the user (brief):
   - **Obsidian:** Open folder as vault → `$VAULT_PATH`; optional Templater plugin
   - **Agent workspace:** open or add `$VAULT_PATH` as the desktop Agent workspace so `AGENTS.md` loads

## Step 4 — Agent Runtime / integrations

1. Read `$VAULT_PATH/.llm-gtd/setup-report.md`. Read `$VAULT_PATH/.llm-gtd/agent-cron-guide.md` only if it exists.
2. Register morning/evening/weekly routines only if the user enabled a scheduler capability and scheduler tools exist; else report skipped or pending.
3. If online_docs/messaging capability is enabled and provider tools exist: create/connect projections, backfill target IDs in managed files as needed; else report skipped or pending.
4. Run doctor:

```bash
python3 "$REPO_PATH/tools/setup/doctor.py" --vault "$VAULT_PATH" --json
```

## Step 5 — Onboard (required)

> 系统准备好了。第一批待办怎么进？
> **A.** 七天 GTD 冷启动（推荐） **B.** 直接告诉我 **C.** 链接或文件 **D.** 粘贴清单

| Choice | Action |
|---|---|
| **A** | `python3 "$REPO_PATH/tools/setup/import_onboarding.py" --vault "$VAULT_PATH" --repo "$REPO_PATH"` |
| **B/C/D** | One Inbox file per open loop; `status/lifecycle: captured`, `source`, `captured_at`, `clarification_needed: true`; summarize; ask before organizing |

Ask: "还要从别的来源再导入吗？" Then refresh discovered projection providers only.

## Step 6 — Final summary + acceptance

Tell the user:

> - **Vault:** `$VAULT_PATH`（Obsidian + Agent workspace）
> - **QUICKSTART** 应已弹出
> - **可选能力:** 列出已启用 / 跳过 / pending 的 capture、render、scheduler、online_docs、messaging、backup、automation providers
>
> **日常口令:** `早` / `回顾` / `周回顾` / `加到 GTD：…`
>
> **现在试一句:** `加到 GTD：明天整理发票` — 或说 `早` 看第一份 brief。

Setup is not done until the user completes one successful capture or Day 1 onboarding.

Mark `onboard` complete in `.llm-gtd/setup-state.json` when finished.

## Pitfalls

- Collect preferences before `init.py`, including the vault path.
- Present providers as optional capabilities.
- If a provider is enabled, installing it is not enough — verify it.
- IM doc sync needs MCP + doc IDs; missing credentials → pending, not failure.
- Preserve `00~07` during setup.
- Provider examples in this repo are convenience implementations. If an injected provider breaks, use that provider's repair path.
