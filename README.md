# LLM-GTD

> Your AI GTD secretary, lives inside QoderWork.

让 AI 帮你管理待办事项，而不是你管理 AI。

---

## 这是什么？

LLM-GTD 是一套开箱即用的 **AI 驱动 GTD（Getting Things Done）系统**。你只需要三样东西：

1. **QoderWork** — AI Agent 运行环境（定时任务、对话、钉钉集成）
2. **Obsidian** — 你的笔记本（Markdown 文件就是你的数据）
3. **一个浏览器** — 打开 Dashboard.html 看全局状态

装好之后，你会拥有一个 7×24 小时在线的 GTD 秘书：

- 🌅 **每天早上** — 自动推送今日重点（最多 3 件 MIT），提醒临近截止和等待超时
- 🌙 **每天晚上** — 问你哪些做完了，帮你归档、更新进度、刷新 Dashboard
- 📅 **每周一次** — 完整回顾：清 Inbox、检查项目、激活 Someday、对齐 OKR
- 💬 **随时对话** — 说一句"帮我记一下：明天给设计稿加动效"，它就落进系统
- 📊 **Dashboard** — 本地 HTML 仪表盘，一眼看到所有任务状态，无需服务器

## 它能帮你做什么？

| 你说 | 它做 |
|------|------|
| "帮我记一下周五要交评审" | 创建一条 NA，标好 `due: 周五`，放进 `02 - Next Actions/` |
| "那个 logo 设计完成了" | 归档到 `06 - Archive/`，写入成就记录，刷新 Dashboard |
| "今天忙什么" | 从 vault 实时扫描，列出今日 MIT + 逾期 + 等待中 |
| "帮我看看 Inbox" | 逐条过 GTD 决策树：该做的建 NA，该等的建 WF，该扔的问你 |
| "这周进展怎么样" | 汇总本周归档项，对比 OKR 进度 |

## 谁适合用？

- 用 Obsidian 记笔记，想让任务管理也住在同一个地方的人
- 想要 GTD 的系统性，但懒得自己维护清单的人
- 团队协作用钉钉，想让同事看到你的排期但不暴露全部细节的人
- 对 AI Agent 感兴趣，想看一个真实落地案例的人

## 不适合谁？

- 不用 QoderWork 的人（Agent 运行时强依赖它）
- 偏好 GUI 任务管理器（Todoist / Things / TickTick）的人
- 不接受文件都是 Markdown 的人

---

## 快速上手（5 分钟）

### 推荐方式：在 QoderWork 中对话完成

打开 QoderWork，直接说：

> "帮我设置 LLM-GTD"

Agent 会自动完成以下所有步骤 — 你只需要回答几个偏好问题（vault 放哪、开哪些功能、定时任务时间），然后确认即可。

唯一需要你手动做的一步：打开 Obsidian → "Open folder as vault" → 选 Agent 生成的路径。（之后所有操作都可以在对话中完成）

---

### 手动方式：命令行

如果你更喜欢自己掌控，6 步搞定：

```bash
# 1. 克隆仓库
git clone https://github.com/<your-org>/llm-gtd.git
cd llm-gtd

# 2. 运行初始化（交互式，问 3 组问题）
python3 setup/init.py

# 3. 用 Obsidian 打开生成的目录
#    Open Obsidian → "Open folder as vault" → 选刚才指定的路径

# 4. 在 QoderWork 中选择这个文件夹作为工作目录

# 5. 注册定时任务（或让 Agent 帮你注册）

# 6. 验证
python3 setup/doctor.py --vault ~/Documents/GTD
```

---

## 系统是怎么工作的？

```
┌─────────────────────────────────────────────────────────┐
│                  你看到的（渲染层）                        │
│  Dashboard.html  │  钉钉每日工作安排  │  钉钉需求排期表   │
└────────┬─────────────────┬────────────────────┬─────────┘
         │                 │                    │
         │   export_dashboard.py    DingTalk MCP│
         │                 │                    │
┌────────▼─────────────────▼────────────────────▼─────────┐
│              AI Agent 层（QoderWork）                     │
│  AGENTS.md 17 节操作规范 + 知识库 + 定时任务              │
└────────┬────────────────────────────────────────────────┘
         │  读 / 写 / 移动 / 归档
┌────────▼────────────────────────────────────────────────┐
│              数据层（Obsidian Vault）                     │
│  00-Inbox │ 01-Projects │ 02-NA │ 03-WF │ 04-Someday   │
│  05-Reference │ 06-Archive │ 07-Achievements            │
└─────────────────────────────────────────────────────────┘
```

核心思路：**vault 是唯一数据源，Agent 是唯一操作者，你只看渲染层的输出。**

详细架构说明见 [docs/architecture.md](docs/architecture.md)。

---

## 功能开关

所有高级功能都是可选的，初始化时选择开启或关闭：

| 功能 | 默认 | 说明 |
|------|------|------|
| OKR 追踪 | 开 | 每条任务可关联 OKR，周回顾自动对比进度 |
| 钉钉同步 | 开 | 自动更新钉钉文档（排期表 + 每日安排），同事能看到 |
| 副项目隔离 | 关 | 个人项目单独追踪，不混入工作输出 |
| 知识库引用 | 开 | Agent 处理 Inbox 时参考 GTD 方法论 wiki |

---

## 项目结构

```
llm-gtd/
├── setup/                  — 安装工具
│   ├── init.py               交互式初始化（3 个问题搞定）
│   ├── doctor.py             环境自检
│   └── config.schema.yaml    配置项参考
├── vault-template/         — vault 模板（init.py 会复制这个）
│   ├── AGENTS.md             Agent 操作规范（17 节，条件渲染）
│   ├── Scripts/              运维脚本（心跳、SLA、自检）
│   ├── Dashboard.html        本地仪表盘
│   └── ...                   GTD 9 大目录 + 模板
├── knowledge/gtd/          — GTD 方法论 wiki（~50 页，所有用户共享）
├── scripts/                — 开发者工具
├── docs/                   — 详细文档（架构、指南、FAQ）
└── examples/demo-vault/    — 虚构用户演示（设计师 Li Wei）
```

---

## 常见问题

**Q: 我不了解 GTD 方法论，能用吗？**
可以。Agent 内置了完整的 GTD 决策逻辑 — 你只管往 Inbox 扔东西，它帮你分类、排期、提醒。用着用着就懂了。

**Q: 数据安全吗？**
所有数据存在你本地的 Obsidian vault 里。不上传云端。钉钉同步只推摘要信息（任务名+状态），不推全文。

**Q: 和 Todoist / Things 有什么区别？**
它们是你操作任务；LLM-GTD 是 Agent 帮你操作任务。你只需要说话和确认。

**Q: 我已经有 Obsidian vault 了，会冲突吗？**
不会。`init.py` 只创建 GTD 目录（`00-Inbox` 到 `07-Achievements`）和 AGENTS.md，不碰你已有的文件。

更多问题见 [docs/faq.md](docs/faq.md)。

---

## 进一步了解

- [用户指南](docs/user-guide.md) — 完整使用手册
- [系统架构](docs/architecture.md) — 三层设计详解
- [FAQ](docs/faq.md) — 15 个常见问题
- [Demo Vault](examples/demo-vault/) — 虚构设计师 Li Wei 的演示数据，可以直接跑

---

## License

MIT — see [LICENSE](LICENSE).
