---
name: llm-gtd-setup
description: "LLM-GTD — 让 AI 做你的 GTD 秘书。每天早上推送今日重点，晚上帮你回顾归档，每周自动清理系统。你只管随时把想法丢给它，剩下的它来管。说\"设置 GTD\"或 /llm-gtd-setup 开始安装。"
version: 1.5.0
---

# LLM-GTD Setup

一键设置完整的 AI GTD 系统（Obsidian vault + 定时播报 + IM 推送 + 知识库）。

## 触发条件

用户说以下任何一种：
- /llm-gtd-setup
- "设置 GTD" / "setup GTD"
- "帮我搞 GTD 系统"
- "初始化 GTD" / "init GTD"
- "我要用 LLM-GTD"

**行为规则**：用户只输入 skill 名称（如 `/llm-gtd-setup`）而不附加其他说明时，直接开始 Step 1，无需再问"你要做什么"。

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
git clone https://github.com/shaanguan/LLM-gtd.git ~/Projects/LLM-gtd
```

记住仓库路径为 `$REPO_PATH`。

### 2. 问用户偏好

一次性问以下 4 个问题（用环境提供的交互式提问工具，如 AskUserQuestion）：

**问题 1 — Vault 位置**
- `~/Documents/GTD`（推荐）
- `~/GTD`
- 自定义路径

**问题 2 — IM 平台**
- 钉钉 — 阿里系，支持文档同步+群消息推送
- 飞书 — 字节系，支持文档同步+群消息推送
- 企业微信 — 腾讯系，支持机器人消息推送
- 微信 — 个人用，仅消息推送（无文档同步）

**问题 3 — 功能开关**（多选）
- OKR 追踪 — 工作任务关联目标，周回顾自动对齐进度
- 文档同步 — 排期表+每日安排自动推送到团队共享文档（需钉钉或飞书）
- 副项目隔离 — 个人项目单独追踪，不混入工作输出
- 知识库引用 — Agent 处理 Inbox 时参考 GTD 方法论 wiki

**问题 4 — 定时播报时间**
- 09:00
- 10:00
- 10:30（推荐）
- 自定义

### 3. 运行 init.py 生成 vault

根据用户回答构建参数：

```bash
python3 $REPO_PATH/setup/init.py --vault "$VAULT_PATH" --non-interactive
```

然后修改生成的 AGENTS.md：
- 替换 `{{user.name}}` 为用户名（从环境上下文获取或问用户）
- 替换 `{{user.role}}` 为用户角色
- 根据功能开关，处理 `<!-- IF feature.X -->` 条件渲染块（init.py --non-interactive 默认全开，按用户选择关闭未选的）

如果 init.py 已经跑过（vault 已存在），告诉用户"检测到已有 vault，是否重新初始化？"

### 3.5. 安装 QuickCapture（macOS 用户）

在 vault 生成后，安装全局快捷键捕获工具：

```bash
python3 $REPO_PATH/setup/install_quickcapture.py --vault "$VAULT_PATH" --repo "$REPO_PATH"
```

此步骤会：
- 检测 Swift toolchain（无则回退 JXA 版）
- 编译并安装 QuickCapture.bin 到 vault/Scripts/
- 注册 LaunchAgent（登录自动启动）
- 提示用户授权辅助功能（首次 Cmd+I 时 macOS 弹窗）

非 macOS 用户自动跳过此步。

### 3.6. 安装 Dashboard 快捷方式（macOS 用户）

在 vault 生成后，创建 Dashboard.app（双击直接打开 Dashboard.html）：

```bash
python3 $REPO_PATH/setup/create_app.py "$VAULT_PATH" "$REPO_PATH"
```

成功后会在 `~/Applications/GTD Dashboard.app` 生成一个可执行的 .app 包。

**验证**：运行 `ls ~/Applications/GTD\ Dashboard.app/Contents/MacOS/launch`，确认文件存在。如果失败（比如路径问题），告诉用户并提供手动方案："你可以在 Finder 里创建一个快捷方式指向 vault 里的 Dashboard.html"。

非 macOS 用户跳过此步。

### 4. IM 频道连接检测

检查用户选的 IM 平台是否已连接。

- 已连接 → 继续
- 未连接 → 引导用户去设置页面连接对应 IM 平台，等连好后继续

同时检测是否有可用的 IM 推送通道：
- 有 → cron 结果会推到这里
- 没有 → 建议用户开启："建议开启 IM 推送通道，这样我能主动把播报推给你，否则你得自己打开 AI 助手来看结果。"

### 5. 文档创建（钉钉/飞书用户，且开启了文档同步时）

如果用户选了"文档同步"且 IM 平台是钉钉或飞书，进入此步。用自然语言征询：

> "文档同步开好了。我推荐配套创建两个共享文档：
>
> **排期表** — 我每周把你的项目排期推上去，同事能直接看到你这周做什么、什么时候交付，减少被追问'这个啥时候好'。
>
> **每日安排** — 每天早间播报把今日 MIT + 会议 + 等待回复的事贴上去，相当于你的对外'今日状态'。
>
> 这两个适合你吗？还是你有别的想推到文档的内容？"

根据用户回答和平台：
- **钉钉用户** → 用钉钉文档 MCP 创建文档，拿到 nodeId
- **飞书用户** → 用飞书文档 MCP 创建文档，拿到 token
- 用户只要其中一个 → 只创建那个
- 用户说想要别的（比如"周报""会议纪要"）→ 按他说的创建
- 用户说不需要 → 跳过

创建完成后，将文档 ID 写入 AGENTS.md §4 对应位置。

**企业微信/微信用户**：跳过此步（这两个平台无文档能力），AGENTS.md §4 文档同步段落自动移除。

### 6. 设置工作文件夹

将 vault 路径设为 AI 助手当前工作目录/项目文件夹。提示用户在界面上选择文件夹（当前各平台均需手动操作）。

### 7. 注册定时任务

用环境提供的定时任务工具注册 4 个任务（根据用户选择的时间调整 cron 表达式）：

**早间播报**（默认 10:30）：
```yaml
name: "GTD 早间播报"
schedule: "30 10 * * *"  # Asia/Shanghai
prompt: >
  执行 GTD 早间播报流程：
  1)扫 00-Inbox 列新增
  2)扫 02-NA 筛 due<=今日，列 MIT(<=3)
  3)筛未来7天临近截止
  4)筛无due未定计划
  5)扫 03-WF 按owner报等待天数(>7天建议催)
  6)从 knowledge/gtd/wiki/ 抽1篇给一句 insight
  完成后将播报内容发送到IM。
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: skip
```

**晚间回顾**（默认 22:30）：
```yaml
name: "GTD 晚间回顾"
schedule: "30 22 * * *"  # Asia/Shanghai
prompt: >
  执行 GTD 晚间回顾：
  1)列今日due项询问完成状态(等用户确认再归档)
  2)扫Inbox按决策树处理
  3)本周归档项更新周报
  4)vault变动则跑 python3 export_dashboard.py
  5)确认完成的写07-Achievements
  完成后通知用户。
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: skip
```

**周回顾**（默认 Sun 21:00）：
```yaml
name: "GTD 周回顾"
schedule: "0 21 * * 0"  # Asia/Shanghai
prompt: >
  执行GTD周回顾(7步/1h上限)：
  1)确认Inbox清零
  2)过NA—仍有效?
  3)过Projects—每个有下一步?
  4)过WF—>7天建议催
  5)过Someday—是否激活
  6)定下周
  7)OKR对齐
  通知用户开始回顾对话。
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: run_latest
```

**每日快照**（23:55 自动 git commit）：
```yaml
name: "GTD Vault 快照"
schedule: "55 23 * * *"  # Asia/Shanghai
prompt: >
  在vault目录执行: cd $VAULT_PATH && git add -A && git diff --cached --quiet || git commit -m 'daily snapshot'。
  静默执行，无需通知用户。
