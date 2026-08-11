# Fons4AI Task Planning V2

## 1. 选择规划模式

优先保持最小充分结构：

- 小型 S1、单一交付边界、任务较少且无需分批确认：使用 V1 单文件任务规划。
- 多模块、多阶段、多责任边界、需要分批评审/执行，或预计持续变更：使用 V2 任务索引与 Task Pack。
- 大型零到一系统先拆 Initiative 下的独立 Feature；不要用 Task Pack 代替本应独立验收的 Feature。

出现以下任一信号时，必须评估 V2 或拆分 Feature，并记录决定：

- 单一规划预计超过 12 个任务。
- Feature 活动与历史任务合计达到 30 项。
- 活动任务规划超过 40 KB 或估算超过 12,000 Token。
- 变更请求达到 3 轮且本轮新增任务不少于 8 项。
- 已完成、停止或已替代内容超过任务正文的 50%。
- 新增工作已经形成可独立验收的业务或技术能力。

这些数字是拆分评估阈值，不是机械拆分命令。独立可验收能力优先新建 Feature；同一 Feature 内的实现分片才使用 Task Pack。

## 2. V2 目录与职责

```text
<feature-dir>/
  <功能中文名>-任务索引.md
  tasks/
    TP-001-<任务包名称>.md
    TP-002-<任务包名称>.md
```

任务索引负责：

- 列出所有 Task Pack、状态、审批状态、AC、依赖和路径。
- 标识唯一的当前活动 Task Pack，或说明为什么没有活动包。
- 汇总阻塞、延期、已替代和已归档状态，不复制完整任务正文。
- 提供用户执行入口和 Feature 级依赖图。

Task Pack 负责：

- 承载一个内聚、可评审、可批准、可执行的任务集合。
- 记录 `PackStatus`、`ApprovalStatus`、`SourceChange`、`DependsOn` 和覆盖 AC。
- 包含完整任务字段和包级完成标准。
- 获得批准后冻结任务目标；后续范围变化使用新 Task Pack。

## 3. Feature 与 Task Pack 边界

优先按业务能力拆 Feature，再按实施边界拆 Task Pack：

1. 用户管理、订单管理、结算、报表等独立用户价值使用独立 Feature。
2. 项目脚手架、公共认证基线、共享 UI 壳层等技术基础可作为 Foundation Feature。
3. 一个 Feature 内优先按可演示的垂直切片拆包；只有前后端可独立交付或所有权明确分离时，才按技术层拆包。
4. 数据迁移、外部集成、部署或发布 Gate 与代码开发责任不同时，拆成独立 Task Pack 或清晰的 Gate 任务。

## 4. 状态模型

`PackStatus` 只允许：

- `draft`：正在规划，不可执行。
- `ready`：内容可评审，等待批准。
- `approved`：已批准，可在依赖满足后执行。
- `in-progress`：正在执行。
- `done`：包内必需任务已关闭。
- `deferred`：因外部前置条件或用户决定延期。
- `superseded`：被新 Task Pack 或继任 Feature 替代。
- `archived`：只读历史。

`ApprovalStatus` 只允许 `pending`、`approved`、`rejected` 或 `not-required`。

只有 `PackStatus: approved|in-progress` 且 `ApprovalStatus: approved|not-required` 的 Task Pack 可以进入实现。

## 5. 标识与依赖

- Task Pack ID 使用 `TP-001`、`TP-002`，Feature 内唯一且不复用。
- Task ID 继续使用 `T001`、`T002`，在整个 Feature 的活动和历史 Task Pack 中全局唯一。
- `DependsOn` 可引用 Task Pack 或 Task ID；依赖图不得形成环。
- 已批准、已完成、已替代或已归档的 Task Pack 不重排、不覆盖、不追加新任务。
- Task Pack 文件名以稳定 ID 开头，可增加来源 CR，例如 `TP-005-CR-002-订单退款.md`。

## 6. 大型需求的渐进规划

大型需求不要一次展开全部任务：

1. 先生成任务索引草案，列出 Task Pack 名称、目标、AC、依赖和预计任务数。
2. 用户确认任务包地图后，将首个或用户指定 Task Pack 展开为详细任务。
3. 每个 Task Pack 单独评审和批准。
4. 后续 Task Pack 在其上游设计或依赖稳定后再展开。

## 7. 变更路由

- 基线尚未批准：修订原草案并更新版本，不创建 CR。
- 已批准或已开始实施的同一能力局部变更：创建 CR 和独立 Change Task Pack。
- 新增独立 AC、业务模块或可独立验收能力：默认新建 Feature。
- 核心流程重写、主数据模型重构、公共契约大改，或达到体量阈值：创建继任 Feature，并使用 `DependsOn`、`Supersedes` 建立关系。
- CR 只引用 Task Pack 和任务 ID，不复制完整任务正文。

## 8. 执行语义

- V2 中 `执行` 只选择任务索引标记的当前活动、已批准 Task Pack。
- `执行 TP-002` 选择指定已批准 Task Pack。
- `执行 T004,T005` 选择指定未完成任务，并检查包级批准和依赖。
- `执行全部活动任务包` 才允许选择所有已批准且依赖可满足的活动包。
- `看看`、`继续看`、`下一步`、任务索引存在或 Task Pack 生成完成都不是实现授权。

## 9. V1 兼容

- 不迁移历史 V1 Feature 也必须继续可验证和实现。
- V1 变更仍可在用户明确接受且未触发拆分评估时追加任务。
- 一旦 V1 Feature 转为 V2，原任务规划冻结并在新任务索引中登记为历史来源；不得同时维护两个活动任务真相源。
