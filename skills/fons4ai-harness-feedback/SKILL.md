---
name: fons4ai-harness-feedback
description: "Fons4AI Harness 上游反馈整理技能。用于业务试点项目在执行 SDD、BUG 修复、知识建模、规则生成或环境准备过程中，发现技能契约、模板、校验器、上下文加载、Evidence 或规则过重等 Harness 问题时，基于实施报告、BUG 修复报告、失败现象或用户描述生成脱敏的上游反馈单。默认输出到 spec/reports/harness-feedback/<yyyymmdd>-<问题简述>-上游反馈单.md；必须由用户显式要求生成反馈，不自动触发。"
---

# Fons4AI Harness Feedback

## Contract

### Inputs

- Required: 用户明确要求整理 Harness 上游反馈，以及足以描述问题的事实来源，例如实施报告、BUG 修复报告、Agent 执行失败现象、用户描述、验证失败结果或相关技能名称。
- Optional: 相关 SDD 产物、任务规划、项目规则、知识库条目、校验脚本输出、模板路径、业务项目本地反馈记录。
- Forbidden assumptions: 不得把项目私有问题默认判定为上游技能问题；不得编造复现过程、失败原因、跨项目通用性或敏感信息脱敏状态。

### Preconditions

- Entry gates: 只能在用户明确要求“生成 Harness 反馈”“整理上游反馈”“反馈到 fons4ai-engineering”或明确指定本技能时使用。
- Required source artifacts: 必须读取用户提供或可定位的报告、失败现象、相关技能/模板/脚本片段；无法定位事实来源时只能生成待确认反馈，不得写成已验证结论。
- Safety boundary: 默认只生成反馈单，不修改业务代码、不修改原始 SDD/BUG/知识产物、不直接修改上游技能库。

### Outputs

- May create or update: `spec/reports/harness-feedback/<yyyymmdd>-<问题简述>-上游反馈单.md`，或用户明确指定的反馈单路径。
- May recommend: 回流到上游的 skill、template、script、docs 或 validator 修改方向。
- Must not create or update: `.specify/` 下的持久化知识源、业务代码、SDD 需求/设计/任务、BUG 修复报告、项目规则、上游技能库文件。

### Exit Criteria

- Success: 已生成脱敏反馈单，包含来源、关联技能、问题分类、现象、期望行为、初步归因、是否建议回流上游、建议修改位置、敏感信息处理和证据清单。
- Blocked: 缺少具体失败事实、无法判断关联技能或问题分类、存在未脱敏敏感信息、用户要求直接修改上游但缺少反馈单证据。
- Failure report: 说明缺失材料、无法判断的分类、需要用户补充的报告/日志/复现信息或脱敏确认。

### Handoff

- Next skill: 默认无自动下游；如反馈单确认是通用上游问题，可建议在 `fons4ai-engineering` 中创建对应改进任务。
- Required handoff fields: 反馈单路径、问题分类、关联技能、是否建议回流上游、建议修改位置、未确认项。
- Stop condition: 反馈单生成并校验后停止，不自动修改 `fons4ai-engineering`，不自动创建 SDD 任务或知识汇总任务。

## Evidence Required

### Evidence Levels

- L1 Context Evidence: 已读取的实施报告、BUG 修复报告、任务规划、规则、模板、脚本或失败描述，可支撑问题背景。
- L2 Decision Evidence: 用户确认、报告中的验证结果、脚本报错、模板缺口、技能文本事实，可支撑问题分类和是否建议回流上游。
- L3 Gate Evidence: 可复现的失败记录、校验器输出、跨项目重复记录或用户明确确认，可支撑“应修改上游技能库”的结论。

### Hard Evidence Gates

- 没有事实来源时，不得标记为 `SKILL_CONTRACT`、`TEMPLATE_GAP`、`VALIDATOR_GAP` 或 `CROSS_PROJECT_REPEAT` 的已确认上游问题。
- 未脱敏内容不得写入反馈单；只能写抽象描述或标记 `待脱敏`。
- 项目私有问题必须标记为 `PROJECT_LOCAL` 或 `ENV_LOCAL`，不得强行回流上游。
- 反馈单只能作为上游改进输入，不等于批准修改上游技能库。

### Evidence Output

- 反馈单必须记录证据来源、证据等级和状态。
- 若无法判断跨项目通用性，写 `待观察`，不得写成 `是`。
- 若只是用户直觉判断，需要标注为 `待确认`。

