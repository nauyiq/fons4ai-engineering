# 风险驱动测试决策策略

本文定义 Fons4AI 技能体系中统一的 Test Decision Gate、测试编写边界、回归范围和证据复用规则。

## 1. 核心原则

- 生产代码变化不等于测试代码必须变化。
- 只有可观察行为变化且现有测试存在明确覆盖缺口时，才新增或更新测试。
- 已有测试能够证明行为时优先复用；部分覆盖时优先扩展或参数化现有测试。
- 使用能证明风险的最低有效测试层级，不用大量 Mock 单测替代契约、事务、数据库或跨服务边界验证。
- 开发阶段运行聚焦或受影响测试；全量回归属于明确风险门禁，不属于每个 Agent Step。

## 2. 规划阶段：Test Intent

| 字段 | 值 |
| --- | --- |
| `BehaviorRisk` | `none|low|medium|high` |
| `TestIntent` | `none|reuse|gap-to-confirm` |
| `MinimumEvidence` | `none|compile|unit|contract|integration|e2e|manual` |
| `TestBasis` | 可观察行为风险和最低证据下限依据 |

任务规划使用 `TestIntentVersion: 1`。它只描述风险和最低证明意图，不判断当前测试是否覆盖，不指定要新建或修改哪些测试，也不提前决定回归范围。`gap-to-confirm` 表示 implement 必须检查覆盖缺口，不代表必须新增测试。

## 3. 实施阶段：Test Decision Gate

implement 读取当前生产代码和直接相关测试后，才记录以下字段：

| 字段 | 值 |
| --- | --- |
| `BehaviorChange` | `none|changed|new` |
| `ExistingCoverage` | `covered|partial|missing|not-applicable` |
| `TestAction` | `none|reuse|update|add` |
| `TestLevel` | `none|unit|contract|integration|e2e|manual` |
| `AffectedTests` | 测试路径、测试类、聚焦命令或 `none` |
| `RegressionScope` | `none|focused|affected|module|full` |
| `TestReason` | 可观察行为、覆盖缺口、测试层级和回归范围依据 |

实施期一致性要求：

- `BehaviorChange: none` 不得搭配 `TestAction: update|add`。
- `ExistingCoverage: covered` 默认使用 `none|reuse`。
- `TestAction: update|add` 必须选择非 `none` 的测试层级。
- `RegressionScope: full` 必须记录明确触发条件。

历史规划产物中的 `TestDecisionVersion: 1` 继续兼容校验；新规划不得同时声明 `TestDecisionVersion: 1` 与 `TestIntentVersion: 1`。

## 4. 全量回归触发条件

只有以下情况允许选择 `full`：

- 发布或合并门禁；
- 公共契约或共享基础模块变化；
- 依赖锁文件或构建配置变化；
- 数据库结构、安全或权限产生广泛影响；
- 影响范围无法可靠判断；
- 用户或 CI 明确要求。

多 Agent 汇总默认执行各 implement 结果中实际 `AffectedTests` 的去重并集和冲突接口的最小集成验证，不自动升级全量回归。

## 5. Evidence Ledger

可复用证据至少记录命令、测试范围、结果、源码指纹、测试指纹、依赖/构建配置指纹、适用任务、失效条件和原始输出。只有输入指纹未变化且原始输出可核验时才能复用。

仅服务重启时，重跑健康检查和受影响运行态 smoke test；输入未变化的静态检查、单元测试和构建证据保持有效。
