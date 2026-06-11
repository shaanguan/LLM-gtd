# Agent Setup Guide

> This file is for the AI agent (QoderWork) to read when a user asks to set up LLM-GTD.
> It is NOT a user-facing document — it's operational instructions for the agent.

## When to use this

User says anything like:
- "帮我设置 LLM-GTD"
- "setup GTD"
- "我要用这个 GTD 系统"
- "帮我初始化"

## Setup flow (agent executes this)

### Step 1: Ask preferences (use AskUserQuestion)

Ask these questions in ONE batch:

**Q1: Vault 位置**
- `~/Documents/GTD` (recommended)
- Custom path

**Q2: 功能开关** (multi-select)
- OKR 追踪（工作任务关联目标）
- 钉钉文档同步（排期表+每日安排自动更新）
- 副项目隔离（个人项目不混入工作输出）
- GTD 知识库引用（Agent 处理 Inbox 时参考方法论）

**Q3: 定时任务时间**
- 早间播报时间（默认 10:30）
- 晚间回顾时间（默认 22:30）
- 周回顾（默认 Sun 21:00）

### Step 2: Run init.py

```bash
python3 <repo-path>/setup/init.py \
  --vault "<user-chosen-path>" \
  --non-interactive
```

Note: Since we already asked the questions via AskUserQuestion, pass `--non-interactive`
and then manually render AGENTS.md with the user's answers. Alternatively, run init.py
interactively by piping answers — but `--non-interactive` + post-edit is cleaner.

After running with `--non-interactive`, edit the generated AGENTS.md to fill in the
user's actual answers (name, role, feature flags, cron times).

Alternatively, just run the full init flow directly in Python:
1. Copy vault-template/ to the target path
2. Render AGENTS.md (replace placeholders + strip disabled conditionals)
3. Create .llm-gtd/ state directory

### Step 3: Set QoderWork working folder

Use the QoderWork action tool to select the vault as the working folder:
```
mcp__builtin_qoderwork__action: key="workspace.folder", action="update", params={path: "<vault-path>"}
```
(Check available actions first via query)

### Step 4: Register cron jobs

Use `qoder_cron` to create scheduled tasks:

```python
# Morning brief
qoder_cron(action="add", job={
    "name": "GTD 早间播报",
    "schedule": {"kind": "cron", "expr": "30 10 * * *", "tz": "Asia/Shanghai"},
    "payload": {
        "kind": "agentTurn",
        "message": "执行 GTD 早间播报流程：1)扫 Inbox 列新增 2)扫 NA 筛 due<=今日 列 MIT(<=3) 3)筛未来 7 天临近截止 4)筛无 due 未定计划 5)扫 WF 按 owner 报等待天数 6)知识库抽 1 篇给一句 insight。完成后将播报内容发送到小Q。",
        "contextDirs": ["<vault-path>"]
    },
    "missedRunPolicy": "skip"
})

# Evening review
qoder_cron(action="add", job={
    "name": "GTD 晚间回顾",
    "schedule": {"kind": "cron", "expr": "30 22 * * *", "tz": "Asia/Shanghai"},
    "payload": {
        "kind": "agentTurn",
        "message": "执行 GTD 晚间回顾流程：1)列今日 due 询问完成 2)扫 Inbox 按决策树处理 3)本周归档项更新周报 4)vault 有变动则跑 export_dashboard.py 刷新渲染层 5)确认完成的写 Achievement。完成后通过小Q通知用户。",
        "contextDirs": ["<vault-path>"]
    },
    "missedRunPolicy": "skip"
})

# Weekly review
qoder_cron(action="add", job={
    "name": "GTD 周回顾",
    "schedule": {"kind": "cron", "expr": "0 21 * * 0", "tz": "Asia/Shanghai"},
    "payload": {
        "kind": "agentTurn",
        "message": "执行 GTD 周回顾流程（7步,1小时上限）：1)确认Inbox清零 2)过NA是否仍有效 3)过Projects每个是否有下一步 4)过WF超7天建议催 5)过Someday是否激活 6)定下周基于due+项目状态 7)重温OKR对比进展。完成后通过小Q通知用户开始回顾对话。",
        "contextDirs": ["<vault-path>"]
    },
    "missedRunPolicy": "run_latest"
})

# Git snapshot (nightly backup)
qoder_cron(action="add", job={
    "name": "GTD Vault 快照",
    "schedule": {"kind": "cron", "expr": "55 23 * * *", "tz": "Asia/Shanghai"},
    "payload": {
        "kind": "agentTurn",
        "message": "在 vault 目录执行 git add -A && git commit -m 'daily snapshot' （如果有变更的话）。这是自动备份，不需要通知用户。",
        "contextDirs": ["<vault-path>"]
    },
    "missedRunPolicy": "skip"
})
```

### Step 5: Run doctor

```bash
python3 <repo-path>/setup/doctor.py --vault "<vault-path>"
```

Report results to user.

### Step 6: Guide user for Obsidian (the one manual step)

Tell the user:
> 最后一步需要你手动操作：打开 Obsidian → 左下角"Open another vault" → "Open folder as vault" → 选择 `<vault-path>`。
> 这样你就能在 Obsidian 里浏览和手动编辑 vault 了。不过即使不开 Obsidian，GTD 系统也能正常工作 — Agent 直接读写文件。

### Step 7: Confirm success

Tell the user:
> 设置完成！从现在开始：
> - 每天 10:30 你会收到早间播报
> - 随时可以对我说"帮我记一下..."来快速 capture
> - 说"帮我看看 Inbox"我来帮你处理收集箱
> - 打开 Dashboard.html 看全局状态

## Important notes for the agent

- NEVER hardcode the user's real name, company, or personal info into any file that gets committed back to the llm-gtd repo
- The vault is user-local; the repo is shared/open-source — keep them separate
- If the user hasn't cloned llm-gtd yet, clone it to a reasonable location first (e.g. `~/Projects/llm-gtd`)
- The `contextDirs` in cron jobs should point to the VAULT path (where AGENTS.md lives), NOT the repo path
