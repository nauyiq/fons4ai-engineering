# TP-xxx <任务包名称>

> TaskPack：`TP-xxx`
> Feature：`<feature-slug>`
> PackStatus：draft | ready | approved | in-progress | done | deferred | superseded | archived
> ApprovalStatus：pending | approved | rejected | not-required
> SourceChange：INIT | CR-xxx
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

> TestDecisionVersion: 1

- [ ] Txxx 用动宾短语描述任务
  - 通俗解释: 这个任务完成后，用户或系统会发生什么可感知变化。
  - AC: AC-xxx
  - 来源: 技术设计说明书 §x | CR-xxx
  - Files: path/to/source; path/to/test
  - Depends: 无 | Txxx | TP-xxx
  - BehaviorChange: none | changed | new
  - ExistingCoverage: covered | partial | missing | not-applicable
  - TestAction: none | reuse | update | add
  - TestLevel: none | unit | contract | integration | e2e | manual
  - AffectedTests: none | path/to/test | <聚焦测试命令>
  - RegressionScope: none | focused | affected | module | full
  - TestReason: 说明可观察行为、覆盖缺口和范围依据；full 必须说明触发条件。
  - Verification: 给定什么输入或前置条件，执行什么动作，应该得到什么可观察结果。
  - Quality: 确认可读性、领域规则归属、重复代码、工具复用、数据口径和依赖门禁。
  - Done: 客观完成标准。

## 3. 包级验证与完成标准

- 必需验证：
- 最小回归：
- 受影响测试并集：无 | <测试类、测试文件或命令>
- 全量回归触发：无 | 发布/合并门禁 | 公共契约或共享基础模块变化 | 依赖或构建配置变化 | 数据库结构或安全权限广泛影响 | 影响范围无法可靠判断 | 用户/CI 明确要求
- 外部 Gate：无 | <责任方、状态和恢复条件>
- Done：包内必需任务完成、验证通过，且未完成外部 Gate 已明确归属和状态。

## 4. 风险与回滚

- 风险：无 | <风险>
- 回滚：不适用，原因 | <回滚方式>
- 暂缓项：无 | <暂缓内容、责任方和恢复条件>
