#!/usr/bin/env python3
"""Validate minimal Fons4AI SDD artifact consistency."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


AC_RE = re.compile(r"\bAC-\d{3}\b")
REQ_RE = re.compile(r"\bREQ-\d{3}\b")
TASK_RE = re.compile(r"^- \[[ xX]\] (T\d{3})(?:\s|$)", re.MULTILINE)
TASK_PACK_RE = re.compile(r"\bTP-\d{3}\b")
TASK_PACK_HEADER_RE = re.compile(r"^>\s*TaskPack[：:]\s*`?(TP-\d{3})`?", re.MULTILINE)
TASK_PACK_INDEX_ROW_RE = re.compile(r"^\|\s*(TP-\d{3})\s*\|", re.MULTILINE)
PACK_STATUS_RE = re.compile(r"^>\s*PackStatus[：:]\s*([a-z-]+)", re.MULTILINE | re.IGNORECASE)
APPROVAL_STATUS_RE = re.compile(r"^>\s*ApprovalStatus[：:]\s*([a-z-]+)", re.MULTILINE | re.IGNORECASE)
PACK_DEPENDS_RE = re.compile(r"^>\s*DependsOn[：:]\s*([^\n\r]+)", re.MULTILINE | re.IGNORECASE)
ACTIVE_PACK_RE = re.compile(r"当前活动任务包\s*[：:]\s*(?:`?(TP-\d{3})`?|无)", re.IGNORECASE)
SQL_PATH_RE = re.compile(r"\.specify/sql/[A-Za-z0-9_./-]+\.sql")
EXECUTABLE_DDL_PATH_RE = re.compile(
    r"\.?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.sql",
    re.IGNORECASE,
)
S2_RE = re.compile(r"(SDD\s*Level|SDD\s*等级)\s*[:：]\s*`?S2`?", re.IGNORECASE)
RUNTIME_SERVICE_DECLARATION_RE = re.compile(
    r"(?:独立可运行服务|服务运行态门禁)\s*[：:]\s*(?:是|适用|yes|true)",
    re.IGNORECASE,
)
RUNTIME_SERVICE_NEGATIVE_RE = re.compile(
    r"(?:独立可运行服务|服务运行态门禁)\s*[：:]\s*(?:否|不适用|no|false)",
    re.IGNORECASE,
)
LEGACY_RUNTIME_SERVICE_ENTRY_RE = re.compile(
    r"启动入口|启动命令|入口文件|入口函数|消息生产|消息消费|后台\s*worker|worker|"
    r"main\.go|func\s+main|FastAPI|Flask|Django|uvicorn|gunicorn|express|koa|nest|"
    r"SpringBootApplication|REST\s*Controller|"
    r"@RestController|@DubboReference|@FeignClient|@RabbitListener|@KafkaListener|"
    r"spring\.application\.name|注册中心|服务注册|服务发现|Actuator|健康检查",
    re.IGNORECASE,
)


def requires_runtime_service_closure(design_text: str) -> bool:
    """Require runtime closure only for declared or unambiguously runnable services."""

    if RUNTIME_SERVICE_NEGATIVE_RE.search(design_text):
        return False
    return bool(
        RUNTIME_SERVICE_DECLARATION_RE.search(design_text)
        or LEGACY_RUNTIME_SERVICE_ENTRY_RE.search(design_text)
    )
RUNTIME_SERVICE_TASK_RE = re.compile(
    r"启动入口|启动验证|服务启动|运行配置|服务注册|注册发现|服务发现|服务路由|健康检查|健康探测|就绪检查|"
    r"核心\s*(API|RPC|gRPC)|HTTP\s*API|REST\s*API|RPC\s*链路|gRPC\s*链路|消息链路|隔离环境|只读验证|暂缓确认",
    re.IGNORECASE,
)
RUNTIME_INIT_DML_RE = re.compile(
    r"运行初始化\s*DML|初始化\s*DML|Seed\s*数据|种子数据|初始化数据|默认角色|默认权限|"
    r"默认配置|系统账号|系统租户|服务账号|白名单|字典",
    re.IGNORECASE,
)
RUNTIME_INIT_DML_TASK_RE = re.compile(
    r"运行初始化\s*DML|初始化\s*DML|Seed\s*脚本|Seed\s*数据|种子数据|初始化数据脚本|"
    r"执行状态|只读复核|复核\s*SQL|回滚说明|占位变量|用户/DBA|DBA|暂缓",
    re.IGNORECASE,
)
RUNTIME_INIT_DML_HEADINGS = (
    "### 4.8 运行初始化 DML / Seed 数据",
    "### 5.4 运行初始化 DML / Seed 数据",
    "### 5.4 运行初始化 DML / Seed",
)

APPROVAL_GATE_HEADINGS = ("## 2. 实现确认门禁", "## 12. 实现确认门禁", "## 实现确认门禁", "## Implementation Approval Gate")
DOCUMENT_STATUS_RE = re.compile(r"(文档状态|Document Status)\s*[:：]\s*([^\n\r]+)", re.IGNORECASE)
BLOCKING_ARTIFACT_RE = re.compile(r"草案-待确认|草案-含待确认|阻塞|blocking|draft", re.IGNORECASE)
SPEC_REQUIRED_HEADING_GROUPS = (
    ("一句话说明", ("## 一句话说明",)),
    ("需求就绪摘要", ("## 需求就绪摘要", "## 需求澄清摘要")),
    ("背景与目标", ("## 背景与目标",)),
    ("需求范围", ("## 需求范围",)),
    ("角色与场景", ("## 角色与场景",)),
    ("需求列表", ("## 需求列表",)),
    ("业务规则", ("## 业务规则",)),
    ("业务流程", ("## 业务流程",)),
    ("业务数据口径", ("## 业务数据口径",)),
    ("影响说明", ("## 影响说明",)),
    ("验收标准", ("## 验收标准",)),
    ("质量要求", ("## 质量要求",)),
    ("风险与待确认", ("## 风险与待确认",)),
    ("版本修订记录", ("## 版本修订记录",)),
)
PLAN_REQUIRED_HEADING_GROUPS = (
    ("设计概要", ("## 1. 设计概要", "## 设计概要")),
    ("架构与调用链路", ("## 2. 架构与调用链路", "## 架构与调用链路")),
    ("API / RPC / 消息契约设计", ("## 3. API / RPC / 消息契约设计", "## API / RPC / 消息契约设计")),
    ("数据模型与 DDL 影响", ("## 4. 数据模型与 DDL 影响", "## 数据模型与 DDL 影响")),
    ("核心逻辑设计", ("## 5. 核心逻辑设计", "## 核心逻辑设计")),
    ("领域建模与业务规则落地", ("## 6. 领域建模与业务规则落地", "## 领域建模与业务规则落地")),
    ("状态流转设计", ("## 7. 状态流转设计", "## 状态流转设计")),
    ("异常、安全、事务与性能", ("## 8. 异常、安全、事务与性能", "## 异常、安全、事务与性能")),
    ("技术决策", ("## 9. 技术决策", "## 技术决策")),
    ("验证策略、AC 映射与风险", ("## 10. 验证策略、AC 映射与风险", "## 验证策略、AC 映射与风险")),
)
DESIGN_V2_REQUIRED_HEADING_GROUPS = (
    ("设计摘要与关键决策", ("## 1. 设计摘要与关键决策",)),
    ("系统边界、模块与调用链", ("## 2. 系统边界、模块与调用链",)),
    ("接口、消息与外部契约", ("## 3. 接口、消息与外部契约",)),
    ("核心业务、领域规则与状态流转", ("## 4. 核心业务、领域规则与状态流转",)),
    ("数据结构、迁移与初始化", ("## 5. 数据结构、迁移与初始化",)),
    ("横切质量设计", ("## 6. 横切质量设计",)),
    ("AC、验证、风险与回滚", ("## 7. AC、验证、风险与回滚",)),
)
KNOWLEDGE_IMPACT_HEADINGS = ("### 10.4 知识同步影响", "### 7.2 知识同步影响", "## 知识同步清单", "## 知识同步影响", "## Knowledge Impact")
RISK_ROLLBACK_HEADINGS = ("### 10.3 风险与回滚", "## 10. 验证策略、AC 映射与风险", "## 7. AC、验证、风险与回滚", "## 风险与回滚", "## Risk and Rollback")
S2_QUALITY_GATE_HEADINGS = ("## S2 质量门禁", "## S2 Quality Gates")
EVIDENCE_MATRIX_RE = re.compile(r"Evidence\s+Matrix|证据矩阵|运行态\s*Evidence|服务级\s*Evidence", re.IGNORECASE)
DATA_IMPACT_HEADINGS = ("### 数据影响判断", "## 数据影响判断", "### Data Impact")
FIELD_MAPPING_HEADINGS = ("### 4.2 字段映射契约", "### 5.2 字段映射与数据流", "### 字段映射契约", "## 字段映射契约", "### Field Mapping Contract")
DATA_FLOW_HEADINGS = ("### 4.3 数据流设计", "### 5.2 字段映射与数据流", "### 数据流设计", "## 数据流设计", "### Data Flow Design")
DATA_SECURITY_HEADINGS = ("### 4.4 数据安全与合规设计", "### 5.5 数据安全与生命周期", "### 数据安全与合规设计", "## 数据安全与合规设计", "### Data Security")
DATA_STRUCTURE_DETAIL_HEADINGS = ("### 4.5 结构变更详设", "### 5.3 结构变更详设", "### 结构变更详设", "## 结构变更详设", "### Data Structure Detail")
EVIDENCE_LIST_HEADINGS = ("## 11. 证据清单", "## 附录 A. 证据清单", "## 证据清单", "## Evidence List")
CHANGE_REQUIRED_HEADING_GROUPS = (
    ("变更摘要", ("## 1. 变更摘要", "## 变更摘要")),
    ("影响范围", ("## 4. 影响范围", "## 影响范围", "## 影响分析", "## Impact Analysis")),
    ("需求与 AC 变化", ("## 5. 需求与 AC 变化", "## 需求与 AC 变化", "### 需求影响")),
    ("技术设计影响", ("## 6. 技术设计影响", "## 技术设计影响", "### 设计影响")),
    ("数据结构与 DDL 影响", ("## 7. 数据结构与 DDL 影响", "## 数据结构与 DDL 影响")),
    ("回归与回滚", ("## 8. 回归与回滚", "## 回归与回滚", "## Regression and Rollback")),
    ("长期知识影响", ("## 9. 长期知识影响", "## 长期知识影响", "### 知识同步清单", "### 知识同步影响", "### Knowledge Impact")),
    ("文档更新", ("## 10. 文档更新", "## 文档更新")),
    ("实现确认门禁", APPROVAL_GATE_HEADINGS),
    ("增量任务", ("## 11. 增量任务", "## 增量任务", "## Incremental Tasks")),
)

CHANGE_TYPE_RE = re.compile(r"(变更类型|Change Type)\s*[:：]\s*(微调|扩展|重构|数据结构变更|契约变更|纯文档修正|tweak|extension|refactor)", re.IGNORECASE)

DOMAIN_QUALITY_RE = re.compile(r"DDD|domain|领域|充血|贫血|业务规则|应用层", re.IGNORECASE)
KNOWLEDGE_OR_DDL_TASK_RE = re.compile(
    r"\.specify/|truth-source|Knowledge|knowledge|知识|DDL|SQL|数据文档|数据架构|配置与资源文档",
    re.IGNORECASE,
)
RISK_CONTROL_RE = re.compile(
    r"rollback|compatib|regression|permission|security|observability|migration|risk|checklist|"
    r"回滚|兼容|回归|权限|安全|观测|迁移|风险|检查|门禁",
    re.IGNORECASE,
)
DATA_RISK_RE = re.compile(
    r"字段映射|数据流|外部数据|入库|出库|同步|对账|报表|迁移|金额|日期|状态|流水号|客户标识|敏感数据|脱敏|加密|审计|保留期限|"
    r"field\s+mapping|data\s+flow|import|export|sync|reconciliation|report|migration|amount|date|status|serial|sensitive",
    re.IGNORECASE,
)
DATA_VERIFICATION_RE = re.compile(
    r"字段映射|数据口径|样例数据|目标数据|金额单位|日期格式|状态口径|流水号|客户标识|敏感数据|日志脱敏|数据安全|合规|"
    r"field\s+mapping|sample\s+data|target\s+data|data\s+security",
    re.IGNORECASE,
)

UI_KEYWORD_RE = re.compile(
    r"页面|前端|控制台|模板引擎|Freemarker|Vue|React|管理后台|可视化界面|交互型交付物",
    re.IGNORECASE,
)

UI_DESIGN_EVIDENCE_RE = re.compile(
    r"UI 设计确认|UI 设计方案|页面信息架构|布局方案|关键交互流|视觉验收|用户跳过.*设计确认|跳过 UI 设计|页面/交互型交付物设计确认",
    re.IGNORECASE,
)
UI_DELIVERY_NEGATIVE_RE = re.compile(r"页面/交互型交付物\s*[：:]\s*(?:否|不适用|no|false)", re.IGNORECASE)
UI_DELIVERY_POSITIVE_RE = re.compile(r"页面/交互型交付物\s*[：:]\s*(?:是|适用|yes|true)", re.IGNORECASE)

DOC_UPDATE_DATE_RE = re.compile(r"更新日期\s*[:：]\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
DESIGN_APPROVAL_RE = re.compile(r"设计确认状态\s*[:：]\s*`?(pending|approved|not-required)`?", re.IGNORECASE)
VALID_PACK_STATUS = {"draft", "ready", "approved", "in-progress", "done", "deferred", "superseded", "archived"}
VALID_PACK_APPROVAL = {"pending", "approved", "rejected", "not-required"}
TEST_DECISION_MARKER = "TestDecisionVersion: 1"
TEST_DECISION_FIELDS = {
    "BehaviorChange:": {"none", "changed", "new"},
    "ExistingCoverage:": {"covered", "partial", "missing", "not-applicable"},
    "TestAction:": {"none", "reuse", "update", "add"},
    "TestLevel:": {"none", "unit", "contract", "integration", "e2e", "manual"},
    "RegressionScope:": {"none", "focused", "affected", "module", "full"},
}
FULL_REGRESSION_TRIGGER_RE = re.compile(
    r"发布|合并|公共契约|共享基础|依赖|构建配置|数据库结构|安全|权限|影响范围|用户|CI|"
    r"release|merge|contract|shared|dependency|build|database|security|permission|unknown|user",
    re.IGNORECASE,
)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except UnicodeDecodeError:
        return path.read_text()


def task_field(block: str, label: str) -> str | None:
    match = re.search(rf"^\s*-\s*{re.escape(label)}\s*([^|\r\n]+)", block, re.MULTILINE)
    return match.group(1).strip().lower() if match else None


def validate_test_decision(task_id: str, block: str, source: str) -> list[str]:
    errors: list[str] = []
    values: dict[str, str] = {}
    for label, allowed in TEST_DECISION_FIELDS.items():
        value = task_field(block, label)
        if value is None:
            errors.append(f"{task_id} in {source} is missing '{label}'")
            continue
        values[label] = value
        if value not in allowed:
            errors.append(f"{task_id} in {source} has invalid {label} value '{value}'")
    for label in ("AffectedTests:", "TestReason:"):
        if task_field(block, label) is None:
            errors.append(f"{task_id} in {source} is missing '{label}'")

    behavior = values.get("BehaviorChange:")
    coverage = values.get("ExistingCoverage:")
    action = values.get("TestAction:")
    level = values.get("TestLevel:")
    scope = values.get("RegressionScope:")
    reason = task_field(block, "TestReason:") or ""
    if behavior == "none" and action in {"update", "add"}:
        errors.append(f"{task_id} in {source} changes tests even though BehaviorChange is none")
    if coverage == "covered" and action in {"update", "add"}:
        errors.append(f"{task_id} in {source} changes tests even though ExistingCoverage is covered")
    if action in {"update", "add"} and level == "none":
        errors.append(f"{task_id} in {source} has TestAction {action} but TestLevel is none")
    if scope == "full" and not FULL_REGRESSION_TRIGGER_RE.search(reason):
        errors.append(f"{task_id} in {source} uses full regression without an explicit trigger in TestReason")
    return errors


def requirement_artifact_paths(feature_dir: Path) -> list[Path]:
    return sorted(feature_dir.glob("*-需求说明书.md"))


def technical_design_artifact_paths(feature_dir: Path) -> list[Path]:
    return sorted(feature_dir.glob("*-技术设计说明书.md"))


def task_planning_artifact_paths(feature_dir: Path) -> list[Path]:
    return sorted(feature_dir.glob("*-任务规划.md"))


def task_index_artifact_paths(feature_dir: Path) -> list[Path]:
    return sorted(feature_dir.glob("*-任务索引.md"))


def task_pack_artifact_paths(feature_dir: Path) -> list[Path]:
    tasks_dir = feature_dir / "tasks"
    return sorted(tasks_dir.glob("TP-*.md")) if tasks_dir.is_dir() else []


def task_blocks(tasks_text: str) -> list[tuple[str, str]]:
    matches = list(TASK_RE.finditer(tasks_text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(tasks_text)
        blocks.append((match.group(1), tasks_text[start:end]))
    return blocks


def validate_task_pack_mode(index_path: Path, pack_paths: list[Path]) -> list[str]:
    errors: list[str] = []
    index_text = read(index_path)
    pack_graph: dict[str, set[str]] = {}
    seen_pack_ids: set[str] = set()
    indexed_pack_ids = set(TASK_PACK_INDEX_ROW_RE.findall(index_text))

    active_match = ACTIVE_PACK_RE.search(index_text)
    if not active_match:
        errors.append(f"{index_path.name} is missing '当前活动任务包' field")
    active_pack = active_match.group(1) if active_match else None

    for pack_path in pack_paths:
        text = read(pack_path)
        header = TASK_PACK_HEADER_RE.search(text)
        if not header:
            errors.append(f"{pack_path.name} is missing TaskPack metadata")
            continue
        pack_id = header.group(1)
        if pack_id in seen_pack_ids:
            errors.append(f"Duplicate Task Pack ID: {pack_id}")
        seen_pack_ids.add(pack_id)
        if pack_id not in indexed_pack_ids:
            errors.append(f"{pack_id} exists in {pack_path.name} but is not registered in {index_path.name}")
        if not pack_path.stem.startswith(pack_id):
            errors.append(f"{pack_path.name} filename must start with its Task Pack ID {pack_id}")

        status_match = PACK_STATUS_RE.search(text)
        approval_match = APPROVAL_STATUS_RE.search(text)
        if not status_match:
            errors.append(f"{pack_path.name} is missing PackStatus metadata")
            status = ""
        else:
            status = status_match.group(1).lower()
            if status not in VALID_PACK_STATUS:
                errors.append(f"{pack_path.name} has invalid PackStatus: {status}")
        if not approval_match:
            errors.append(f"{pack_path.name} is missing ApprovalStatus metadata")
            approval = ""
        else:
            approval = approval_match.group(1).lower()
            if approval not in VALID_PACK_APPROVAL:
                errors.append(f"{pack_path.name} has invalid ApprovalStatus: {approval}")
        if status in {"approved", "in-progress"} and approval not in {"approved", "not-required"}:
            errors.append(f"{pack_path.name} is executable but ApprovalStatus is not approved/not-required")

        depends_match = PACK_DEPENDS_RE.search(text)
        dependencies = set(TASK_PACK_RE.findall(depends_match.group(1))) if depends_match else set()
        if pack_id in dependencies:
            errors.append(f"{pack_path.name} cannot depend on itself ({pack_id})")
        pack_graph[pack_id] = dependencies

    for indexed_pack_id in sorted(indexed_pack_ids - seen_pack_ids):
        errors.append(f"{index_path.name} registers {indexed_pack_id} but no matching task pack file exists")

    for pack_id, dependencies in pack_graph.items():
        for dependency in sorted(dependencies - seen_pack_ids):
            errors.append(f"{pack_id} depends on unknown Task Pack {dependency}")

    if active_pack and active_pack not in seen_pack_ids:
        errors.append(f"{index_path.name} current active Task Pack {active_pack} has no task pack file")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(pack_id: str) -> None:
        if pack_id in visited:
            return
        if pack_id in visiting:
            errors.append(f"Task Pack dependency cycle detected at {pack_id}")
            return
        visiting.add(pack_id)
        for dependency in pack_graph.get(pack_id, set()):
            if dependency in pack_graph:
                visit(dependency)
        visiting.remove(pack_id)
        visited.add(pack_id)

    for pack_id in pack_graph:
        visit(pack_id)

    return errors


def heading_match(text: str, heading: str) -> re.Match[str] | None:
    return re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE)


def first_heading(text: str, headings: tuple[str, ...]) -> str | None:
    for heading in headings:
        if heading_match(text, heading):
            return heading
    return None


def has_any_heading(text: str, headings: tuple[str, ...]) -> bool:
    return first_heading(text, headings) is not None


def section_content(text: str, headings: tuple[str, ...]) -> str:
    heading = first_heading(text, headings)
    if not heading:
        return ""
    match = heading_match(text, heading)
    if not match:
        return ""
    content_start = match.end()
    next_heading = re.search(r"^##\s+", text[content_start:], re.MULTILINE)
    if not next_heading:
        return text[content_start:]
    return text[content_start : content_start + next_heading.start()]


def has_section_content(text: str, headings: tuple[str, ...]) -> bool:
    content = section_content(text, headings)
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if set(stripped) <= {"-", "|", ":", "：", " "}:
            continue
        return True
    return False


def requires_runtime_init_dml(text: str) -> bool:
    section = section_content(text, RUNTIME_INIT_DML_HEADINGS)
    if section:
        if re.search(r"是否涉及(?:运行初始化数据)?\s*[：:]\s*(?:否|不适用|no|false)", section, re.IGNORECASE):
            return False
        if re.search(r"是否涉及(?:运行初始化数据)?\s*[：:]\s*(?:是|适用|yes|true)", section, re.IGNORECASE):
            return True
        return bool(RUNTIME_INIT_DML_RE.search(section) and not re.search(r"不适用|none", section, re.IGNORECASE))
    return bool(RUNTIME_INIT_DML_RE.search(text))


def requires_ui_design(design_text: str, planning_text: str) -> bool:
    if UI_DELIVERY_POSITIVE_RE.search(design_text):
        return True
    if UI_DELIVERY_NEGATIVE_RE.search(design_text) and not UI_KEYWORD_RE.search(planning_text):
        return False
    return bool(UI_KEYWORD_RE.search(design_text) or UI_KEYWORD_RE.search(planning_text))


def validate_required_heading_groups(
    text: str,
    heading_groups: tuple[tuple[str, tuple[str, ...]], ...],
    artifact_name: str,
) -> list[str]:
    errors: list[str] = []
    for display_name, headings in heading_groups:
        if not has_any_heading(text, headings):
            errors.append(f"{artifact_name} is missing section '{display_name}'")
    return errors


def validate_req_ac_mapping(spec_text: str) -> list[str]:
    errors: list[str] = []
    req_ids = sorted(set(REQ_RE.findall(spec_text)))
    for req_id in req_ids:
        mapped = any(req_id in line and AC_RE.search(line) for line in spec_text.splitlines())
        if not mapped:
            errors.append(f"{req_id} has no AC mapping in requirement artifact")
    return errors


def validate_artifact_readiness(text: str, artifact_name: str) -> list[str]:
    errors: list[str] = []
    statuses = [match.group(2).strip() for match in DOCUMENT_STATUS_RE.finditer(text)]
    if any(BLOCKING_ARTIFACT_RE.search(status) for status in statuses):
        errors.append(f"{artifact_name} is a draft or has unresolved clarification and cannot enter downstream planning")
    return errors


def validate_quality_domain_check(task_id: str, block: str, context: str) -> list[str]:
    if KNOWLEDGE_OR_DDL_TASK_RE.search(block):
        return []
    if DOMAIN_QUALITY_RE.search(block):
        return []
    return [f"{task_id} in {context} Quality is missing DDD-lite/domain-modeling check"]


def plan_declares_sql_sync(plan_text: str) -> bool:
    return bool(
        re.search(r"SQL DDL update needed\s*:\s*yes", plan_text, re.IGNORECASE)
        or re.search(r"DDL sync required\s*:\s*yes", plan_text, re.IGNORECASE)
        or re.search(r"DDL file action\s*:\s*(add|update|rename)", plan_text, re.IGNORECASE)
        or re.search(r"是否需要\s*DDL\s*同步\s*[：:]\s*是", plan_text)
        or re.search(r"DDL\s*文件动作\s*[：:]\s*(新增|更新|重命名)", plan_text)
    )


def declares_data_structure_change(text: str) -> bool:
    return bool(
        plan_declares_sql_sync(text)
        or re.search(r"(是否涉及持久化结构变化|持久化结构变化|数据结构变更|DDL\s*影响)\s*[：:]\s*是", text, re.IGNORECASE)
        or re.search(r"SQL\s*DDL\s*(update needed|action|required)\s*:\s*(yes|add|update|rename)", text, re.IGNORECASE)
    )


def declares_existing_table_change_with_baseline(text: str) -> bool:
    return bool(
        re.search(r"Existing\s+table.*baseline\s+DDL\s*:\s*(yes|confirmed)", text, re.IGNORECASE)
        or re.search(r"存量表原始\s*DDL\s*[：:]\s*已存在", text)
        or re.search(r"是否为存量表结构变更\s*[：:]\s*是[，,]?\s*原始\s*DDL\s*已存在", text)
    )


def executable_ddl_paths(text: str) -> list[str]:
    return sorted(
        {
            path
            for path in EXECUTABLE_DDL_PATH_RE.findall(text)
            if not path.startswith(".specify/sql/")
        }
    )


def validate(feature_dir: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    requirement_files = requirement_artifact_paths(feature_dir)
    if not requirement_files:
        errors.append(f"Missing required artifact: {feature_dir / '<功能中文名>-需求说明书.md'}")
        spec = feature_dir / "<功能中文名>-需求说明书.md"
    elif len(requirement_files) > 1:
        errors.append(f"Multiple requirement artifacts found in {feature_dir}; keep exactly one *-需求说明书.md")
        spec = requirement_files[0]
    else:
        spec = requirement_files[0]
    design_files = technical_design_artifact_paths(feature_dir)
    if not design_files:
        errors.append(f"Missing required artifact: {feature_dir / '<功能中文名>-技术设计说明书.md'}")
        design = feature_dir / "<功能中文名>-技术设计说明书.md"
    elif len(design_files) > 1:
        errors.append(f"Multiple technical design artifacts found in {feature_dir}; keep exactly one *-技术设计说明书.md")
        design = design_files[0]
    else:
        design = design_files[0]
    task_files = task_planning_artifact_paths(feature_dir)
    task_index_files = task_index_artifact_paths(feature_dir)
    task_pack_files = task_pack_artifact_paths(feature_dir)
    planning_mode = ""
    planning_artifacts: list[Path] = []
    if task_files and task_index_files:
        errors.append(f"Both V1 task plan and V2 task index found in {feature_dir}; keep only one active planning mode")
    elif task_index_files:
        planning_mode = "task-pack"
        if len(task_index_files) > 1:
            errors.append(f"Multiple task indexes found in {feature_dir}; keep exactly one *-任务索引.md")
        if not task_pack_files:
            errors.append(f"V2 task index found but no task packs exist under {feature_dir / 'tasks'}")
        planning_artifacts = task_index_files[:1] + task_pack_files
    elif task_files:
        planning_mode = "single-file"
        if len(task_files) > 1:
            errors.append(f"Multiple task planning artifacts found in {feature_dir}; keep exactly one *-任务规划.md")
        planning_artifacts = task_files[:1]
    else:
        errors.append(
            f"Missing task planning artifact: expected {feature_dir / '<功能中文名>-任务规划.md'} "
            f"or {feature_dir / '<功能中文名>-任务索引.md'} with tasks/TP-*.md"
        )

    if errors:
        return errors, warnings

    spec_text = read(spec)
    design_text = read(design)
    planning_text_by_path = [(path, read(path)) for path in planning_artifacts]
    tasks_text = "\n".join(text for _, text in planning_text_by_path)
    planning_name = ", ".join(path.name for path in planning_artifacts)
    task_index = task_index_files[0] if task_index_files else None
    if planning_mode == "task-pack" and task_index:
        errors.extend(validate_task_pack_mode(task_index, task_pack_files))
    all_text = "\n".join((spec_text, design_text, tasks_text))

    ac_ids = sorted(set(AC_RE.findall(spec_text)))
    if not ac_ids:
        errors.append("requirement artifact contains no AC-### acceptance criteria IDs")

    errors.extend(validate_required_heading_groups(spec_text, SPEC_REQUIRED_HEADING_GROUPS, str(spec.name)))
    errors.extend(validate_artifact_readiness(spec_text, str(spec.name)))
    errors.extend(validate_req_ac_mapping(spec_text))
    design_heading_groups = (
        DESIGN_V2_REQUIRED_HEADING_GROUPS
        if has_any_heading(design_text, DESIGN_V2_REQUIRED_HEADING_GROUPS[0][1])
        else PLAN_REQUIRED_HEADING_GROUPS
    )
    errors.extend(validate_required_heading_groups(design_text, design_heading_groups, str(design.name)))
    design_approval = DESIGN_APPROVAL_RE.search(design_text)
    if design_approval and design_approval.group(1).lower() == "pending":
        errors.append(f"{design.name} design approval is pending and cannot enter task execution planning")
    if not has_any_heading(spec_text, DATA_IMPACT_HEADINGS):
        errors.append(f"{spec.name} is missing data impact check section")
    for display_name, headings in (
        ("字段映射契约", FIELD_MAPPING_HEADINGS),
        ("数据流设计", DATA_FLOW_HEADINGS),
        ("数据安全与合规设计", DATA_SECURITY_HEADINGS),
        ("结构变更详设", DATA_STRUCTURE_DETAIL_HEADINGS),
    ):
        if not has_any_heading(design_text, headings):
            errors.append(f"{design.name} is missing data design section '{display_name}'")

    for ac_id in ac_ids:
        if ac_id not in design_text:
            errors.append(f"{ac_id} is not referenced in {design.name}")
        if ac_id not in tasks_text:
            errors.append(f"{ac_id} is not referenced in task planning artifacts")

    plan_sql_files = sorted(set(SQL_PATH_RE.findall(design_text)))
    if plan_declares_sql_sync(design_text) and not plan_sql_files:
        errors.append(f"{design.name} declares DDL sync but names no .specify/sql/**/*.sql file")
    if declares_data_structure_change(design_text) and not has_any_heading(design_text, EVIDENCE_LIST_HEADINGS):
        errors.append(f"{design.name} declares data structure or DDL impact but has no evidence list")
    for sql_file in plan_sql_files:
        if sql_file not in tasks_text:
            errors.append(f"{sql_file} is referenced in {design.name} but not in task planning artifacts")

    if declares_existing_table_change_with_baseline(design_text):
        executable_ddl_files = executable_ddl_paths(design_text)
        if not executable_ddl_files:
            errors.append(f"{design.name} declares an existing-table change with baseline DDL but names no executable change DDL file")
        for ddl_file in executable_ddl_files:
            if ddl_file not in tasks_text:
                errors.append(f"{ddl_file} is referenced as executable change DDL in {design.name} but not in task planning artifacts")
        if not re.search(r"(执行型变更\s*DDL|Executable\s+change\s+DDL|ALTER\s+TABLE)", tasks_text, re.IGNORECASE):
            errors.append("task planning artifacts have no executable change DDL task for the existing-table structural change")

    if DATA_RISK_RE.search(design_text) and not DATA_VERIFICATION_RE.search(tasks_text):
        errors.append("task planning artifacts have no data verification task for triggered data design/governance risk")

    if requires_runtime_service_closure(design_text):
        if not RUNTIME_SERVICE_TASK_RE.search(tasks_text):
            errors.append("task planning artifacts have no runtime service closure task for triggered service runtime design")
        if S2_RE.search(all_text) and not EVIDENCE_MATRIX_RE.search(tasks_text + "\n" + design_text):
            errors.append("S2 task planning artifacts must include an Evidence Matrix for runtime service delivery")

    if requires_runtime_init_dml(design_text):
        if not RUNTIME_INIT_DML_TASK_RE.search(tasks_text):
            errors.append("task planning artifacts have no runtime initialization DML/Seed deliverable task")

    if not has_any_heading(design_text, KNOWLEDGE_IMPACT_HEADINGS):
        errors.append(f"{design.name} is missing knowledge impact section")
    approval_surface = read(task_index) if task_index else tasks_text
    if not has_any_heading(approval_surface, APPROVAL_GATE_HEADINGS):
        errors.append("task plan or task index is missing implementation approval gate section")

    if S2_RE.search(all_text):
        if not has_any_heading(design_text, RISK_ROLLBACK_HEADINGS):
            errors.append(f"S2 {design.name} is missing risk and rollback section")
        for display_name, headings in design_heading_groups:
            if has_any_heading(design_text, headings) and not has_section_content(design_text, headings):
                errors.append(f"S2 {design.name} section '{display_name}' has no content")
        has_s2_quality_gate = has_any_heading(tasks_text, S2_QUALITY_GATE_HEADINGS)
        if not has_s2_quality_gate and not RISK_CONTROL_RE.search(tasks_text):
            errors.append("S2 task planning artifacts must include S2 quality gates or explicit risk-control tasks")

    blocks = task_blocks(tasks_text)
    if not blocks:
        errors.append("task planning artifacts contain no checklist tasks in '- [ ] T001' format")

    seen: set[str] = set()
    requires_test_decision = TEST_DECISION_MARKER in tasks_text
    for task_id, block in blocks:
        if task_id in seen:
            errors.append(f"Duplicate task ID: {task_id}")
        seen.add(task_id)
        if not AC_RE.search(block):
            errors.append(f"{task_id} has no AC mapping")
        for label in ("Files:", "Verification:", "Quality:", "Done:"):
            if label not in block:
                errors.append(f"{task_id} is missing '{label}'")
        errors.extend(validate_quality_domain_check(task_id, block, planning_name))
        if requires_test_decision:
            errors.extend(validate_test_decision(task_id, block, planning_name))

    # UI Gate check: page/UI deliverables must have UI design confirmation evidence
    if requires_ui_design(design_text, tasks_text):
        if not UI_DESIGN_EVIDENCE_RE.search(tasks_text):
            errors.append("task planning artifacts contain UI/page deliverables but have no UI design confirmation task or evidence")

    # Document update time consistency check
    dated_artifacts = [
        ("requirement", spec, spec_text),
        ("technical design", design, design_text),
    ] + [("task planning", path, text) for path, text in planning_text_by_path]
    for doc_name, doc_path, doc_text in dated_artifacts:
        update_match = DOC_UPDATE_DATE_RE.search(doc_text)
        if update_match and update_match.group(1) == "YYYY-MM-DD":
            warnings.append(f"{doc_path.name} has template placeholder date 'YYYY-MM-DD' as update date; update to actual date")

    return errors, warnings


def validate_change_file(change_file: Path) -> list[str]:
    errors: list[str] = []
    if not change_file.exists():
        return [f"Missing change artifact: {change_file}"]

    text = read(change_file)
    errors.extend(validate_required_heading_groups(text, CHANGE_REQUIRED_HEADING_GROUPS, str(change_file)))
    errors.extend(validate_artifact_readiness(text, str(change_file)))

    if not CHANGE_TYPE_RE.search(text):
        errors.append(f"{change_file} is missing change type field")
    if BLOCKING_ARTIFACT_RE.search(text) and TASK_RE.search(text):
        errors.append(f"{change_file} is a draft or blocked CR but contains executable incremental tasks")
    if re.search(r"^- \[[ xX]\] T\d{3}.*(知识同步|知识汇总)", text, re.MULTILINE):
        errors.append(f"{change_file} must not create knowledge-sync or knowledge-summary handoff tasks")

    if not AC_RE.search(text):
        errors.append(f"{change_file} contains no AC-### mapping")
    has_task_pack_reference = bool(
        TASK_PACK_RE.search(text)
        and re.search(r"(?<![A-Za-z0-9_.-])tasks[\\/][^\s`|]+\.md", text, re.IGNORECASE)
    )
    if not TASK_RE.search(text) and not has_task_pack_reference:
        errors.append(f"{change_file} contains neither V1 incremental checklist tasks nor a V2 Task Pack reference")

    requires_test_decision = TEST_DECISION_MARKER in text
    for task_id, block in task_blocks(text):
        for label in ("Files:", "Verification:", "Quality:", "Done:"):
            if label not in block:
                errors.append(f"{task_id} in {change_file} is missing '{label}'")
        errors.extend(validate_quality_domain_check(task_id, block, str(change_file)))
        if requires_test_decision:
            errors.extend(validate_test_decision(task_id, block, str(change_file)))

    ddl_action = (
        re.search(r"SQL DDL action\s*:\s*(add|update|rename)", text, re.IGNORECASE)
        or re.search(r"SQL\s*DDL\s*动作\s*[：:]\s*(新增|更新|重命名)", text)
    )
    if ddl_action:
        sql_files = sorted(set(SQL_PATH_RE.findall(text)))
        if not sql_files:
            errors.append(f"{change_file} declares SQL DDL action but names no .specify/sql/**/*.sql file")
        if not re.search(r"(执行型\s*DDL|执行型变更\s*DDL|Executable\s+change\s+DDL|ALTER\s+TABLE)", text, re.IGNORECASE):
            errors.append(f"{change_file} declares SQL DDL action but has no executable DDL draft task")
        if not re.search(r"(确认\s*DDL\s*执行状态|DDL\s*执行确认|read-only verification|只读.*验证)", text, re.IGNORECASE):
            errors.append(f"{change_file} declares SQL DDL action but has no DDL execution-confirmation task")
        if not re.search(r"(同步\s*SQL\s*当前结构快照|SQL\s*当前结构快照|\\.specify/sql/)", text, re.IGNORECASE):
            errors.append(f"{change_file} declares SQL DDL action but has no SQL current-structure snapshot task")
    if declares_existing_table_change_with_baseline(text):
        executable_ddl_files = executable_ddl_paths(text)
        if not executable_ddl_files:
            errors.append(f"{change_file} declares an existing-table change with baseline DDL but names no executable change DDL file")
        if not re.search(r"(执行型变更\s*DDL|Executable\s+change\s+DDL|ALTER\s+TABLE)", text, re.IGNORECASE):
            errors.append(f"{change_file} has no executable change DDL task for the existing-table structural change")

    # UI Gate check for change files
    if UI_KEYWORD_RE.search(text) and not UI_DESIGN_EVIDENCE_RE.search(text):
        errors.append(f"{change_file} involves UI/page changes but has no UI design confirmation Gate or evidence")

    return errors


def validate_bugfix_report(report: Path) -> list[str]:
    errors: list[str] = []
    if not report.exists():
        return [f"Missing bugfix report: {report}"]

    text = read(report)
    required = (
        "## 问题描述",
        "## 复现步骤",
        "## 根因分析",
        "## 自动化测试",
        "## 手动验证",
        "## 回归验证",
        "## 知识库同步",
    )
    for heading in required:
        if heading not in text:
            errors.append(f"{report} is missing '{heading}'")
    for field in ("回滚方案", "Knowledge Sync Needed", "SQL DDL files"):
        if field not in text:
            errors.append(f"{report} is missing '{field}'")
    if not has_any_heading(text, EVIDENCE_LIST_HEADINGS):
        errors.append(f"{report} is missing evidence list section")
    for phrase in ("复现信号", "根因判断", "修复已生效"):
        if phrase not in text:
            errors.append(f"{report} evidence list is missing '{phrase}'")
    if re.search(r"Status:\s*(Fixed|Verified)", text, re.IGNORECASE) and "L3" not in text:
        errors.append(f"{report} is Fixed/Verified but has no L3 verification evidence")

    return errors


def validate_implementation_report(report: Path) -> list[str]:
    errors: list[str] = []
    if not report.exists():
        return [f"Missing implementation report: {report}"]

    text = read(report)
    required = (
        "## 4. 验证结果",
        "## 5. Evidence Bundle",
        "## 5.1 服务级 Evidence Matrix",
        "## 6. Review 与人工 Gate",
        "## 7. AC 覆盖",
        "## 9. DDL 与数据结构状态",
        "## 9.1 运行初始化 DML / Seed 状态",
        "验证证据等级",
        "未验证项",
        "Review 状态",
        "Spec Review",
        "Code Review",
        "人工 Gate",
        "可交付完成判断",
    )
    for heading in required:
        if heading not in text:
            errors.append(f"{report} is missing '{heading}'")

    declares_complete = bool(
        re.search(r"实施结果\s*[：:]\s*完成", text)
        or re.search(r"是否可交付完成\s*[：:]\s*是", text)
        or re.search(r"是否发布就绪\s*[：:]\s*是", text)
    )
    if declares_complete:
        if not re.search(r"未验证项\s*[：:]\s*无", text):
            errors.append(f"{report} declares completion but has unverified items or no explicit '未验证项：无'")
        if not re.search(r"验证证据等级\s*[：:]\s*L3", text):
            errors.append(f"{report} declares completion but has no L3 verification evidence")
        if not re.search(r"Spec Review\s*[：:]\s*(通过|有条件通过)", text):
            errors.append(f"{report} declares completion but Spec Review is not passed or conditionally passed")
        if not re.search(r"Code Review\s*[：:]\s*(通过|有条件通过)", text):
            errors.append(f"{report} declares completion but Code Review is not passed or conditionally passed")
        if re.search(r"Critical/Important 问题\s*[：:]\s*(?!无|已修复并复审)", text):
            errors.append(f"{report} declares completion but Critical/Important review issues are not closed")
        if (
            re.search(r"人工 Gate 适用性\s*[：:]\s*适用", text)
            and not re.search(r"人工 Gate 状态\s*[：:]\s*(已通过|有条件通过)", text)
        ):
            errors.append(f"{report} declares completion but required human Gate is not passed or conditionally passed")
    if (
        re.search(r"是否涉及 DDL\s*[：:]\s*是", text)
        and re.search(r"DDL 执行状态\s*[：:]\s*未执行", text)
        and re.search(r"是否发布就绪\s*[：:]\s*是", text)
    ):
        errors.append(f"{report} is release-ready while DDL execution is not confirmed")

    # UI Gate check for implementation reports
    if UI_KEYWORD_RE.search(text) and not UI_DESIGN_EVIDENCE_RE.search(text):
        errors.append(f"{report} mentions UI/page deliverables but has no UI design confirmation status record")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Fons4AI SDD artifacts")
    parser.add_argument("--feature-dir", help="Feature directory containing V1 *-任务规划.md or V2 *-任务索引.md plus tasks/*.md")
    parser.add_argument("--change-file", help="Path to spec/features/<yyyymmdd>/changes/CR-xxx.md")
    parser.add_argument("--bugfix-report", help="Path to spec/bugfixes/<yyyymmdd>/<bug中文名>-BUG修复报告.md")
    parser.add_argument("--implementation-report", help="Path to spec/features/<yyyymmdd>/reports/<功能中文名>-实施报告.md")
    parser.add_argument("--strict", action="store_true", help="Fail modern SDD section omissions instead of warning")
    args = parser.parse_args()

    selected = [value for value in (args.feature_dir, args.change_file, args.bugfix_report, args.implementation_report) if value]
    if len(selected) != 1:
        print("ERROR: provide exactly one of --feature-dir, --change-file, --bugfix-report, or --implementation-report", file=sys.stderr)
        return 2

    if args.feature_dir:
        target = Path(args.feature_dir).resolve()
        errors, warnings = validate(target, strict=args.strict)
        success = f"OK: {target} SDD artifacts are valid"
    elif args.change_file:
        target = Path(args.change_file).resolve()
        errors = validate_change_file(target)
        warnings = []
        success = f"OK: {target} SDD change artifact is valid"
    elif args.bugfix_report:
        target = Path(args.bugfix_report).resolve()
        errors = validate_bugfix_report(target)
        warnings = []
        success = f"OK: {target} bugfix report is valid"
    else:
        target = Path(args.implementation_report).resolve()
        errors = validate_implementation_report(target)
        warnings = []
        success = f"OK: {target} implementation report is valid"

    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(success)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
