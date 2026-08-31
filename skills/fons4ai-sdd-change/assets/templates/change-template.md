# CR-xxx <变更标题>

> 功能标识：`<feature-slug>`
> 变更类型：微调 | 扩展 | 重构 | 数据结构变更 | 契约变更 | 纯文档修正
> SDD 等级：`S1|S2`
> 文档状态：正式 | 草案-待确认
> 规划模式：single-file | task-pack
> 创建日期：YYYY-MM-DD

## 1. 变更摘要

- 用户诉求：
- 本次变更结论：
- 不变更的影响：

## 2. 路由与基线判断

- FeatureLifecycle：accepted | released | <有证据的其他状态>
- ExternalizedBaseline：yes | no
- 已有不可逆效果：否 | 是，说明 DDL、真实数据、公共契约或外部系统影响
- CR 触发条件：已验收 | 已发布 | 已外部化 | 已有不可逆效果 | 用户明确要求正式审计
- 路由结果：change-request
- 路由理由：必须说明为什么不能使用 baseline-revision 或 iteration-correction
- 是否命中体量阈值：否 | 是，说明
- 新 Feature/继任 Feature：不适用 | `<feature-slug>`
- DependsOn：无 | `<feature-slug>`
- Supersedes：无 | `<feature-slug>`
- 用户决定：pending | approved，证据摘要

## 3. 当前状态检查

- 未完成任务或 Task Pack：无 | Txxx / TP-xxx，处理方式
- 历史 CR 未完成项：无 | CR-xxx，处理方式
- 文档与代码一致性：一致 | 存在差异，说明
- 技术设计与实现一致性：一致 | 存在差异，说明
- 前置阻塞：无 | 有，说明

## 4. 影响范围

- 需求影响：无 | 有，说明
- 技术设计影响：无 | 有，说明
- 代码影响：无 | 有，涉及文件
- 测试影响：只记录风险与最低证据意图；具体测试文件和动作由 implement 检查后确定
- BehaviorRisk: none | low | medium | high
- TestIntent: none | reuse | gap-to-confirm
- MinimumEvidence: none | compile | unit | contract | integration | e2e | manual
- TestBasis: 可观察行为风险和最低证据下限；不得在变更规划阶段预置新增测试或 full 回归
- 接口/契约影响：无 | 有，说明
- 权限/安全影响：无 | 有，说明
- 兼容/回滚影响：无 | 有，说明

## 5. 需求与 AC 变化

- 新增 AC：无 | AC-xxx
- 变更 AC：无 | AC-xxx
- 删除 AC：无 | AC-xxx
- REQ/AC 映射调整：无 | 有，说明

## 6. 技术设计影响

- 关键设计决策：不变 | 变化，D-xxx
- API/RPC/消息：不适用 | 具体影响
- 领域规则/状态流转：不适用 | 具体影响
- 数据/事务/一致性：不适用 | 具体影响
- 安全/兼容/回滚：不适用 | 具体影响
- 是否需要重新确认设计：否 | 是，原因

## 7. 数据结构与 DDL 影响

- 是否涉及结构变更：否 | 是
- SQL 当前结构快照：不适用 | `.specify/sql/<database_or_service>/<business_model>.sql`
- SQL DDL 动作：无 | 新增 | 更新 | 重命名
- 现状证据：不适用 | 已确认 | 待确认
- 执行型变更 DDL：不适用 | `<project-migration-path>.sql` | `<feature-dir>/ddl-changes/CR-xxx-<model>.sql`
- 执行责任方：不适用 | 用户/DBA/迁移流程
- 执行确认：不适用 | 用户确认 | 只读验证

## 8. 回归与回滚

- 回归范围：
- 全量回归触发：无 | <明确风险触发条件>
- 证据复用策略：不适用 | <可复用 Evidence、输入指纹和失效条件>
- 回滚方案：不适用，原因 | 具体方案
- S2 风险 Gate：不适用 | 需要，说明

## 9. 长期知识影响

- 是否产生长期知识影响：否 | 是
- 影响类型：无 | 业务规则 | 技术方案 | 数据结构 | 接口契约 | 治理规则 | 其他
- 影响说明：
- 处理边界：由 `fons4ai-knowledge-summary` 在用户显式触发后处理，本 CR 不生成知识同步任务。

## 10. 文档更新

- 需求说明书：不更新 | 更新章节
- 技术设计说明书：不更新 | 更新章节
- V1 任务规划：不适用 | 追加任务 Txxx（已获得继续单文件决定）
- V2 任务索引：不适用 | 登记 Task Pack TP-xxx
- 变更记录：已追加 | 不适用，原因

## 11. 增量任务

可执行任务正文只能存在于 V1 活动任务规划或 V2 Task Pack。本节只记录引用。

| TaskPack | 任务 ID | 任务摘要 | AC | 文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| TP-xxx / V1 | Txxx | <摘要> | AC-xxx | `tasks/CR-xxx-TP-xxx-<名称>.md` | draft |

## 12. 实现确认门禁

- 状态：等待用户确认
- 规划产物不等于实现授权。
- V1：`执行` 默认执行全部未完成任务；可回复 `执行 T001,T002`。
- V2：`执行` 只执行当前活动、已批准 Task Pack；可回复 `执行 TP-xxx`、`执行 Txxx` 或 `执行全部活动任务包`。
