# Harness Layer Map

本文档记录当前 Fons4AI 技能资产在 Harness Engineering 六层体系中的位置，并基于现有 `skills/*/SKILL.md` 做结构盘点。

本次盘点只读取现有技能，不修改技能正文。

## 1. 分层口径

Fons4AI Harness Engineering 使用 6 层结构：

| 层级 | 关注点 | 典型职责 |
| --- | --- | --- |
| Intent Harness | 明确意图、范围和验收 | 需求澄清、变更分析、AC 定义 |
| Context Harness | 控制上下文加载和知识事实 | 项目知识基线、领域/能力域建模、知识汇总 |
| Skill Harness | 约束 Agent 按角色执行 | 技能契约、触发门禁、职责边界、handoff |
| Rule Harness | 固化团队工程规则 | 项目 Agent 规则、代码规范、SDD 团队协作规范 |
| Feedback Harness | 证明完成和失败归因 | 实施报告、验证结果、BUG 修复报告、环境准备度 |
| Learning Harness | 跨项目抽象可复用经验 | 失败案例、`spec/reports/harness-feedback/` 上游反馈单、回放样例、校验器改进 |

一个技能可以横跨多层，但必须有一个主层级，避免职责扩散。

## 2. 当前技能分层映射

| 技能 | 主层级 | 辅助层级 | 当前职责摘要 | 阶段 2 处理建议 |
| --- | --- | --- | --- | --- |
| `fons4ai-sdd-requirements` | Intent Harness | Context Harness, Skill Harness | 澄清需求并生成需求说明书 | 保留现有职责；后续评估是否补充轻量 Evidence 章节 |
| `fons4ai-sdd-design` | Intent Harness | Skill Harness, Feedback Harness | 在需求后生成技术设计，记录风险、验证策略和知识影响 | 结构较完整；后续补显式 `职责边界` 章节 |
| `fons4ai-sdd-tasks` | Intent Harness | Skill Harness, Feedback Harness | 把需求和设计拆成任务规划，并停止等待实现确认 | 保留任务规划职责；后续评估是否补充轻量 Evidence 章节 |
| `fons4ai-sdd-change` | Intent Harness | Skill Harness, Feedback Harness | 对既有 SDD 功能做变更分析、CR 和增量任务 | 结构完整，可作为变更类技能样板 |
| `fons4ai-sdd-implement` | Feedback Harness | Skill Harness, Context Harness | 执行已授权 SDD 任务，要求验证证据和实施报告 | 结构完整，可作为实现类技能样板 |
| `fons4ai-bugfix-workflow` | Feedback Harness | Intent Harness, Skill Harness | 复现、诊断、修复、验证并记录 BUG | Contract 完整；后续补显式角色和职责边界章节 |
| `fons4ai-agent-env-readiness` | Feedback Harness | Context Harness | 评估 Agent 环境准备度和验证可靠性 | 保留按需增强定位；后续评估是否补 Evidence 章节 |
| `fons4ai-harness-feedback` | Learning Harness | Feedback Harness | 将业务试点项目中的 Agent 使用问题整理为脱敏上游反馈单 | 新增技能；默认输出到 `spec/reports/harness-feedback/` |
| `fons4ai-knowledge-bootstrap` | Context Harness | Skill Harness | 从代码、文档、接口、测试和配置建立项目知识基线 | Contract 已补齐；后续按 MVP 试点反馈优化 |
| `fons4ai-domain-knowledge-modeling` | Context Harness | Skill Harness | 对领域或技术能力域进行深度知识建模 | Contract 已补齐；后续按 MVP 试点反馈优化 |
| `fons4ai-knowledge-summary` | Context Harness | Feedback Harness, Skill Harness | 汇总已验证事实到知识库、领域文档、知识卡片和 SQL 快照 | 结构完整，可作为知识汇总类技能样板 |
| `fons4ai-generate-project-rules` | Rule Harness | Context Harness, Skill Harness | 把已验证事实和用户决策转为项目 Agent 规则 | Contract 已补齐；后续按 MVP 试点反馈优化 |

## 3. 结构盘点结果

### 3.1 校验脚本结果

现有脚本：

```text
scripts/validate_skill_contracts.py --skills-root skills
scripts/validate_feedback_harness.py
```

使用内置 Python 执行结果：

```text
OK: core skill contracts are valid
OK: Feedback Harness entrypoint assets are valid
```

其中 `validate_skill_contracts.py` 检查核心技能 Contract 和 Evidence 基线；`validate_feedback_harness.py` 检查 Feedback Harness 总入口，包括实施报告、BUG 修复报告、环境准备度、上游反馈单、反馈路径约定和核心校验器。

含义：

