# Skill Contract Standard

本文档定义 Fons4AI 技能的统一契约结构，用于阶段 2 结构升级。

目标不是把所有技能写成同样厚重的流程，而是让 Agent 能快速判断：

- 什么时候可以使用该技能。
- 需要读取哪些输入。
- 可以产出什么。
- 不能做什么。
- 成功、阻塞和交接标准是什么。
- 需要什么级别的证据才能宣称完成。

## 1. 标准章节

每个正式技能建议使用以下章节顺序。

```text
---
name: <skill-name>
description: "<一句话说明触发条件和职责>"
---

# <Skill Name>

## Contract

### Inputs
### Preconditions
### Outputs
### Exit Criteria
### Handoff

## Evidence Required

### Evidence Levels
### Hard Evidence Gates
### Evidence Output

## 触发门禁
## 角色说明
## 职责边界
## 必要上下文
## 执行流程
## 质量要求
## 禁止事项
## 结束回复要求
```

并非所有技能都必须使用同等重量的 Evidence。Evidence 标准不是一刀切，必须按技能风险和职责边界分级适用；但 Contract、触发门禁、角色说明和职责边界应成为正式技能的稳定入口。

## 2. Contract 标准

### 2.1 Inputs

说明技能启动需要的输入。

应区分：

- Required：没有就不能执行。
- Optional：有助于判断，但不是必需。
- Forbidden assumptions：不得推断的内容。

示例口径：

```text
- Required: 用户最新消息中的明确实现授权，以及任务规划中的未完成任务。
- Optional: 需求说明书、技术设计说明书、测试、配置、SQL/schema 证据。
- Forbidden assumptions: 不得从历史对话、任务存在或模糊指令推断实现授权。
```

### 2.2 Preconditions

说明技能执行前必须满足的条件。

应覆盖：

- 触发门禁。
- 必要产物是否存在。
- 依赖任务或依赖事实是否具备。
- 是否需要用户确认。
- 是否存在必须先停止的歧义。

### 2.3 Outputs

说明技能允许和禁止产出的内容。

应至少包含：

- May create or update。
- Must not create or update。
- Output location。

该章节用于防止技能越权，例如规划类技能写业务代码、知识类技能生成实现任务、实现类技能重写需求。

### 2.4 Exit Criteria

说明技能结束条件。

应至少包含：

- Success：什么情况算成功。
- Blocked：什么情况必须停止。
- Failure report：失败时如何报告。

成功标准应尽量绑定可验证证据，不能只写“完成文档”或“实现代码”。

### 2.5 Handoff

说明技能完成后能交给谁，以及不能自动进入什么流程。

应包含：

- Next skill。
- Required handoff fields。
- Stop condition。

Handoff 只说明建议和交接信息，不等于自动触发下一个技能。

## 3. Evidence 标准

Evidence 用于支撑“为什么可以继续”和“为什么可以宣称完成”。

### 3.1 Evidence Levels

统一使用三档：

| 等级 | 含义 | 典型证据 |
| --- | --- | --- |
| L1 Context Evidence | 支撑上下文理解和影响分析 | 已读取的代码、文档、配置、规则 |
| L2 Decision Evidence | 支撑局部决策和范围确认 | 用户确认、正式 SDD 产物、接口定义、源码事实 |
| L3 Gate Evidence | 支撑完成、发布就绪或知识沉淀 | 测试结果、构建结果、校验脚本结果、只读验证、手工验证记录 |

### 3.2 Evidence 适用强度

Evidence 不应一刀切。

| 技能类型 | Evidence 强度 | 说明 |
| --- | --- | --- |
| 实现类 | 强制完整 Evidence | 任务完成必须有 L3 验证证据 |
| BUG 修复类 | 强制完整 Evidence | 必须记录复现、修复和验证结果 |
| 知识汇总类 | 强制完整 Evidence | 长期知识沉淀必须有 L3 或明确待确认状态 |
| 技术设计/变更类 | 强制或中等 Evidence | 高风险设计、DDL、安全和契约必须有证据 |
| 需求/任务规划类 | 轻量 Evidence | 重点记录用户确认、正式产物和阻塞歧义 |
| 编排/Runner 类 | 轻量到中等 Evidence | 重点记录阶段出口、handoff、校验结果和停止点 |
| 规则生成类 | 中等 Evidence | 规则必须来自用户确认或已验证项目事实 |
| 环境准备类 | 中等 Evidence | 区分已验证能力、未验证能力和建议项 |
| 知识建模/基线类 | 中等到强制 Evidence | 不得把单点实现或推断写成标准事实 |

