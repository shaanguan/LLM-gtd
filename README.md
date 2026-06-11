# LLM-GTD

> 让 AI 帮你管理待办事项，而不是你管理 AI。

一套 AI 驱动的 GTD 系统。Obsidian 存数据，AI Agent 帮你捕获、分拣、提醒、归档。你只需要说话。

## 30 秒看懂

```
你说一句话 → Agent 写入 vault → 定时播报提醒你 → 做完了归档
```

每天早上推今日重点，晚上帮你回顾归档，每周清理一遍系统。中间随时可以对它说"帮我记一下 xxx"。

## 快速上手

**1. 安装 Setup Skill**

把 setup 流程装进你的 Agent，让它知道怎么帮你搭系统：

- **Claude Desktop（推荐）** — 新建 Project，把 [SKILL.md](skills/llm-gtd-setup/SKILL.md) 内容粘到 Project Instructions
- **QoderWork** — 技能市场搜索 `llm-gtd-setup`，点击安装
- **其他 Agent** — 把 SKILL.md 内容粘到 system prompt 或对应的指令配置里

**2. 对 Agent 说：**

> "帮我设置 LLM-GTD"

它会问你几个问题（vault 放哪、用什么 IM、几点播报），然后全自动搭好。

## 需要什么

- 一个 AI Agent 环境（Claude Desktop / QoderWork / 其他支持 system prompt 的工具）
- Obsidian
- Python 3.9+

## 平台兼容性

| 平台 | 定时任务 | IM 推送 | 文档同步 |
|------|---------|---------|---------|
| Claude Desktop | 需外部 cron | 需 MCP 插件 | 需 MCP 插件 |
| QoderWork | ✅ 内置 | ✅ 钉钉/飞书/企微 | ✅ 钉钉/飞书文档 |
| 其他 | 手动触发 | — | — |

核心功能（vault 管理 + Dashboard + 对话）在所有平台都能跑。

## 更多

- [用户指南](docs/user-guide.md)
- [系统架构](docs/architecture.md)
- [FAQ](docs/faq.md)

## License

MIT