- 脚本当前覆盖 7 个核心技能。
- 已覆盖核心技能满足当前脚本要求的 Contract 和 Evidence 基线。
- 全部 12 个 Fons4AI 自有技能均已具备统一 Contract 五要素；脚本覆盖面仍需从核心技能扩展到全量技能。

### 3.2 全量技能 Contract 盘点

将全部 12 个 Fons4AI 自有技能按统一 Contract 口径盘点时，P1 技能状态如下：

| 技能 | 主要缺口 | 建议优先级 |
| --- | --- | --- |
| `fons4ai-domain-knowledge-modeling` | 已补齐 `## Contract`、Inputs、Preconditions、Outputs、Exit Criteria、Handoff | 完成 |
| `fons4ai-knowledge-bootstrap` | 已补齐 `## Contract`、Inputs、Preconditions、Outputs、Exit Criteria、Handoff | 完成 |
| `fons4ai-generate-project-rules` | 已补齐 `## Contract`、Inputs、Preconditions、Outputs、Exit Criteria、Handoff | 完成 |

### 3.3 全量技能章节盘点

按阶段 2 目标章节口径检查时，当前状态如下：

| 技能 | 结构状态 | 备注 |
| --- | --- | --- |
| `fons4ai-sdd-implement` | 完整 | 可作为实现类技能样板 |
| `fons4ai-sdd-change` | 完整 | 可作为变更类技能样板 |
| `fons4ai-knowledge-summary` | 完整 | 可作为知识汇总类技能样板 |
| `fons4ai-sdd-design` | 基本完整 | 缺显式 `## 职责边界` 标题 |
| `fons4ai-bugfix-workflow` | Contract 完整 | 缺显式 `## 角色说明`、`## 职责边界` 标题 |
| `fons4ai-sdd-requirements` | Contract 完整 | 缺 Evidence 章节；可按需求类技能决定是否需要轻量 Evidence |
| `fons4ai-sdd-tasks` | Contract 完整 | 缺 Evidence 章节；可按规划类技能决定是否需要轻量 Evidence |
| `fons4ai-agent-env-readiness` | Contract 完整 | 缺 Evidence 章节；作为验证可靠性技能，建议补轻量 Evidence |
| `fons4ai-knowledge-bootstrap` | Contract 已补齐 | 后续按试点反馈调整证据口径和输出边界 |
| `fons4ai-domain-knowledge-modeling` | Contract 已补齐 | 后续按试点反馈调整建模证据、确认门禁和适配输出粒度 |
| `fons4ai-generate-project-rules` | Contract 已补齐 | 后续按试点反馈调整规则证据矩阵和 MCP 边界 |

## 4. 阶段 2 优先级

### P0：已确认的结构决策

- 使用 `docs/skill-contract-standard.md` 作为后续技能整理标准。
- Evidence 标准不是一刀切；不同技能按风险和职责采用不同证据强度。
- `fons4ai-project-knowledge-base-init` 已移除；项目知识基线主入口统一收敛到 `fons4ai-knowledge-bootstrap`。

### P1：统一 Contract 补齐状态

P1 技能的统一 Contract 已补齐：

1. `fons4ai-knowledge-bootstrap`
2. `fons4ai-generate-project-rules`
3. `fons4ai-domain-knowledge-modeling`

后续处理：

- 不再继续孤立补全所有细节。
- 使用业务项目 MVP 试点检验这三个入口技能的触发、上下文加载、确认门禁和输出边界。
- 试点反馈通过 `fons4ai-harness-feedback` 汇总后，再回流优化技能正文、模板或校验器。

### P2：补齐显式章节

对以下技能做轻量结构整理：

- `fons4ai-sdd-design`：补显式职责边界。
- `fons4ai-bugfix-workflow`：补角色说明和职责边界。
- `fons4ai-agent-env-readiness`：评估并补轻量 Evidence。
- `fons4ai-sdd-requirements`、`fons4ai-sdd-tasks`：评估需求/规划类 Evidence 是否采用轻量版本。

### P3：保留观察项

旧入口 `fons4ai-project-knowledge-base-init` 已移除，阶段 2 不再为它补 Contract。

后续只需要观察是否仍有文档、脚本、插件配置或外部项目引用该旧技能名；如发现引用，应迁移到 `fons4ai-knowledge-bootstrap`。

## 5. 后续执行边界

后续如果进入技能正文整理，必须遵守：

- 每次只处理一类技能或一个技能。
- 保留原有触发门禁和职责边界，不借结构整理扩展技能权限。
- 不把阶段 3 的自动反馈闭环混入阶段 2。
- 每次改动后运行 `scripts/validate_skill_contracts.py`；涉及 Feedback Harness、反馈路径、报告模板或验证脚本时，同时运行 `scripts/validate_feedback_harness.py`。
