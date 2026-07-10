# SDD元数据与UI设计门禁缺失 Loop 改进记录

> 记录路径：`spec/reports/loop-improvements/20260709-SDD元数据与UI设计门禁缺失-loop改进记录.md`
> Status：Verified
> 创建日期：2026-07-09
> 负责人：用户 + Agent

## 1. 来源反馈

- 来源反馈单：`spec/reports/harness-feedback/20260709-SDD元数据与UI设计门禁缺失-上游反馈单.md`
- 关联试点项目：已脱敏
- 问题分类：SKILL_CONTRACT | TEMPLATE_GAP | VALIDATOR_GAP | EVIDENCE_GAP
- 是否进入上游改进：是

## 2. 用户决策

- 用户目标：将反馈单中的两个问题（SDD 文档元数据不一致、UI 设计 Gate 缺失）回流到上游 `fons4ai-engineering` 技能库。
- 用户确认的边界：
  - 只修改 SDD 流水线相关技能（sdd-change、sdd-implement、sdd-tasks）及其模板和校验器。
  - UI 设计 Gate 针对页面、控制台、前端、模板引擎页面等交互型交付物，不对纯后端 API 任务施加额外 Gate。
  - 文档更新时间维护规则适用于所有 SDD 正式文档模板（需求说明书、技术设计说明书、任务规划、实施报告）。
- 不允许修改的范围：非 SDD 流水线技能（bugfix、knowledge、domain-knowledge 等）。
- 需要用户再次确认的事项：无。

## 3. 问题归因

- 现象摘要：
  1. 正式 SDD 文档正文变更后，头部更新时间未同步更新。
  2. 增量实现涉及可视化管理页面时，Agent 直接进入页面代码实现，未先输出 UI 设计确认，导致页面视觉形态偏原始。
- 根因判断：
  1. SDD 文档元数据治理缺口：当前技能流程强调正文、任务状态和验证证据，但没有把"修改正式文档必须同步元数据"做成强规则或校验项。
  2. SDD 实现职责边界缺口：增量变更进入实现阶段后，Agent 对页面类任务采用了"功能闭环优先"的后端式实现路径，没有自动识别 UI 设计 Gate。
- 项目私有因素：无。
- 上游通用因素：有。
  - 文档更新时间与正文变更不一致属于通用 SDD 文档治理风险。
  - 页面类任务缺少设计确认 Gate 会影响任何采用 SDD 实现可视化界面的项目。
- 证据成熟度：L2

## 4. 修改清单

| 类型 | 路径 | 动作 | 状态 |
| --- | --- | --- | --- |
| skill | `skills/fons4ai-sdd-change/SKILL.md` | 修改：增加文档元数据同步规则 + UI 变更设计 Gate | done |
| skill | `skills/fons4ai-sdd-implement/SKILL.md` | 修改：增加 UI 设计确认 Gate | done |
| skill | `skills/fons4ai-sdd-tasks/SKILL.md` | 修改：增加页面类任务 UI 设计确认任务生成规则 | done |
| template | `skills/fons4ai-sdd-requirements/assets/templates/spec-template.md` | 修改：增加更新时间维护规则 | done |
| template | `skills/fons4ai-sdd-design/assets/templates/technical-design-template.md` | 修改：增加更新时间维护规则 | done |
| template | `skills/fons4ai-sdd-tasks/assets/templates/tasks-template.md` | 修改：增加页面/交互型交付物设计确认小节 | done |
| template | `skills/fons4ai-sdd-implement/assets/templates/implementation-report-template.md` | 修改：增加 UI 设计确认状态记录项 | done |
| validator | `skills/fons4ai-sdd-tasks/scripts/validate_sdd_artifacts.py` | 修改：增加更新时间一致性 + UI Gate 关键词检查 | done |

## 5. 验证记录

| 验证命令 | 结果 | 说明 |
| --- | --- | --- |
| `python scripts/validate_all.py` | 通过（skill contracts / loop phase 1 / implementation report template 等均通过；validate_feedback_harness.py 预存语法错误与本次改动无关） | 仓库级校验通过 |
| `python -c "import py_compile; ..."` | 通过 | validate_sdd_artifacts.py 语法正确 |

## 6. 全局同步

- 是否涉及全局 skills：否
- 同步路径：不适用
- 同步文件：无
- 哈希比对：不适用

## 7. 关闭结论

- 当前状态：Verified
- 是否关闭：否
- 剩余风险：
  - 跨项目重复性待观察（仅基于一个试点项目反馈）。
  - UI 设计 Gate 的具体输出格式（页面信息架构、布局方案、交互流）尚未在模板中标准化，后续可能需要细化。
- 待观察项：
  - 后续其他试点项目中是否重复出现"正式文档更新时间未同步"。
  - 后续其他页面类 SDD 实现中是否重复出现"未确认 UI 设计即直接编码"。