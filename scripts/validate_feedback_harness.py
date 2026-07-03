#!/usr/bin/env python3
"""Validate the repository-level Feedback Harness entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = (
    "skills/fons4ai-sdd-implement/SKILL.md",
    "skills/fons4ai-sdd-implement/assets/templates/implementation-report-template.md",
    "skills/fons4ai-sdd-tasks/scripts/validate_sdd_artifacts.py",
    "skills/fons4ai-bugfix-workflow/SKILL.md",
    "skills/fons4ai-bugfix-workflow/assets/templates/bugfix-report-template.md",
    "skills/fons4ai-bugfix-workflow/scripts/validate_bugfix_report.py",
    "skills/fons4ai-agent-env-readiness/SKILL.md",
    "skills/fons4ai-agent-env-readiness/assets/templates/readiness-report-template.md",
    "skills/fons4ai-agent-env-readiness/scripts/validate_readiness_report.py",
    "skills/fons4ai-harness-feedback/SKILL.md",
    "skills/fons4ai-harness-feedback/agents/openai.yaml",
    "skills/fons4ai-harness-feedback/assets/templates/upstream-feedback-template.md",
    "skills/fons4ai-harness-feedback/scripts/validate_harness_feedback.py",
    "skills/fons4ai-knowledge-summary/SKILL.md",
    "onboarding/business-project/README.md",
    "scripts/validate_business_project_harness.py",
    "docs/harness-engineering.md",
    "docs/harness-layer-map.md",
)

TEXT_REQUIREMENTS = (
    (
        "implementation skill must require evidence and implementation report",
        "skills/fons4ai-sdd-implement/SKILL.md",
        (
            "## Evidence Required",
            "L3 Gate Evidence",
            "spec/features/<yyyymmdd>/reports",
            "implementation-report-template.md",
            "Evidence Bundle",
            "Spec Review",
            "Code Review",
            "人工 Gate",
        ),
    ),
    (
        "implementation report template must carry evidence and review gates",
        "skills/fons4ai-sdd-implement/assets/templates/implementation-report-template.md",
        ("Evidence Bundle", "Review 与人工 Gate", "Spec Review", "Code Review", "人工 Gate", "可交付完成判断"),
    ),
    (
        "SDD artifact validator must enforce implementation report review gates",
        "skills/fons4ai-sdd-tasks/scripts/validate_sdd_artifacts.py",
        ("Evidence Bundle", "Spec Review", "Code Review", "人工 Gate", "可交付完成判断"),
    ),
    (
        "bugfix skill must require evidence and bugfix report",
        "skills/fons4ai-bugfix-workflow/SKILL.md",
        ("## Evidence Required", "L3 Gate Evidence", "spec/bugfixes/<yyyymmdd>", "validate_bugfix_report.py"),
    ),
    (
        "environment readiness skill must produce a readiness report",
        "skills/fons4ai-agent-env-readiness/SKILL.md",
        ("Agent", "readiness-report-template.md", "validate_readiness_report.py"),
    ),
    (
        "harness feedback skill must be explicit-trigger only",
        "skills/fons4ai-harness-feedback/SKILL.md",
        ("spec/reports/harness-feedback", "必须由用户显式要求", "不自动触发", "validate_harness_feedback.py"),
    ),
    (
        "harness feedback template must carry required report sections",
        "skills/fons4ai-harness-feedback/assets/templates/upstream-feedback-template.md",
        ("spec/reports/harness-feedback", "PROJECT_LOCAL", "SKILL_CONTRACT", "VALIDATOR_GAP", "EVIDENCE_GAP", "CROSS_PROJECT_REPEAT"),
    ),
    (
        "harness feedback validator must enforce path and categories",
        "skills/fons4ai-harness-feedback/scripts/validate_harness_feedback.py",
        ("spec/reports/harness-feedback", "CLASSIFICATION_TERMS", "FORBIDDEN_TERMS"),
    ),
    (
        "knowledge summary must accept verified implementation and bugfix evidence",
        "skills/fons4ai-knowledge-summary/SKILL.md",
        ("## Evidence Required", "实施报告", "BUG 修复报告", "L3 Gate Evidence"),
    ),
    (
        "business project onboarding guide must describe orchestration and validation",
        "onboarding/business-project/README.md",
        ("业务项目 Harness 接入编排与验收", "fons4ai-knowledge-bootstrap", "fons4ai-generate-project-rules", "validate_business_project_harness.py"),
    ),
    (
        "business project validator must enforce core onboarding assets",
        "scripts/validate_business_project_harness.py",
        ("AGENTS.md", ".specify/rules/agent运行规则.md", ".specify/memory/index.md", "Evidence Bundle", "人工 Gate"),
    ),
    (
        "harness docs must describe Feedback Harness and feedback path",
        "docs/harness-engineering.md",
        ("Feedback Harness", "spec/reports/harness-feedback", "上游反馈单"),
    ),
    (
        "layer map must include the feedback skill",
        "docs/harness-layer-map.md",
        ("Feedback Harness", "fons4ai-harness-feedback", "spec/reports/harness-feedback"),
    ),
)

ACTIVE_REF_SCAN_ROOTS = (
    "skills",
    "scripts",
)

TEXT_SCAN_ROOTS = (
    "README.md",
    "docs",
    "skills",
    "scripts",
)

TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt"}
REMOVED_SKILL = "fons4ai-" + "project-knowledge-base-init"
OLD_FEEDBACK_PATH = ".specify" + "/reports/harness-feedback"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def collect_text_files(root: Path, entries: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for entry in entries:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                files.append(child)
    return files


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def validate_required_files(root: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            errors.append(f"missing required Feedback Harness asset: {name}")
    return errors


def validate_text_requirements(root: Path) -> list[str]:
    errors: list[str] = []
    for label, file_name, required_terms in TEXT_REQUIREMENTS:
        path = root / file_name
        if not path.exists():
            continue
        text = read_text(path)
        missing = [term for term in required_terms if term not in text]
        if missing:
            errors.append(f"{file_name}: {label}; missing terms: {', '.join(missing)}")
    return errors


def validate_feedback_path(root: Path) -> list[str]:
    errors: list[str] = []
    for path in collect_text_files(root, TEXT_SCAN_ROOTS):
        text = read_text(path)
        if OLD_FEEDBACK_PATH in text:
            errors.append(f"{relative(path, root)} contains removed feedback path {OLD_FEEDBACK_PATH}")
    return errors


def validate_removed_skill_refs(root: Path) -> list[str]:
    errors: list[str] = []
    for path in collect_text_files(root, ACTIVE_REF_SCAN_ROOTS):
        text = read_text(path)
        if REMOVED_SKILL in text:
            errors.append(f"{relative(path, root)} still references removed skill {REMOVED_SKILL}")
    lock_file = root / "skills-lock.json"
    if lock_file.exists() and REMOVED_SKILL in read_text(lock_file):
        errors.append(f"skills-lock.json still references removed skill {REMOVED_SKILL}")
    return errors


def validate_no_shared_skill_dependency(root: Path) -> list[str]:
    errors: list[str] = []
    for path in collect_text_files(root, ("skills",)):
        text = read_text(path)
        if "../shared/" in text or "skills/shared" in text:
            errors.append(f"{relative(path, root)} must not depend on sibling shared skill files")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_required_files(root))
    errors.extend(validate_text_requirements(root))
    errors.extend(validate_feedback_path(root))
    errors.extend(validate_removed_skill_refs(root))
    errors.extend(validate_no_shared_skill_dependency(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Feedback Harness entrypoint assets")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: Feedback Harness entrypoint assets are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
