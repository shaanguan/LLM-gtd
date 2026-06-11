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

### 9. 冷启动：导入已有待办或引导上手

**此步骤不可跳过。**

Setup 完成后，问用户一个选择：

> "系统搭好了。你手上应该有一堆待办散落在各处——咱们先把它们收进来。选一种方式：
>
> **A. 直接告诉我** — 你一条条说，我帮你存。脑子里飘着什么就说什么。
>
> **B. 给我一个链接或地址** — 你现有的待办清单在哪？钉钉文档、飞书文档、本地文件路径都行，我去读然后导入。
>
> **C. 直接粘贴** — 把你现有的待办列表复制粘贴过来，我批量导入。
>
> **D. 7 天上手** — 手上没什么积压，想先体验一遍 GTD 流程。我帮你导入 7 天引导任务，每天一个小练习。
>
> 选哪个？"

**如果用户选 A（直接告诉我）：**

进入 brain dump 对话循环。用户每说一条，Agent 立即写入 `00 - Inbox/`，回复"收到，还有吗？"。直到用户说"没了"或"先这样"，Agent 回应：

"好，收了 N 条。明早播报会提醒你处理。或者你现在就可以说'帮我过一下 Inbox'开始分拣。"

**如果用户选 B（给链接或地址）：**

用户可能给出：
- 钉钉文档 URL → 通过钉钉 MCP 读取文档内容
- 飞书文档 URL → 通过飞书 MCP 读取文档内容
- 本地文件路径（.md / .txt / .csv / .opml 等）→ 直接读取
- 网页 URL → WebFetch 抓取

读取后，Agent 逐条解析为待办项，写入 `00 - Inbox/`。解析完毕后向用户确认：

"从 [来源] 读到了 N 条，已全部存入 Inbox。你看一眼有没有漏的或不该导的？"

**如果用户选 C（直接粘贴）：**

用户粘贴一段文本（可能是 bullet list、编号列表、纯文本逐行、或混合格式）。Agent 智能拆分为独立条目，逐条写入 `00 - Inbox/`。完成后确认：

"拆出了 N 条，已全部存入 Inbox。有需要拆分或合并的吗？"

**如果用户选 D（7 天上手）：**

将仓库 `vault-template/00 - Inbox/` 里的 Day 1-7 文件复制到用户 vault 的 `00 - Inbox/`，同时把 due 日期设置为从今天起的连续 7 天（Day 1 = 今天，Day 2 = 明天 ...）。

7 个任务分别是：
1. **Day 1：把脑子清空** — 练习 Capture，至少收集 10 条
2. **Day 2：清空收件箱** — 练习 Clarify + Organize，Inbox 归零
3. **Day 3：选出今日 MIT** — 练习 Engage，选 3 条最重要的执行
4. **Day 4：建一个真实项目** — 练习拆解，建项目 + 拆 Next Actions
5. **Day 5：追踪等别人的事** — 练习 Waiting For，记录 2 条
6. **Day 6：存"以后再说"的事** — 练习 Someday Maybe，存 3 条
7. **Day 7：做一次周回顾** — 练习 Weekly Review，走完 7 步

导入后告诉用户：

"好，7 天引导任务已就位。从今天开始每天的早间播报会提醒你当天的任务。Day 1 是把脑子清空——随时对我说'帮我收集'就能开始。"

**注意**：A/B/C 三条路可以混合使用。用户导完一批后 Agent 应该主动问"还有别的来源要导入吗？"，直到用户说够了为止。

### 10. 打开 Quick Start

**必须自动打开，怼脸呈现，不能指望用户自己找。**

优先级从高到低，用第一个能用的方式：

1. `open "$VAULT_PATH/QUICKSTART.html"` — macOS 默认浏览器直接弹出来
2. `xdg-open "$VAULT_PATH/QUICKSTART.html"` — Linux
3. 浏览器工具导航到 `file://$VAULT_PATH/QUICKSTART.html`

不需要告诉用户"我打开了"——他已经看到了。直接说下一步该干嘛就行。

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
