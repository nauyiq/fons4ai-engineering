# Fons4AI Engineering

Fons4AI Engineering 是一套用于把业务仓库初始化为 Harness Engineering 项目的 Template Kit。

本仓库不是集中式跨项目 Harness 工程，也不替业务项目定义业务边界、领域边界、团队规则或验证等级。它维护可安装技能、模板、上游校验器和说明文档。业务项目引入配套技能后，在自己的仓库内生成并维护项目级 Harness Engineering 资产。

## 项目定位

Fons4AI Engineering 的定位是：

> 面向企业软件交付的 Agent Harness Engineering Template Kit。

这里的 Harness Engineering 指对 Agent 工作环境进行工程化驾驭，包括：

- 明确任务意图、边界和完成定义。
- 组织 Agent 需要读取的项目上下文。
- 通过技能契约约束不同工作角色。
- 用项目规则和验证门禁限制高风险行为。
- 将失败、验证和评审结果沉淀为项目本地资产或脱敏上游反馈。

## 目录结构

```text
skills/                  # 可安装技能，负责生成/维护项目本地资产
templates/               # 通用交接和报告模板
scripts/validators/      # 上游校验器
docs/                    # Kit 使用说明、契约标准、分层说明
```

## 业务项目自治

业务项目接入后，自己就是一个 Harness Engineering 项目。上游 Template Kit 只提供生成方法、默认骨架、校验标准和反馈通道。

业务项目本地通常会形成：

```text
AGENTS.md
.specify/memory/
.specify/rules/
spec/features/
spec/reports/harness-feedback/
```

推荐接入顺序：

1. 使用 `fons4ai-knowledge-bootstrap` 建立项目知识基线和技能路由入口。
2. 使用 `fons4ai-generate-project-rules` 生成项目规则。
3. 运行 `scripts/validators/validate_business_project_harness.py --target <业务项目根目录>`。
4. 选择一个低风险真实需求做 SDD MVP 回放。
5. 发现通用 Harness 问题时，使用 `fons4ai-harness-feedback` 生成脱敏上游反馈单。

## 业务开发入口

业务项目完成最小接入后，日常开发优先按工作类型选择入口：

| 场景 | 推荐入口 | 说明 |
| --- | --- | --- |
| 正常新需求开发 | `fons4ai-sdd-feature-workflow` | 编排需求、设计和任务规划，校验后停止等待实现确认 |
| 已有功能迭代 | `fons4ai-sdd-change` | 生成 CR 和增量任务，停止等待实现确认 |
| BUG、异常、回归失败 | `fons4ai-bugfix-workflow` | 复现、修复、验证并生成 BUG 修复报告 |
| 用户确认实现 | `fons4ai-sdd-implement` | 只执行已规划且已授权的任务 |
| 低风险小变更 | `fons4ai-sdd-quick-path` | S0 快路径，生成快速变更记录，确认后实现 |

## 技能分类

Fons4AI 技能按用户入口和职责边界分为以下类型：

| 类别 | 技能 | 分类原因 |
| --- | --- | --- |
| 流程编排类 | `fons4ai-sdd-feature-workflow` | 串联阶段、控制停止点，不直接写业务代码 |
| SDD 阶段产物类 | `fons4ai-sdd-requirements`、`fons4ai-sdd-design`、`fons4ai-sdd-tasks`、`fons4ai-sdd-change` | 生成或调整需求、设计、任务规划和 CR |
| 实现执行类 | `fons4ai-sdd-implement` | 执行已规划且已授权的任务，更新代码、测试、任务状态和实施报告 |
| 轻量快路径类 | `fons4ai-sdd-quick-path` | S0 等级，低风险小变更用单份快速变更记录替代 SDD 三件套 |
| BUG 修复闭环类 | `fons4ai-bugfix-workflow` | 面向缺陷、异常和回归失败，独立完成复现、修复、验证和报告 |
| 知识库类 | `fons4ai-knowledge-bootstrap`、`fons4ai-domain-knowledge-modeling`、`fons4ai-knowledge-summary` | 建立、深化和汇总项目知识事实 |
| 规则生成类 | `fons4ai-generate-project-rules` | 把已验证项目事实和团队决策固化为 `.specify/rules/` |
| 反馈治理类 | `fons4ai-harness-feedback` | 把业务试点中的通用 Harness 问题整理为脱敏上游反馈单 |


