---
name: fons4ai-bugfix-workflow
description: 处理 BUG、异常和回归。先确认预期与复现证据，局部缺陷最小修复并聚焦验证，复杂缺陷按需记录调查；不把新需求当 BUG。
---

# BUG 修复

核实预期行为来自需求、调用契约、测试还是用户说明。当前实现不自动等于正确基线。

- 已有清楚预期、可复现、局部低风险：复用失败测试或增加最小回归用例，修复后执行聚焦与受影响验证，不生成报告。
- 影响不明、跨模块、数据/安全/线上事故：读 [复杂缺陷调查](references/investigate.md)，先定位原因再修改。

涉及框架或第三方行为时先读 [依赖核查](../fons4ai-knowledge/references/dependency-discovery.md)，不能以“源码搜不到”推断没有能力。行为修复遵循 [TDD](../fons4ai-sdd-implement/references/tdd.md)，完成时读 [完成检查](../fons4ai-sdd-implement/references/completion.md)。

预期行为发生变化时按 [重新规划与转接](../fons4ai-sdd-plan/references/replanning.md) 核实基线，再决定进入变更或在当前调查中补充规划；实现过程中自己引入的缺陷直接修复。只报告实际复现、修改、验证和残留风险；环境无法复现时明确限制。完成后只沉淀本次有长期价值的事实。
