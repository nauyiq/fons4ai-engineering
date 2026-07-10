# 多 Agent 协作编排参考

本文档是 `fons4ai-sdd-feature-workflow` 和 `fons4ai-bugfix-workflow` 多 Agent 协作模式的详细参考。平台中立的协议定义见 `skill-contract-standard.md` 第 10 节。

## 1. 架构总览

```
                    Orchestrator Agent
                    (feature-workflow / bugfix-workflow)
                    只做路由/门禁/校验/handoff
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
    Requirements      Design           Tasks
    Agent             Agent            Agent
    (L2 Evidence)     (L2 Evidence)    (L1 Evidence)
          |                |                |
          +----------------+----------------+
                           |
                    +------+------+
                    |             |
                    v             v
              Implement      Implement
              Agent A        Agent B
              (L3 Evidence)  (L3 Evidence)
              (parallel)
```

## 2. 三层分离

| 层 | 文件 | 职责 | 平台中立 |
| --- | --- | --- | --- |
| 契约层 | `SKILL.md` | Contract / Evidence / Handoff / 角色边界 | 是 |
| Agent 清单层 | `agents/manifest.yaml` | 角色 / 上下文预算 / 权限 / Evidence 级别 / Tier | 是 |
| 平台适配层 | `agents/<platform>.yaml` | 线程管理 / 并行能力 / spawn / handoff 方式 | 否 |

## 3. 能力分级

### Tier 0：单 Agent 技能切换

所有平台的基线模式。编排者自行按序加载各阶段技能，通过文件系统传递产物。

- 适用平台：所有平台（包括不支持多 Agent 的工具）
- 上下文：单个 Agent 累积所有阶段上下文
- Handoff：编排者写入结构化 handoff YAML，下一个阶段技能读取
- 并行：不支持

### Tier 1：串行多 Agent 调度

编排者为每个阶段创建独立 Agent 线程，串行调度。

- 适用平台：支持多 Agent 的平台（Codex、Claude Code）
- 上下文：每个 Agent 只接收 handoff YAML 中的 artifacts 和 confirmed_facts
- Handoff：Agent 完成后写入 handoff YAML，编排者校验后创建下一 Agent
- 并行：不支持
- 用户确认门禁：不变

### Tier 2：并行多 Agent 调度

在 Tier 1 基础上，实现阶段支持并行。

- 适用平台：支持多 Agent 且支持并行的平台（Codex）
- 上下文：同 Tier 1，但多个实现 Agent 同时运行
- Handoff：编排者收集所有并行 Agent 的产出，合并 Evidence Bundle
- 并行：无依赖关系的任务组可并行
- L3 Evidence：编排者必须重新运行全量回归验证

## 4. Handoff YAML 协议

### 文件位置

```
spec/features/<yyyymmdd>/handoff/<from-skill>-to-<to-skill>.yaml
```

### Schema 概要

```yaml
schema_version: "1.0"
from:
  skill: fons4ai-sdd-requirements
  agent_thread_id: <platform-specific-id>
  stage: requirements
  status: success
to:
  skill: fons4ai-sdd-design
  allowed: true
artifacts:
  - path: spec/features/20260710/XX-需求说明书.md
    type: requirements-spec
    validator: validate_sdd_artifacts.py
evidence:
  level: L2
  items:
    - type: user-confirmation
      summary: "需求范围和 AC 已获用户确认"
      source: dialog
confirmed_facts:
  - "用户确认订单状态只有三种：待处理、已完成、已取消"
pending_questions: []
risk_and_blockers: []
validator_results:
  - command: "validate_sdd_artifacts.py --feature-dir spec/features/20260710"
    result: pass
    failures: []
    blocking: false
stop_condition:
  auto_proceed: false
  requires_user_confirm: true
  trigger_words: ["执行", "开始实现", "继续执行"]
```

### 校验

```bash
python scripts/validators/validate_handoff_schema.py --file <handoff.yaml>
```

## 5. 上下文隔离

### 原则

- 每个 Agent 只加载 manifest.yaml 中 context_budget 声明的上下文。
- 前序阶段的推理过程不传递给下游 Agent。
- 只传递 handoff YAML 中的 confirmed_facts 和 artifacts。
- 编排者只保留阶段状态摘要，不保留各阶段的完整对话。

### 上下文预算示例

| Agent | Required | Optional | Forbidden Full Scan |
| --- | --- | --- | --- |
| Requirements | AGENTS.md, .specify/memory/index.md | domain docs, knowledge cards | true |
| Design | 需求说明书, AGENTS.md | source code, existing contracts | true |
| Tasks | 需求说明书, 技术设计说明书 | source code | true |
| Implement | 任务规划 | 需求/设计/规则/代码/测试 | true |
| Bugfix | bug report | source code, tests, logs | true |

## 6. 跨 Agent Evidence 信任

### 信任规则

| Evidence Level | 信任方式 | 说明 |
| --- | --- | --- |
| L1 Context | 下游可直接信任 | 上下文证据，如已读取的代码、文档 |
| L2 Decision | 下游可信任，但需检查 confirmed_facts | 决策证据，如用户确认、正式 SDD 产物 |
| L3 Gate | 编排者必须重新运行校验器确认 | 门禁证据，如测试结果、构建结果 |

### 并行 Agent 的 Evidence 合并

- 每个 Agent 的 L3 Evidence 只对自己的任务子集有效。
- 编排者必须在所有并行 Agent 完成后，重新运行全量回归验证。
- 如果并行 Agent 的修改产生冲突，编排者必须停止并报告冲突。

## 7. 降级策略

### 降级触发条件

- 平台适配文件声明 multi_agent: false -> 降级到 Tier 0
- 平台适配文件声明 parallel: false -> 降级到 Tier 1
- Agent 线程创建失败 -> 降级到 Tier 0

### 降级不降质

降级只影响执行方式，不影响产物质量：

- handoff YAML 格式不变
- Evidence 要求不变
- 校验器不变
- 用户确认门禁不变
- 产物路径和格式不变

## 8. 平台适配文件示例

### Codex（openai.yaml）

```yaml
adapter:
  platform: codex
  capabilities:
    multi_agent: true
    parallel: true
    thread_handoff: true
  spawn_method: create_thread
  handoff_method: handoff_thread
  context_isolation: true
```

### Claude Code（claude.yaml，待创建）

```yaml
adapter:
  platform: claude-code
  capabilities:
    multi_agent: true
    parallel: false
    thread_handoff: false
  spawn_method: subagent
  handoff_method: file_based
  context_isolation: true
```

### Qder / Trace（qder.yaml / trace.yaml，待创建）

```yaml
adapter:
  platform: qder
  capabilities:
    multi_agent: false
    parallel: false
    thread_handoff: false
  spawn_method: none
  handoff_method: file_based
  context_isolation: false
```

## 9. 新增平台适配步骤

为新的 AI 工具创建适配文件：

1. 在技能的 agents/ 目录下创建 <platform>.yaml。
2. 声明 adapter.platform、adapter.capabilities、adapter.spawn_method 和 adapter.handoff_method。
3. 运行 validate_platform_neutrality.py --platform <platform> 校验。
4. 在业务项目的 AGENTS.md 中记录团队使用的平台列表。
5. 编排者读取当前平台的适配文件，决定执行 Tier。
