# Fons4AI Engineering

Fons4AI Engineering 是面向企业软件交付的 Harness Engineering 实践仓库。

本仓库当前聚焦通过 SDD、项目知识基线、技能契约、项目规则、证据门禁和验证闭环，帮助 Codex/Agent 从“能写代码”进入“能按团队工程标准交付”的状态。

## 项目定位

Fons4AI Engineering 的当前定位是：

> 面向企业软件交付的 Agent Harness Engineering 体系。

这里的 Harness Engineering 指对 Agent 工作环境进行工程化驾驭，包括：

- 明确任务意图、边界和完成定义。
- 组织 Agent 需要读取的项目上下文。
- 通过技能契约约束不同工作角色。
- 用项目规则和验证门禁限制高风险行为。
- 将失败、验证和评审结果沉淀为可复用资产。

本仓库不是通用业务脚手架，也不是单纯的 prompt 集合。它维护的是跨项目可复用的 Agent 工程治理资产。

## 与 Loop Engineering 的关系

本仓库当前优先落地 Harness Engineering，长期演进目标包含 Loop Engineering。

```text
Prompt Engineering
  -> Harness Engineering
      -> Loop Engineering
```

- Harness Engineering 解决“如何驾驭 Agent 完成受控交付”。
- Loop Engineering 解决“如何让执行结果、失败原因和验证反馈持续回流，推动体系自我改进”。

因此，Fons4AI Engineering 的阶段性定位是：

> 当前以 Harness Engineering 为主线，后续在跨项目反馈、失败归因、回放验证和自动评估成熟后，演进为 Loop Engineering 体系。

## 核心资产

当前仓库主要包含以下资产：

- `skills/`：Fons4AI 技能定义，包括 SDD、BUG 修复、知识建模、项目规则和环境准备等工作流。
- `scripts/`：用于校验技能契约、Feedback Harness 入口、规则文档或工作产物的脚本。
- `onboarding/business-project/`：业务项目 Harness 接入编排与验收说明，负责说明技能执行顺序和最小结构校验，不复制技能产物模板。
- `skills-lock.json`：技能来源与版本锁定信息。

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

当前仓库级校验入口：

```text
scripts/validate_skill_contracts.py --skills-root skills
scripts/validate_feedback_harness.py
scripts/validate_business_project_harness.py --target <业务项目根目录>
```

其中 `validate_feedback_harness.py` 用于检查 Feedback Harness 的总入口资产是否齐全：实现报告、BUG 修复报告、环境准备度、上游反馈单、反馈路径约定和核心校验器。
`validate_business_project_harness.py` 用于检查业务项目是否具备最小 Harness 接入结构。

## 业务项目接入

业务项目最小接入包位于：

- [业务项目 Harness 接入编排与验收](onboarding/business-project/README.md)

建议依次执行：

1. `fons4ai-knowledge-bootstrap`
2. `fons4ai-generate-project-rules`
3. `fons4ai-agent-env-readiness`
4. `scripts/validate_business_project_harness.py --target <业务项目根目录>`
5. 选择一个低风险真实需求做 SDD MVP 回放

## SDD 的位置

SDD 是当前 Fons4AI Harness 的核心执行骨架，但不是全部。

SDD 主要负责把需求、设计、任务、实现和验证串成可追踪链路：

```text
需求说明书
  -> 技术设计说明书
      -> 任务规划
          -> 实现与验证
              -> 知识汇总
```

对于低风险、小范围或非功能性任务，体系应允许轻量处理；对于高风险任务，必须通过更严格的 SDD、证据和验证门禁。

## 落地优先级

当前优先级如下：

1. 概念归一：统一 Harness Engineering 定位、术语和路线。
2. 结构升级：整理技能、规则、模板和校验脚本，使其符合 Harness 分层。
3. 反馈闭环：建立失败报告、上游反馈、回放验证和跨项目改进机制。

## 设计原则

- 风险分层，不用同一套重流程处理所有任务。
- 规则短而硬，解释和样例放到专门文档。
- 优先机器可验证，其次人工可审查，最后才是文字约束。
- 项目私有问题留在业务项目，跨项目通用问题反馈回本仓库。
- 不把一次性经验上升为通用规则，除非经过脱敏、归因和抽象。
- 技能不是提示词集合，而是具备输入、前置条件、输出和完成标准的工作契约。

## 文档入口

- [Harness Engineering 方案](docs/harness-engineering.md)
