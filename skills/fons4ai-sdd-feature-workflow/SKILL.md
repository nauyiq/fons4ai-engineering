---
name: fons4ai-sdd-feature-workflow
description: "Fons4AI 正常新需求开发 SDD 编排技能。用于把全新功能需求按 fons4ai-sdd-requirements -> fons4ai-sdd-design -> fons4ai-sdd-tasks 编排为 SDD 三件套，运行 SDD 产物校验，并在实现前停止等待用户确认。只有当用户明确指定该技能、明确要求使用 Fons4AI/SDD 工作流处理全新功能，或启用 Fons4AI 路由且当前意图匹配正常新需求开发时使用。"
---

# Fons4ai-sdd-feature-workflow

## Contract

### Inputs

- Required: 用户的新功能、新业务能力或从 0 到 1 的需求描述。
- Optional: `AGENTS.md`、`.specify/memory/index.md`、项目规则、领域/能力域文档、知识卡片、接口/产品/测试资料和用户指定的需求材料。
- Forbidden assumptions: 不得把 BUG 修复、已有功能迭代、单纯实现授权或知识沉淀请求误判为正常新需求；不得替阶段技能补写业务规则、技术方案或任务细节。

### Preconditions

- Entry gates: 满足触发条件之一，且用户请求属于全新需求开发；如类型不明确，必须先分流确认。
- Required source artifacts: 无固定前置 SDD 产物；如发现目标能力已有正式 SDD 目录，必须先判断是否应转入 `fons4ai-sdd-change`。
- Required repository facts: 只读取判断工作流类型和启动需求澄清所需的最小上下文，不默认全量读取知识库、规则、SQL 或历史 spec。

### Outputs

- May create or update: 由下游阶段技能生成或更新的 `spec/features/<yyyymmdd>/<功能中文名>-需求说明书.md`、`<功能中文名>-技术设计说明书.md`、`<功能中文名>-任务规划.md`。
- Must not create or update: 业务代码、测试代码、实施报告、BUG 修复报告、CR、知识库正文、SQL 当前结构快照、执行型 DDL 和生产配置。
- Output location: `spec/features/<yyyymmdd>/`。

### Exit Criteria

- Success: 需求说明书、技术设计说明书和任务规划已按阶段生成或更新，任务规划的实现确认状态保持 `pending`，SDD 产物校验通过，并明确等待用户确认实现。
- Blocked: 请求类型无法判断、需求澄清未关闭、设计证据不足、任务拆解输入不完整、SDD 产物校验失败，或发现应转入变更/BUG/实现/知识工作流。
- Failure report: 汇报当前所处阶段、阻塞原因、已生成产物、建议转入的技能和用户需要回答的最高影响问题。

### Handoff

- Next skill: 默认无自动下游；只有用户最新消息明确确认实现后，才可进入 `fons4ai-sdd-implement`。
- Required handoff fields: feature 目录、需求说明书路径、技术设计路径、任务规划路径、SDD 等级、未完成任务 ID、校验命令、校验结果、实现确认状态。
- Stop condition: 任务规划生成并通过校验后必须停止，等待用户确认实现；不得自动进入实现。

## 角色说明

你是正常新需求开发的 SDD 工作流编排者，负责把用户的新功能请求串联到三个阶段技能：

```text
fons4ai-sdd-requirements
  -> fons4ai-sdd-design
      -> fons4ai-sdd-tasks
          -> validate_sdd_artifacts.py
              -> 等待用户确认实现
```

你的职责不是替代任何阶段技能，而是控制入口分流、阶段顺序、阶段出口、校验和 handoff。

## 触发门禁

使用本技能前，必须确认至少满足以下任一条件：

1. 用户明确指定该技能，例如 `$fons4ai-sdd-feature-workflow`。
2. 用户明确要求使用 Fons4AI、SDD 或 Fons4AI 工作流处理一个全新功能或正常新需求。
3. 当前仓库作用域内存在 `AGENTS.md`，且包含 `<!-- fons4ai-skill-routing: enabled -->`，并且用户请求明显是正常新需求开发。

如果以上条件都不满足，不得自动应用本技能。应继续使用普通 AI agent 行为，或询问用户是否希望启用 Fons4AI SDD 工作流。

## 工作流分流

先判断用户请求属于哪类工作：

| 场景 | 处理方式 |
| --- | --- |
| 全新功能、全新业务能力、从 0 到 1 的需求 | 继续本技能 |
| 已有 SDD 功能要调整需求、AC、公共契约、数据语义或设计 | 转入 `fons4ai-sdd-change` |
| BUG、异常、错误行为、回归失败 | 转入 `fons4ai-bugfix-workflow` |
| 用户只是在已生成任务规划后确认实现 | 转入 `fons4ai-sdd-implement` |
| 用户只要求沉淀已验证事实 | 转入 `fons4ai-knowledge-summary` |
| 低风险小变更（文案、样式、小配置、纯重命名、日志级别） | 转入 `fons4ai-sdd-quick-path`（S0） |
| 类型不清 | 先提出一个最高影响澄清问题 |

分流时只说明推荐技能和原因，不得擅自进入会修改业务代码的技能。

## 编排步骤

1. 启动需求阶段。
   - 进入 `fons4ai-sdd-requirements` 阶段，由该阶段技能按自身职责边界和模板生成或更新需求说明书。
   - 如果需求阶段存在阻塞歧义，停止并汇报阻塞问题，不进入设计。

2. 启动设计阶段。
   - 在正式需求说明书完成后，进入 `fons4ai-sdd-design` 阶段，由该阶段技能生成或更新技术设计说明书。
   - 如果设计阶段缺少数据、契约、权限、兼容、迁移或回滚证据，停止并汇报应补充的证据或应回到的上游技能。

3. 启动任务规划阶段。
   - 在正式需求和技术设计完成后，进入 `fons4ai-sdd-tasks` 阶段，由该阶段技能生成或更新任务规划。
   - 任务规划必须保持实现确认状态为 `pending`。

4. 执行 SDD 产物校验。
   - Python 可用时运行：

```text
python skills/fons4ai-sdd-tasks/scripts/validate_sdd_artifacts.py --feature-dir spec/features/<yyyymmdd>
```

   - 如果在 `skills/fons4ai-sdd-feature-workflow` 技能目录相对路径内运行，也可使用：

```text
python ../fons4ai-sdd-tasks/scripts/validate_sdd_artifacts.py --feature-dir <feature-dir>
```

   - 校验失败时，不得声明 SDD 三件套完成；必须报告失败项，并建议回到对应阶段修复。

5. 停止等待实现确认。
   - 校验通过后输出 handoff。
   - 明确说明：下一步只有在用户回复 `执行`、`开始实现`、`继续执行` 或 `执行 T001,T002` 后，才能进入 `fons4ai-sdd-implement`。

## 职责边界

本技能不得：

- 编写、修改或输出业务代码。
- 调用或模拟 `fons4ai-sdd-implement`。
- 生成实施报告、BUG 修复报告或上游反馈单。
- 修改 `.specify/memory/`、`.specify/sql/` 或 `.specify/rules/`。
- 为了串联阶段而忽略任何阶段技能的阻塞门禁。
- 在任务规划后自动进入实现。

阶段产物的内容细节由对应阶段技能负责；本技能只负责确认阶段出口是否满足进入下一阶段的条件。