## 体系分层

Fons4AI Harness Engineering 按 6 层组织：

| 层级 | 目标 | 典型产物 |
| --- | --- | --- |
| Intent Harness | 明确用户意图、范围和验收标准 | 需求说明书、CR、AC、澄清问题 |
| Context Harness | 控制 Agent 应加载的上下文 | `AGENTS.md`、`.specify/memory/`、知识卡片 |
| Skill Harness | 约束 Agent 按角色执行 | `skills/*/SKILL.md`、技能契约、handoff |
| Rule Harness | 固化团队工程规则 | `.specify/rules/`、规则模板、校验脚本 |
| Feedback Harness | 证明任务完成并记录失败 | 测试结果、实施报告、失败报告 |
| Learning Harness | 跨项目沉淀可复用经验 | 失败案例、回放样例、`spec/reports/harness-feedback/` 上游反馈单 |

## 校验入口

仓库级校验入口：

```text
scripts/validators/validate_skill_contracts.py --skills-root skills
scripts/validators/validate_feedback_harness.py
scripts/validate_all.py
scripts/validators/validate_business_project_harness.py --target <业务项目根目录>
```

`scripts/validate_all.py` 是仓库级一键入口。业务项目接入校验优先使用 `scripts/validators/validate_business_project_harness.py --target <业务项目根目录>`。

## 与 Loop Engineering 的关系

本仓库当前优先提供 Harness Engineering Template Kit，并已进入 Loop Phase 1：人工反馈闭环标准化。长期目标是逐步演进为具备回放样例和自动评估能力的 Loop Engineering。

```text
Prompt Engineering
  -> Harness Engineering
      -> Loop Engineering
```

- Harness Engineering 解决“如何驾驭 Agent 完成受控交付”。
- Loop Engineering 解决“如何让执行结果、失败原因和验证反馈持续回流，推动体系自我改进”。
- Loop Phase 1 先标准化 `上游反馈单 -> Loop 改进记录 -> 修改清单 -> 校验 -> 全局 skills 同步`，不引入无人值守自动循环。

## Loop Phase 1

Loop Phase 1 的标准产物：

```text
spec/reports/loop-improvements/<yyyymmdd>-<问题简述>-loop改进记录.md
```

使用模板：

```text
templates/loop-improvement-record-template.md
```

每次通用上游改进应记录来源反馈单、用户决策、修改清单、验证命令、全局 skills 同步状态和关闭结论。

## SDD 的位置

SDD 是当前 Fons4AI Harness 的核心执行骨架之一，但不是全部。

```text
fons4ai-sdd-feature-workflow
  -> fons4ai-sdd-requirements
      -> fons4ai-sdd-design
          -> fons4ai-sdd-tasks
              -> 等待用户确认实现
                  -> fons4ai-sdd-implement
                      -> 阻塞时由 fons4ai-sdd-implement 诊断并路由（可选）
                      -> 用户显式触发知识汇总（可选）
                          -> fons4ai-knowledge-summary
```

对于低风险、小范围或非功能性任务，体系应允许轻量处理；对于高风险任务，必须通过更严格的 SDD、证据和验证门禁。

## 设计原则

- 业务项目自治：项目私有边界、规则、验证能力和知识沉淀留在业务项目。
- 上游只维护通用能力：技能、模板、校验器和脱敏反馈闭环。
- 风险分层，不用同一套重流程处理所有任务。
- 规则短而硬，解释和样例放到专门文档。
- 优先机器可验证，其次人工可审查，最后才是文字约束。
- 不把一次性经验上升为通用规则，除非经过脱敏、归因和抽象。

## 文档入口

- [Harness Engineering 方案](docs/harness-engineering.md)
- [Loop Phase 1](docs/loop-phase-1.md)
- [Harness Layer Map](docs/harness-layer-map.md)
- [Skill Contract Standard](docs/skill-contract-standard.md)
