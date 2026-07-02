---
name: fons4ai-agent-env-readiness
description: "Fons4AI 按需 Agent 环境准备度与验证可靠性增强技能。用于项目刚接入 Agent 开发、新开发者接入、任务依赖 MySQL/Redis/RocketMQ/Nacos/配置中心/日志/测试环境等外部状态验证、或用户希望评估 MCP/CLI/只读账号/本地替代方案是否能提升 Agent 输入输出可靠性时。该技能不是 SDD 标准工作流步骤，不作为开发准入门槛；仅用于识别验证能力边界、生成环境准备清单、建议可选 MCP 或替代工具，并规范交付时的验证证据与未验证声明。"
---

# Fons4AI Agent Env Readiness

## Contract

### Inputs

- Required: 用户希望评估或增强 Agent 开发可靠性的项目、模块、任务类型、外部依赖或当前环境问题描述。
- Optional: 项目配置、启动方式、依赖清单、已有 MCP 配置、数据库/缓存/MQ/配置中心/日志/测试环境访问方式、团队权限边界、用户已确认的安全限制。
- Forbidden assumptions: 不得编造已配置 MCP、账号、连接串、内网地址、topic、namespace、表名、key 规则或配置项；不得把个人本机工具写成团队项目事实。

### Preconditions

- Entry gates: 用户明确指定本技能、询问 Agent 环境/MCP/外部依赖验证能力，或当前任务明显依赖外部状态才能验证。
- Required source artifacts: 先读取项目规则、README、配置文件、构建脚本、测试配置、docker compose、启动脚本、环境示例文件，再判断需要哪些外部组件验证能力。
- Safety boundary: 默认只评估和建议，不主动连接生产环境，不生成敏感连接信息，不要求用户安装所有 MCP。

### Outputs

- May create or update: `.specify/agent-readiness/<yyyymmdd>/<项目或模块名>-Agent环境准备度报告.md`，或用户指定路径下的准备度清单。
- May recommend: MCP、CLI、SDK、测试容器、本地 mock、只读账号、日志查询、手工验证步骤。
- Must not create or update: SDD 需求、技术设计、任务规划、业务代码、生产配置、密钥、账号密码、真实连接串。

### Exit Criteria

- Success: 已识别外部依赖与验证场景，给出准备度等级、可用/缺失能力、建议补充项、降级策略和交付证据要求。
- Blocked: 缺少项目上下文、无法判断外部依赖、用户未确认敏感环境边界，或必须访问受限系统才能继续评估。
- Failure report: 输出已检查范围、缺失事实、无法确认的组件、继续推进所需的用户确认或环境材料。

### Handoff

- Next skill: 如用户要沉淀项目规则，可建议显式使用 `fons4ai-generate-project-rules`；如要进入需求、设计或实现，按用户指定再进入 SDD 或实现类技能。
- Required handoff fields: 准备度等级、已验证能力、缺失能力、建议工具、风险边界、未验证项、报告路径。
- Stop condition: 完成准备度评估或报告后停止，不自动进入 SDD、不自动安装 MCP、不自动修改项目规则。

## 定位

本技能是 Agent 可靠性增强工作流，不是 SDD 标准步骤，也不是开发准入标准。它只回答一个问题：

> 当前项目是否具备足够的外部环境访问能力，让 Agent 能更可靠地验证输入、判断和输出？

MCP 是优先推荐的工具形态之一，但不是唯一方案。没有 MCP 时，可以使用 CLI、测试容器、本地 mock、只读账号、日志平台、项目脚本或手工验证步骤；都不可用时，必须明确说明验证能力边界。

## 准备度等级

- L0 静态分析：只能阅读代码、配置和文档，无法运行或观察外部状态。
- L1 本地验证：能运行单元测试、构建、静态检查或本地最小启动。
- L2 只读观察：能只读查询数据库、缓存、配置中心、日志、MQ 元数据或消费状态。
- L3 安全联调：能在开发/测试环境执行接口、消费消息、改写测试数据并验证闭环。
- L4 证据自动化：能自动采集命令、查询、日志、测试、消息轨迹等证据并附到交付结果。

等级只描述当前验证能力，不评价开发者能力，也不阻塞普通开发。

## 工作流

1. 确认触发目标。
   - 区分“项目接入准备”“新开发者接入”“某个任务验证能力不足”“交付证据规范”四类场景。
   - 如果用户只是在普通开发中顺手提到 Redis/MySQL/MQ，不要扩大成强制环境治理。

2. 读取项目上下文。
   - 优先读取 `AGENTS.md`、README、配置目录、构建脚本、测试配置、docker compose、启动脚本、环境示例文件。
   - 搜索 MySQL、Redis、RocketMQ、Nacos、Kafka、Elasticsearch、OSS、RPC、日志、配置中心、定时任务等关键词。
   - 只读取与环境能力判断相关的文件，避免全量扫描业务代码。

3. 建立外部依赖与验证场景矩阵。
   - 组件：例如 MySQL、Redis、RocketMQ、Nacos、日志、测试环境。
   - 验证用途：数据状态、缓存状态、配置生效、消息投递/消费、接口闭环、异常定位。
   - 访问方式：MCP、CLI、SDK、项目脚本、测试容器、本地 mock、手工入口。
   - 权限边界：只读、测试环境读写、禁止生产写入、敏感字段脱敏。
   - 当前状态：可用、缺失、待用户确认、不适用。

4. 评估准备度等级。
   - 根据当前可用能力给出 L0-L4。
   - 对每个缺失能力说明影响，不把缺失 MCP 夸大成开发阻塞。
   - 当任务强依赖外部状态时，说明“结论可靠性受限”的具体原因。

5. 生成建议。
   - 优先建议最小可行增强项，例如只读 MySQL 查询、Redis key 只读检查、Nacos 配置只读查看、MQ topic/consumer 状态查询。
   - 对高风险组件给出安全边界：默认测试环境、只读优先、禁止生产写入、敏感信息不入文档。
   - 推荐 MCP 时必须说明其验证价值和替代方案，不得写成强制安装。
   - 组件能力细节可读取 `references/component-capability-map.md`。

6. 输出准备度报告。
   - 使用 `assets/templates/readiness-report-template.md`。
   - 默认路径：`.specify/agent-readiness/<yyyymmdd>/<项目或模块名>-Agent环境准备度报告.md`。
   - 如果只是轻量咨询，可以只在对话中输出清单，不写文件。

7. 校验报告。
   - Python 可用时运行 `scripts/validate_readiness_report.py --report <report-path>`。
   - 校验失败时补齐缺失章节再结束。

## 报告内容要求

报告必须包含：

- 评估范围。
- 当前准备度等级。
- 外部依赖与验证场景矩阵。
- 已具备能力。
- 缺失能力与影响。
- MCP 与替代方案建议。
- 安全与权限边界。
- Agent 交付证据要求。
- 未验证项声明。
- 后续行动。

## 输出规则

- 明确说明本技能不是 SDD 必经步骤。
- 明确说明缺少 MCP 不等于不能开发，只代表部分验证能力缺失。
- 不输出真实密钥、连接串、账号密码、内网地址或敏感查询结果。
- 不把“建议补充 MCP”写成“必须安装 MCP”。
- 不把个人本机工具状态写成团队标准。
- 不自动修改 `AGENTS.md` 或 `.specify/rules`；用户要求沉淀规则时，建议转入 `fons4ai-generate-project-rules`。
