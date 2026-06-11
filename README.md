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

下载 [SKILL.md](skills/llm-gtd-setup/SKILL.md)，装到你的 Agent 里（具体方式见文件开头说明）。

**2. 对 Agent 说：**

> "帮我设置 LLM-GTD"

它会问你几个问题（vault 放哪、用什么 IM、几点播报），然后全自动搭好。

## 需要什么

- 一个 AI Agent 环境（Claude Desktop / QoderWork / 其他支持 system prompt 的工具）
- Obsidian
- Python 3.9+

## 更多

- [用户指南](docs/user-guide.md)
- [系统架构](docs/architecture.md)
- [FAQ](docs/faq.md)

## License

MIT
