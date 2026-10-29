---
name: fons4ai-sdd-change
description: 基于已有项目知识或过程基线调整功能、契约和实现。普通自动路由需要相关基线；显式调用但缺少基线时先重建最小事实。新能力和 BUG 分别使用规划与修复入口。
---

# SDD 变更

先定位相关 Wiki 专题或需求/设计/任务文档，再核实当前代码和测试。无相关基线时不自动进入此技能：按 [重新规划与转接](../fons4ai-sdd-plan/references/replanning.md) 在当前工作中核实事实、选择轻量处理或正式规划。用户显式调用时读 [基线恢复](references/baseline.md)，不能凭空写“原行为”，内部技能转接不算用户显式调用。新能力转 [规划](../fons4ai-sdd-plan/SKILL.md)。

按情况仅加载一条分支：

- 明确、局部、可逆且无重大业务/契约/数据/安全影响，可包含简单行为变化：[小变更](references/local-change.md)。
- 复杂或重大业务/契约/数据/安全变化，或需正式调整规格：[规格变更](references/spec-change.md)。

恢复既定正确行为属于 [BUG 修复](../fons4ai-bugfix-workflow/SKILL.md)。当前实现产生的局部缺陷留在实现闭环处理，不反复路由。

修改通用能力前读取 [依赖核查](../fons4ai-knowledge/references/dependency-discovery.md)。验证结果才能支持完成声明；相关知识通过 [更新与合并](../fons4ai-knowledge/references/consolidate.md) 增量维护。

仅变更规划授权时止于可评审结果。正式规格变更按 [实施授权](../fons4ai-sdd-plan/references/approval.md) 确认当前基线，轻量变更按已有有效授权处理；同一已确认基线续做不重复确认，未授权的范围扩大应明确说明。