contextDirs: ["$VAULT_PATH"]
missedRunPolicy: skip
```

注意：如果 vault 还没有 git init，先执行：
```bash
cd "$VAULT_PATH" && git init && git add -A && git commit -m "initial vault setup"
```

### 8. 运行 doctor 验证

```bash
python3 $REPO_PATH/setup/doctor.py --vault "$VAULT_PATH"
```

确认零 error 零 warning。

### 9. 打开 Quick Start + 发起 Brain Dump

**此步骤不可跳过**——即使前面所有步骤都已完成，必须执行以下两个动作：

**A. 确认引导任务存在：**

init.py 会把 `00 - Inbox/Getting Started with GTD.md` 复制到用户 vault。验证它存在：
```bash
ls "$VAULT_PATH/00 - Inbox/Getting Started with GTD.md"
```
这条引导任务是冷启动的核心——它让用户的第一次播报不是空的，且引导用户亲手走通 GTD 全流程（Inbox → Project → NA → due → MIT）。

**B. 在浏览器打开 QUICKSTART.html（必做）：**

立即使用浏览器工具导航到：
```
file://$VAULT_PATH/QUICKSTART.html
```

如果浏览器工具不可用，退而求其次用 `open` 命令：
```bash
open "$VAULT_PATH/QUICKSTART.html"
```

告诉用户："我已在浏览器打开了 Quick Start 引导页，你可以收藏备用。"

**C. 在对话里立即发起 brain dump（必做）：**

> 搞定了。我刚在浏览器打开了 Quick Start 页面，随时可以回看。
>
> 另外我在你的 Inbox 里放了一条「开始使用 GTD」引导任务——明天你可以跟着它走一遍完整流程，5 步跑通。
>
> 现在咱们把系统填上——你脑子里飘着哪些事？待办、承诺、想法都行，一条一条告诉我。

之后进入对话循环：用户每说一条，Agent 立即写入 `00 - Inbox/`，回复"收到，还有吗？"。直到用户说"没了"或"先这样"，Agent 回应：

"好，收了 N 条（加上引导任务共 N+1 条）。明早播报会提醒你处理。或者你现在就可以说'帮我过一下 Inbox'开始分拣。"

**关键**：引导任务 + brain dump 双保险，确保第一次早间播报至少有内容可报。

## Pitfalls

- 不要把 vault 建在仓库目录内（llm-gtd/ 是模板仓库，vault 是用户数据，要分开）
- `contextDirs` 指向 vault（AGENTS.md 所在处），不是 repo
- 如果用户已有 Obsidian vault 想复用，init.py 不会覆盖已有文件，可以安全执行
- 如果定时任务注册失败（比如权限问题），告诉用户手动在定时任务面板创建
- 钉钉/飞书文档创建失败时（如 MCP 未连接），告诉用户手动创建文档后把 URL 发过来，Agent 从 URL 提取文档 ID 填入
- 企微/微信用户如果后续想加文档同步，需要先绑定一个有文档能力的平台（钉钉或飞书）

## Verification

- `doctor.py` 报告 0 error / 0 warning
- 在 vault 里 `ls "00 - Inbox/"` 能看到目录
- AGENTS.md 存在且无 `{{` 残留
- 定时任务列表能看到 4 个新任务
- macOS: `launchctl list | grep com.gtd.quickcapture` 有输出（QuickCapture 运行中）
