---
name: llm-gtd-setup
description: 一键设置 LLM-GTD 系统（AI 驱动的 GTD 工作流）。当用户说"设置 GTD""setup LLM-GTD""帮我搞 GTD 系统""初始化 GTD"或使用 /llm-gtd-setup 时触发。克隆仓库、问偏好、生成 vault、注册定时任务，全程对话完成。
version: 1.0.0
---

# LLM-GTD Setup

一键在 QoderWork 中设置完整的 AI GTD 系统。

## 触发条件

用户说以下任何一种：
- /llm-gtd-setup
- "设置 GTD" / "setup GTD"
- "帮我搞 GTD 系统"
- "初始化 GTD" / "init GTD"
- "我要用 LLM-GTD"

## Steps

### 1. 克隆仓库

检查本地是否已有 llm-gtd 仓库：

```bash
# 检查常见位置
ls ~/Projects/llm-gtd 2>/dev/null || ls ~/llm-gtd 2>/dev/null
```

如果没有，克隆到 `~/Projects/llm-gtd`：

```bash
mkdir -p ~/Projects
git clone https://github.com/<org>/llm-gtd.git ~/Projects/llm-gtd
```

记住仓库路径为 `$REPO_PATH`。

### 2. 用 AskUserQuestion 问偏好

一次性问以下问题：

**问题 1 — "Vault 位置"**（header: "Vault路径"）
- `~/Documents/GTD`（推荐）
- `~/GTD`
- 自定义路径（Other）

**问题 2 — "功能开关"**（header: "功能", multiSelect: true）
- OKR 追踪 — 工作任务关联目标，周回顾自动对齐进度
- 钉钉同步 — 排期表+每日安排自动推送钉钉文档
- 副项目隔离 — 个人项目单独追踪，不混入工作输出
- 知识库引用 — Agent 处理 Inbox 时参考 GTD 方法论 wiki

**问题 3 — "定时播报"**（header: "早报时间"）
- 09:00
- 10:00
- 10:30（推荐）
- 自定义（Other）

### 3. 运行 init.py 生成 vault

根据用户回答构建参数：

```bash
python3 $REPO_PATH/setup/init.py --vault "$VAULT_PATH" --non-interactive
```

然后用 Python 或 Edit 工具修改生成的 AGENTS.md：
- 替换 `{{user.name}}` 为用户名（可以从 QoderWork 上下文获取，或问用户）
- 替换 `{{user.role}}` 为用户角色
- 根据功能开关，手动处理 `<!-- IF feature.X -->` 块（init.py --non-interactive 默认全开，需要按用户选择关闭未选的）

如果 init.py 已经跑过（vault 已存在），告诉用户"检测到已有 vault，是否重新初始化？"

### 4. 设置 QoderWork 工作文件夹

将 vault 路径设为 QoderWork 当前工作目录。使用 QoderWork action 工具（如可用），或者提示用户在界面上选择文件夹。

### 5. 注册定时任务

用 `qoder_cron` 注册 4 个任务（根据用户选择的时间调整 cron expr）：

**早间播报**（默认 10:30）：
```
name: "GTD 早间播报"
schedule: { kind: "cron", expr: "30 10 * * *", tz: "Asia/Shanghai" }
payload.message: "执行 GTD 早间播报流程：1)扫 00-Inbox 列新增 2)扫 02-NA 筛 due<=今日，列 MIT(<=3) 3)筛未来7天临近截止 4)筛无due未定计划 5)扫 03-WF 按owner报等待天数(>7天建议催) 6)从 knowledge/gtd/wiki/ 抽1篇给一句 insight。完成后将播报内容发送到IM。"
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: "skip"
```

**晚间回顾**（默认 22:30）：
```
name: "GTD 晚间回顾"
schedule: { kind: "cron", expr: "30 22 * * *", tz: "Asia/Shanghai" }
payload.message: "执行 GTD 晚间回顾：1)列今日due项询问完成状态(等用户确认再归档) 2)扫Inbox按决策树处理 3)本周归档项更新周报 4)vault变动则跑 python3 export_dashboard.py 5)确认完成的写07-Achievements。完成后通知用户。"
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: "skip"
```

**周回顾**（默认 Sun 21:00）：
```
name: "GTD 周回顾"
schedule: { kind: "cron", expr: "0 21 * * 0", tz: "Asia/Shanghai" }
payload.message: "执行GTD周回顾(7步/1h上限)：1)确认Inbox清零 2)过NA—仍有效? 3)过Projects—每个有下一步? 4)过WF—>7天建议催 5)过Someday—是否激活 6)定下周 7)OKR对齐。通知用户开始回顾对话。"
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: "run_latest"
```

**每日快照**（23:55 自动 git commit）：
```
name: "GTD Vault 快照"
schedule: { kind: "cron", expr: "55 23 * * *", tz: "Asia/Shanghai" }
payload.message: "在vault目录执行: cd $VAULT_PATH && git add -A && git diff --cached --quiet || git commit -m 'daily snapshot'。静默执行，无需通知用户。"
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: "skip"
```

注意：如果 vault 还没有 git init，先执行：
```bash
cd "$VAULT_PATH" && git init && git add -A && git commit -m "initial vault setup"
```

### 6. 运行 doctor 验证

```bash
python3 $REPO_PATH/setup/doctor.py --vault "$VAULT_PATH"
```

确认零 error 零 warning。

### 7. 告知用户完成 + 唯一手动步

输出类似：

> ✅ LLM-GTD 设置完成！
>
> - Vault: `$VAULT_PATH`
> - 功能: OKR / 钉钉 / 知识库（根据实际）
> - 定时任务: 早 10:30 / 晚 22:30 / 周日 21:00 / 快照 23:55
>
> **还有一步需要你手动做**：打开 Obsidian → 左下角 "Open another vault" → "Open folder as vault" → 选择上面的路径。这样你可以在 Obsidian 里浏览笔记。
>
> 不过即使不开 Obsidian，系统也能正常工作 —— 我直接读写文件。
>
> **现在可以试试**：
> - 对我说"帮我记一下：买咖啡豆"
> - 或者说"帮我看看 Inbox"
> - 或者等明天早上收到第一次播报 ☀️

## Pitfalls

- 不要把 vault 建在仓库目录内（llm-gtd/ 是模板仓库，vault 是用户数据，要分开）
- `contextDirs` 指向 vault（AGENTS.md 所在处），不是 repo
- 如果用户已有 Obsidian vault 想复用，init.py 不会覆盖已有文件，可以安全执行
- 如果 qoder_cron 注册失败（比如权限问题），告诉用户手动在 QoderWork 定时任务面板创建
- 钉钉功能开启后，需要用户后续自己填 nodeId（AGENTS.md §4），提醒一下

## Verification

- `doctor.py` 报告 0 error / 0 warning
- 在 vault 里 `ls "00 - Inbox/"` 能看到目录
- AGENTS.md 存在且无 `{{` 残留
- `qoder_cron list` 能看到 4 个新任务