### 3.3 Hard Evidence Gates

硬门禁应只放真正会影响交付可信度的规则。

推荐硬门禁：

- 实现任务完成状态必须有 L3 验证证据。
- 验证失败时不得勾选任务完成。
- DDL 或数据结构任务必须记录 DDL 状态、验证状态或阻塞原因。
- 长期知识沉淀不得只依赖推断。
- 规则文件不得把未确认项目事实写成团队规则。

不推荐硬门禁：

- 所有文档任务都必须跑业务测试。
- 所有低风险任务都必须完整 SDD。
- 所有技能都必须有相同长度的 Evidence 章节。

## 4. 触发门禁标准

触发门禁用于判断技能是否能被自动使用。

标准口径：

```text
使用本技能前，必须满足以下任一条件：

1. 用户明确指定该技能。
2. 用户明确要求执行该技能对应的具体工作类型或阶段。
3. 当前仓库作用域内存在 AGENTS.md，且包含 Fons4AI 路由标记，并且用户当前意图明确匹配该技能职责。
```

泛化的“使用 SDD 开发新功能”应优先路由到正常新需求编排技能；需求、设计、任务等阶段技能只能在用户明确指定阶段、补齐阶段产物，或由编排技能进入对应阶段时触发。

实现类技能还必须增加：

```text
最新用户消息必须明确确认进入实现。
```

不得把以下内容当作实现授权：

- “看一下”
- “继续看看”
- “下一步是什么”
- “使用 SDD”
- 历史对话中的旧确认
- 已存在任务规划

## 5. 职责边界标准

职责边界应明确技能负责什么、不负责什么。

建议写法：

```text
本技能负责：

- ...

本技能不得：

- ...
```

重点防止以下越权：

- 编排型技能替代阶段技能生成细节。
- 编排型技能绕过用户确认进入实现。
- 需求技能直接设计或实现。
- 设计技能直接写业务代码。
- 任务技能创建知识同步任务。
- 实现技能扩展 AC 或重写设计。
- 知识技能生成新的实现任务。
- 规则技能把项目事实堆成规则。

### 5.1 编排型 Skill 标准

编排型 Skill 可以调度多个阶段 Skill，但只负责：

- 判断请求类型和分流。
- 控制阶段顺序。
- 检查阶段出口和 handoff。
- 运行对应阶段的确定性校验脚本。
- 在需要用户授权的边界停止。

编排型 Skill 不得：

- 替代阶段 Skill 的产物细节。
- 跳过阶段 Skill 的阻塞门禁。
- 写业务代码。
- 自动进入实现类 Skill。
- 把历史确认或模糊表达当作实现授权。

## 6. 必要上下文标准

必要上下文应按“最小足够”原则写。

建议顺序：

1. 入口规则或 AGENTS。
2. 当前任务直接相关的 SDD 产物。
3. 任务 `Files:` 指定文件。
4. 直接相关测试、配置、接口和 SQL。
5. 相关项目规则和知识卡片。
6. 只有在冲突、歧义或高风险时才读取更深上下文。

不得为了安全感全量读取仓库、全量读取知识库或全量读取历史产物。

## 7. 输出和结束回复标准

结束回复应让用户能判断：

- 本技能做了什么。
- 产物在哪里。
- 验证结果是什么。
- 是否还有阻塞或风险。
- 下一步建议是什么。

实现类和修复类技能必须说明：

- 变更文件。
- 测试或验证命令。
- 验证结果。
- 未验证项。
- DDL 或外部依赖状态。

文档类和规则类技能必须说明：

- 新增或更新的文档。
- 依据来源。
- 待确认项。
- 不应自动进入实现的边界。

## 8. 阶段 2 迁移规则

结构升级时按以下顺序推进：

1. 先对齐文档标准，不改技能。
2. 选一个样板技能确认结构。
3. 再按技能类型小批量整理。
4. 每次整理后运行校验脚本。
5. 再决定是否扩展校验脚本覆盖更多技能。

优先顺序：

