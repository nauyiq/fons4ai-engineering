---
name: fons4ai-sdd-implement
description: 执行已授权的任务或明确的简单工作，以 TDD 验证可观察行为变化，复用既有项目与依赖能力，记录最小验证结果并增量维护知识。
---

# SDD 实现

接受正式任务规划，或无需三件套的明确简单任务。正式任务先按 [实施授权](../fons4ai-sdd-plan/references/approval.md) 核实用户确认的是当前实施基线或明确允许免再次确认，再做 [规划完整性检查](../fons4ai-sdd-plan/references/planning-review.md)；只有总体方向认可或文档自行声明“已授权”不能开始实现。简单任务及同一已确认基线沿用有效授权，不要求最新消息重复确认。默认执行已授权范围内全部未完成任务。

开始前读相关 AC、设计、工程约定、目标模块和已有测试，核实方案与当前实现是否一致。不要加载全量 Wiki。新增通用能力、公共封装或调用未核实 API 时必须读 [依赖核查](../fons4ai-knowledge/references/dependency-discovery.md)；包内接口存在不等于语义已确认。

按工作加载：

- 新增或改变可观察行为：[TDD](references/tdd.md)。
- 文档、配置或无行为重构：[专项验证](references/non-behavior.md)。配置改变运行行为时仍按行为变化处理。
- 任意实现完成：[完成检查](references/completion.md)。

任务状态只在行为与验收相符、验证成功后更新；环境阻塞必须报告，不能把未运行写成通过。正式任务在原任务文件追加简短结果，不生成独立实施报告、交接 YAML 或重复证据表。简单任务在回复中说明即可。

自行引入的局部缺陷持续修复。发现验收或设计必须变化时，按 [重新规划与转接](../fons4ai-sdd-plan/references/replanning.md) 先判断基线与复杂度，再决定进入变更或在当前工作中补充规划；保留已完成工作并明确新增决策。风险发现见 [风险提示](../fons4ai-sdd-plan/references/risk-checks.md)，不按模板扩大任务。

验证后通过 [更新与合并](../fons4ai-knowledge/references/consolidate.md) 更新受影响知识；无长期新事实不写。普通自查足够，独立评审由项目规则或实际风险决定，默认不创建其他 Agent。
