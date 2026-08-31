# TP-xxx <任务包名称>

> TaskPack：`TP-xxx`
> Feature：`<feature-slug>`
> PackStatus：draft | ready | approved | in-progress | done | deferred | superseded | archived
> ApprovalStatus：pending | approved | rejected | not-required
> SourceChange：INIT | ITER-xxx | CR-xxx
> DependsOn：无 | TP-xxx | Txxx
> 覆盖 AC：AC-xxx
> 创建日期：YYYY-MM-DD
> 更新日期：YYYY-MM-DD

## 1. 任务包目标

- 可感知交付结果：
- 包含范围：
- 不包含范围：
- 外部前置条件：无 | <环境、凭据、DBA、Provider、网络等>
- 完成层级：Development | Integration | Deployment | Release

## 2. 任务列表

> TestIntentVersion: 1
> ImplementationContractVersion: 2

- [ ] Txxx 用动宾短语描述任务
  - 通俗解释: 这个任务完成后，用户或系统会发生什么可感知变化。
  - AC: AC-xxx
  - DesignRefs: 技术设计说明书 §x | TD-xxx | contracts/<contract>.md | CR-xxx
  - Implementation: 1) 在已确认的规则归属层完成核心动作；2) 复用现有组件完成调用、映射或持久化；3) 按设计处理错误、事务或幂等边界。
  - Invariants: 不改变已确认的业务口径、状态约束、数据语义和兼容承诺。
  - NonGoals: 不修改当前任务包之外的公共契约、数据结构或相邻流程。
  - Files: existing:path/to/source; new-confirmed:path/to/new-file
  - Depends: 无 | Txxx | TP-xxx
  - BehaviorRisk: none | low | medium | high
  - TestIntent: none | reuse | gap-to-confirm
  - MinimumEvidence: none | compile | unit | contract | integration | e2e | manual
  - TestBasis: 说明可观察行为风险和最低证据下限；具体测试动作与回归范围由 implement 基于当前覆盖决定。
  - Verification: 给定什么输入或前置条件，执行什么动作，应该得到什么可观察结果。
  - Quality: 确认可读性、领域规则归属、重复代码、工具复用、数据口径和依赖门禁。
  - Done: 客观完成标准。

## 3. 包级验证与完成标准

- 必需验证：
- 最小回归：
- 最低证据组合：<各任务 MinimumEvidence 的风险覆盖组合>
- 实施阶段聚合：由 implement 汇总实际 `AffectedTests` 并决定回归范围；规划阶段不预置测试清单或 full 回归。
- 外部 Gate：无 | <责任方、状态和恢复条件>
- Done：包内必需任务完成、验证通过，且未完成外部 Gate 已明确归属和状态。

## 4. 风险与回滚

- 风险：无 | <风险>
- 回滚：不适用，原因 | <回滚方式>
- 暂缓项：无 | <暂缓内容、责任方和恢复条件>
