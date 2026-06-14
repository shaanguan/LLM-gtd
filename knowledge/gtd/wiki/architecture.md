---
title: LLM-GTD 系统架构
created: 2026-06-14
updated: 2026-06-14
type: concept
tags: [architecture, design, agent, skill, maintenance]
---

# LLM-GTD 系统架构

## 三层模型

```
Agent Runtime 层
  Skill（路由） + cron jobs + AGENTS.md（规则） + knowledge/wiki
        ↕ 约定耦合，非强绑定
Computer Tools 层
  QuickCapture / Dashboard export / Git snapshot / Dashboard.app
        ↕
Vault 层（用户资产）
  00-Inbox ~ 07-Achievements / Dashboard.html / Templates / AGENTS.md
```

## 三层各自的生命周期

| 操作 | Vault（用户资产） | Computer Tools | Agent Runtime |
|------|:--:|:--:|:--:|
| 安装 | 创建模板 | 创建 launchd | 装 Skill + 注册 cron |
| 升级 | 更新模板，保留数据 | 刷新脚本/app | 刷新 Skill + 重注册 cron |
| 卸载 | **不动** | 全删 | Skill + cron **都该删** |

三层通过约定而非强绑定连接。脚本只能操作所在层的资源，无法跨层。

## 核心问题：缺乏协调者

三层各自独立维护，但安装/升级/卸载需要协调。当前没有统一的副作用追踪机制。

### 已知故障模式

| 故障 | 根因 | 发生条件 |
|------|------|----------|
| QuickCapture 升级后失效 | Agent Runtime 升级→init.py 冲掉 Computer 层 launch agent | 升级后未补装 |
| Cron 卸载残留 | uninstall.py 只到 Computer 层，Hermes cron 在 Runtime 层 | 任何卸载 |
| Skill/Vault 版本不对齐 | 两层独立升级，无自动检测 | Skill 升级后忘跑 upgrade.py |

## 优化方案：Manifest 副作用注册表

在 Vault 层的 `.llm-gtd/manifest.json` 中记录所有跨层副作用：

```json
{
  "artifacts": [
    {"layer": "computer",  "type": "launchd", "id": "com.llm-gtd.export-dashboard"},
    {"layer": "computer",  "type": "launchd", "id": "com.gtd.quickcapture"},
    {"layer": "computer",  "type": "app",     "path": "~/Applications/GTD Dashboard.app"},
    {"layer": "runtime",   "type": "cron",    "id": "<platform-cron-id>", "name": "GTD Morning Brief"},
    {"layer": "runtime",   "type": "skill",   "name": "llm-gtd"}
  ]
}
```

### 三条铁律

1. **安装时写入** — 每往系统放一个东西，同步写 manifest
2. **卸载时按图索骥** — Agent 读 manifest → 按 layer 分组 → 逐层清理
3. **Vault 笔记永不入 manifest** — 用户数据不在注册表中，保证不被误删

### 版本对齐机制

manifest 同时记录 vault 版本和 skill 版本，Agent 每次加载时对比 → 不一致则自动提醒 upgrade。

## 架构设计原则（Anthropic 简化风格）

- 三层各自自治，跨层通过 manifest 通信
- 副作用可追溯，卸载不留痕
- Vault 是唯一真理源，manifest 是操作记录
- Agent 是协调者，不依赖脚本跨层能力

## 相关页面

- [[gtd-five-steps]]
- [[capture]]
- [[weekly-review]]