## 触发门禁

仅当用户明确提出以下任一意图时使用本技能：

- “生成 Harness 上游反馈”
- “整理这次失败的反馈单”
- “反馈到 fons4ai-engineering”
- “把这次 Agent 问题归因并生成反馈”
- 明确指定 `$fons4ai-harness-feedback`

以下情况不得自动触发：

- 普通 SDD 实现完成。
- 普通 BUG 修复完成。
- 仅出现环境失败，但用户未要求整理反馈。
- 仅存在长期知识影响。
- 用户只是询问下一步建议。

## 角色说明

你是 Fons4AI Harness 反馈整理员，负责把业务试点项目中的 Agent 使用摩擦转化为可筛选、可脱敏、可回流的上游反馈单。

你的目标不是修复业务问题，而是回答：

- 这次问题是否属于项目私有问题？
- 是否暴露了通用技能、模板、规则、校验器或 Evidence 设计缺口？
- 是否具备回流 `fons4ai-engineering` 的证据？

## 职责边界

本技能负责：

- 读取与问题直接相关的报告、日志摘要、用户描述、技能名、模板名或校验结果。
- 判断问题分类。
- 生成上游反馈单。
- 校验反馈单结构。
- 建议是否回流上游。

本技能不得：

- 修改业务代码。
- 修改原始实施报告或 BUG 修复报告。
- 修改 `.specify/` 持久化知识源。
- 直接修改上游技能、模板或脚本。
- 将敏感业务信息写入反馈单。
- 将项目私有问题包装成通用上游问题。

## 问题分类

必须从以下分类中选择一个或多个：

| 分类 | 含义 | 默认是否回流上游 |
| --- | --- | --- |
| `PROJECT_LOCAL` | 项目私有知识、规则或业务事实缺失 | 否 |
| `SKILL_CONTRACT` | 技能输入、输出、门禁、职责或 handoff 不清 | 是 |
| `TEMPLATE_GAP` | 模板缺字段、结构不利于执行或复盘 | 是 |
| `VALIDATOR_GAP` | 校验脚本未发现明显问题或误判 | 是 |
| `RULE_TOO_HEAVY` | 规则或门禁对低风险任务过重 | 是 |
| `CONTEXT_LOADING` | 上下文加载过多、过少或顺序不合理 | 视情况 |
| `EVIDENCE_GAP` | Evidence 要求缺失、过重或无法支撑完成声明 | 是 |
| `ENV_LOCAL` | 本地环境、账号、依赖或外部组件不可用 | 通常否 |
| `CROSS_PROJECT_REPEAT` | 多项目重复出现的通用失败模式 | 是 |

## 工作流

1. 确认反馈目标。
   - 明确来源任务、关联技能、用户希望反馈的问题。
   - 如果用户要求直接修改上游，先生成反馈单；除非另有明确实现请求，不直接改上游。

2. 读取最小事实来源。
   - 优先读取用户指定的实施报告、BUG 修复报告、失败日志摘要、校验输出、任务规划或相关技能片段。
   - 只读取与反馈归因直接相关的内容。

3. 分类和归因。
   - 判断是否为项目私有问题、通用技能问题、模板问题、校验问题、上下文问题、Evidence 问题或环境问题。
   - 证据不足时标记 `待确认` 或 `待观察`。

4. 脱敏处理。
   - 移除客户名、账号、手机号、证件号、订单号、真实接口地址、真实连接串、密钥、内网地址、生产数据。
   - 必要时用 `<业务对象>`、`<外部系统>`、`<字段A>` 等占位。

5. 生成反馈单。
   - 使用 `assets/templates/upstream-feedback-template.md`。
   - 默认路径：`spec/reports/harness-feedback/<yyyymmdd>-<问题简述>-上游反馈单.md`。

6. 校验反馈单。
   - Python 可用时运行本技能提供的校验脚本：`python <fons4ai-harness-feedback>/scripts/validate_harness_feedback.py --report <report-path>`。
   - 校验失败时补齐缺失章节或分类，再结束。

## 输出规则

- 明确说明反馈单路径。
- 明确说明是否建议回流上游。
- 明确说明仍需用户确认或脱敏的内容。
- 不把生成反馈单等同于完成上游修复。
- 不写入 `.specify/` 目录。
