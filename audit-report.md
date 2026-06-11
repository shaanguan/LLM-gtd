# LLM-GTD 项目审计报告

> 审计时间：2026-06-11
> 审计范围：`/Users/zhoubo/Open GTD/llm-gtd/` 全仓库
> 审计方法：逐文件阅读源码 + 架构分析 + 交叉一致性检查

---

## 项目概览

一套开箱即用的 AI 驱动 GTD 系统，以 Obsidian Vault（Markdown 文件）为唯一数据源，通过 QoderWork 运行 AI Agent 实现全自动化的任务捕获、处理、回顾和渲染。

### 架构

```
渲染层  Dashboard.html │ 钉钉每日安排 │ 钉钉排期表
          ↑ export_dashboard.py / DingTalk MCP
Agent 层  QoderWork + AGENTS.md（17 节操作规范）+ 知识库
          ↑ 读/写/移动/归档
存储层  Obsidian Vault（00-Inbox ~ 07-Achievements + Scripts + Templates）
```

### 核心设计理念

- **Vault 是唯一数据源**，Agent 是唯一操作者，用户只看渲染层输出
- **AGENTS.md 即大脑**——注入到每次 Agent 会话，修改即时生效
- **条件渲染**的功能开关（`<!-- IF feature.X -->`）让模板按需裁剪
- **知识库与操作分离**——GTD 方法论 wiki 共享，vault 是个人的

### 架构亮点

- 三层分离设计清晰，关注点分离做得好
- §15/§16 把真实踩过的坑（Wiki 被覆盖、日期断言错误、图片尺寸丢失）记录为防御规则，非常务实
- 渲染层按受众分粒度（Dashboard 全量、排期表仅交付件、日报仅 MIT），同源不同视图

---

## 🔴 实际 Bug（3 条）

### Bug 1. cron 默认值不一致

`_config.py` 和 `config.schema.yaml` 的 weekly schedule 默认值为 `"Fri 18:30"`，但 `SKILL.md` 和 `AGENTS.md` 写的默认值是 `"Sun 21:00"`。两套默认值冲突。

**结论**：config 里的默认值应改为 `"Sun 21:00"`（通用用户标准值），`Fri 18:30` 是个人偏好，通过 `config.yaml` 覆盖。

**涉及文件**：
- `vault-template/Scripts/_config.py:45`
- `setup/config.schema.yaml:44`

### Bug 2. export_dashboard.py yaml 无 fallback

`doctor.py` 里对 `import yaml` 做了 try/except 处理，但 `export_dashboard.py` 直接 `import yaml`，PyYAML 未安装时会 ImportError 崩溃。

**涉及文件**：
- `vault-template/export_dashboard.py:21`

### Bug 3. cron_heartbeat.py fromisoformat Python <3.11 兼容

`datetime.fromisoformat()` 在 Python 3.11 以下不支持带时区偏移的 ISO string（如 `+08:00`）。同事机器不一定是 3.11+，heartbeat.json 里存的就是带时区的 ISO string。

**涉及文件**：
- `vault-template/Scripts/cron_heartbeat.py:57`

---

## 📋 发布前 TODO（3 条）

不急，发布前补上即可。

| # | 问题 | 说明 |
|---|------|------|
| 1 | README git clone 地址是占位符 | `<your-org>/llm-gtd`，还没推 GitHub |
| 2 | init.py --non-interactive 功能开关不可配置 | 硬编码默认值，发布前加 `--features` 参数 |
| 3 | 无 requirements.txt | 发布前补，至少声明 `pyyaml>=6.0` |

---

## 📐 代码质量小项