1. 已完整技能作为样板：`fons4ai-sdd-implement`、`fons4ai-sdd-change`、`fons4ai-knowledge-summary`。
2. 编排型样板：`fons4ai-sdd-feature-workflow`。
3. P1 Contract 已补齐的 MVP 入口技能：`fons4ai-knowledge-bootstrap`、`fons4ai-generate-project-rules`、`fons4ai-domain-knowledge-modeling`。
4. P2 显式章节缺口技能：`fons4ai-sdd-design`、`fons4ai-bugfix-workflow`；跨服务运行态与初始化数据证据应回收到 SDD 主链路。
5. 旧入口处理：`fons4ai-project-knowledge-base-init` 已移除，后续引用应迁移到 `fons4ai-knowledge-bootstrap`。

## 9. 校验脚本演进建议

当前 `scripts/validators/validate_skill_contracts.py` 已能验证 9 个核心技能。

后续建议：

- 增加技能类型配置，而不是把所有技能套同一套硬规则。
- 区分必需章节、推荐章节和条件章节。
- 支持输出 Markdown 盘点报告。
- 支持已移除或迁移技能名的引用检查。
- 支持 Evidence 强度分级。

脚本演进前，不应因为新标准存在就立即判定所有旧技能失败；应先通过文档盘点和用户确认确定迁移范围。

## 10. 平台中立与多 Agent 协作标准

### 10.1 三层分离

Fons4AI 技能在多 Agent 协作场景下按三层分离组织：

| 层 | 文件 | 职责 | 平台中立 |
| --- | --- | --- | --- |
| 契约层 | `SKILL.md` | 定义 Contract、Evidence、Handoff、角色边界 | 是 |
| Agent 清单层 | `agents/manifest.yaml` | 定义角色、上下文预算、权限、Evidence 级别、multi_agent_tier | 是 |
| 平台适配层 | `agents/<platform>.yaml` | 定义线程管理、并行能力、spawn/handoff 方式 | 否 |

### 10.2 manifest.yaml 标准章节

每个正式技能必须包含 `agents/manifest.yaml`，包含以下字段：

```text
schema_version: "1.0"
agent:
  role:                    # Agent 角色名
  category:                # 技能类别
  context_budget:          # 上下文预算（required / optional / forbidden_full_scan）
  permissions:             # 权限（read / write / execute）
  evidence_level:          # Evidence 级别（L1 / L2 / L3）
  spawn_by:                # 由哪个编排技能创建（null 表示可独立触发）
  handoff_targets:         # 可交接的下游技能列表
  stop_for_user_confirm:   # 是否需要用户确认才能继续
  multi_agent_tier:        # 多 Agent 能力等级（0 / 1 / 2）
```

### 10.3 平台适配标准

平台适配文件（如 `agents/openai.yaml`）必须包含 `adapter` 段：

```text
adapter:
  platform:                # 平台标识（codex / claude / qder / trace）
  capabilities:            # 能力声明
    multi_agent:           # 是否支持多 Agent
    parallel:              # 是否支持并行执行
    thread_handoff:        # 是否支持线程级 handoff
  spawn_method:            # 创建子 Agent 的方式
  handoff_method:          # 交接方式（handoff_thread / file_based）
  context_isolation:       # 是否支持上下文隔离
```

### 10.4 平台中立约束

- `SKILL.md` 不得包含平台专属执行逻辑（`adapter:`、`create_thread`、`handoff_thread`、`subagent` 等）。
- `manifest.yaml` 不得包含平台标识（`platform: codex`、`platform: claude` 等）或平台专属 API。
- 平台专属内容只能出现在 `agents/<platform>.yaml` 中。
- 结构化 handoff YAML（`templates/handoff-yaml-template.yaml`）是平台中立的文件格式，所有平台共用。

### 10.5 多 Agent 能力分级

| Tier | 能力 | 说明 |
| --- | --- | --- |
| 0 | 单 Agent + 技能切换 + 文件 handoff | 所有平台基线 |
| 1 | Orchestrator 创建子线程，串行调度 | 需要多 Agent 能力 |
| 2 | 并行多 Agent + 跨 Agent Evidence 信任 | 需要并行能力 |

平台不支持高 Tier 时自动降级到 Tier 0，但产物格式、handoff 协议和校验器对所有 Tier 一视同仁。

### 10.6 校验入口

```text
scripts/validators/validate_platform_neutrality.py --root .
scripts/validators/validate_handoff_schema.py --file <handoff.yaml>
```