| 位置 | 问题 | 建议 |
|------|------|------|
| `init.py:204` | `cron.daily_doc_time` 的 `.replace(':30', ':00').replace(':00', ':00')` 第二个 replace 是空操作 | 删掉或修正逻辑 |
| `verify_sync.py:27` | 报告写到 `/tmp/gtd-sync-report.md` 硬编码路径 | 改为 `$GTD_VAULT/.llm-gtd/state/` |
| `export_dashboard.py:52` | 数据注入正则 `const {name}=.*?;(?=\s*\n)` 依赖单行格式 | 用明确标记注释作边界更稳健，当前够用 |
| `inbox_sla.py:37` | 用 `st_mtime` 判断文件年龄，git clone / Dropbox 同步会重置 mtime | 改用 frontmatter `date` 字段，mtime 作 fallback |

---

## 总结

| 维度 | 评价 |
|------|------|
| **架构设计** | ⭐⭐⭐⭐⭐ 三层分离 + AGENTS.md 即时生效 + 渲染层受众分粒度，设计成熟 |
| **实用性** | ⭐⭐⭐⭐⭐ 真实使用迭代出的产品，Lessons Learned 记录了 4 个真实事故 |
| **代码质量** | ⭐⭐⭐⭐ 代码简洁可读，有少量一致性问题 |
| **工程基础** | ⭐⭐⭐ 缺少测试、依赖管理、版本号，发布前需补齐 |
| **文档** | ⭐⭐⭐⭐ README / 架构文档 / 用户指南齐全，部分脚本缺文档 |

**核心结论**：设计思路非常成熟，从 AGENTS.md 的 17 节规范和事故复盘可以看出是真实落地迭代出来的。主要短板在工程基础设施（测试、依赖管理、版本号）和细节一致性上。核心架构没有硬伤。

---

## 附录：完整文件清单

### 核心脚本（8 个）

| 文件 | 职责 | 状态 |
|------|------|------|
| `setup/init.py` | 交互式初始化（3 个问题 + 模板渲染） | ⚠️ non-interactive 模式待增强 |
| `setup/doctor.py` | 环境自检（7 项检查） | ✅ |
| `setup/config.schema.yaml` | 配置项参考 | ✅ |
| `vault-template/Scripts/_config.py` | 共享配置加载器 | ⚠️ weekly 默认值需改 |
| `vault-template/Scripts/cron_heartbeat.py` | cron 心跳监控 | ⚠️ fromisoformat 兼容性 |
| `vault-template/Scripts/verify_sync.py` | vault 前置检查 + 漂移检测 | ✅ |
| `vault-template/Scripts/inbox_sla.py` | Inbox SLA 告警 | ✅ |
| `vault-template/Scripts/preflight.py` | cron 预检 + PTO 开关 | ✅ |
| `vault-template/export_dashboard.py` | vault → Dashboard 数据同步 | ⚠️ yaml 无 fallback |

### 文档（6 个）

| 文件 | 内容 |
|------|------|
| `README.md` | 项目介绍 + 快速上手 |
| `docs/architecture.md` | 三层架构详解 |
| `docs/user-guide.md` | 完整用户指南 |
| `docs/faq.md` | 11 个常见问题 |
| `docs/setup-guide-for-agent.md` | Agent 操作指南（中文） |
| `vault-template/AGENTS.md` | Agent 17 节操作规范（模板源码） |

### 知识库（~50 页）

| 路径 | 说明 |
|------|------|
| `knowledge/gtd/SCHEMA.md` | wiki 规范 |
| `knowledge/gtd/wiki/` | ~50 页 GTD 方法论 wiki |

### Vault 模板

| 路径 | 说明 |
|------|------|
| `vault-template/00 - Inbox/` | 收集箱（含 README） |
| `vault-template/01 - Projects/` ~ `07 - Achievements/` | GTD 9 大目录 |
| `vault-template/Templates/` | Action / Inbox / Project 模板 |
| `vault-template/Dashboard.html` | 本地单页仪表盘 |

### 其他

| 路径 | 说明 |
|------|------|
| `scripts/sync-knowledge.sh` | 知识库同步脚本（rsync） |
| `skill/SKILL.md` | QoderWork Skill 定义（一键 setup） |
| `examples/demo-vault/` | 演示 vault（虚构设计师 Li Wei） |
