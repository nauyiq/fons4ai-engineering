#!/usr/bin/env python3
"""Validate and synchronize Fons4AI skills to a user-level skills directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


LOCK_FILE = "skills-lock.json"
IGNORED_FILE_SUFFIXES = {".pyc", ".pyo"}


def is_ignored_skill_file(path: Path, skill_dir: Path) -> bool:
    relative = path.relative_to(skill_dir)
    return "__pycache__" in relative.parts or path.suffix.lower() in IGNORED_FILE_SUFFIXES


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_skill_files(skill_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(skill_dir).as_posix(): sha256(path)
        for path in sorted(skill_dir.rglob("*"))
        if path.is_file() and not is_ignored_skill_file(path, skill_dir)
    }


def collect_skills(skills_root: Path) -> dict[str, dict[str, str]]:
    skills: dict[str, dict[str, str]] = {}
    for skill_dir in sorted(skills_root.glob("fons4ai-*")):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
            skills[skill_dir.name] = collect_skill_files(skill_dir)
    return skills


def validate_repository(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_all.py", "--root", "."],
        cwd=root,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("repository validation failed; global sync was not started")


def sync_skill(source: Path, destination: Path, expected_files: dict[str, str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    expected_paths = {Path(relative_path) for relative_path in expected_files}
    for target_file in sorted(destination.rglob("*"), reverse=True):
        if target_file.is_file() and target_file.relative_to(destination) not in expected_paths:
            target_file.unlink()
        elif target_file.is_dir() and not any(target_file.iterdir()):
            target_file.rmdir()
    for relative_path in expected_files:
        source_file = source / relative_path
        target_file = destination / relative_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)


def verify_target(target_root: Path, expected: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for skill_name, expected_files in expected.items():
        target = target_root / skill_name
        actual_files = collect_skill_files(target) if target.is_dir() else {}
        if actual_files != expected_files:
            errors.append(f"hash mismatch after sync: {target}")
    return errors


def write_lock(root: Path, expected: dict[str, dict[str, str]]) -> None:
    path = root / LOCK_FILE
    payload: dict[str, object] = {"version": 1, "skills": {}}
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    skill_records = payload.setdefault("skills", {})
    if not isinstance(skill_records, dict):
        raise ValueError(f"{path} has an invalid skills section")
    for name in list(skill_records):
        if name.startswith("fons4ai-") and name not in expected:
            del skill_records[name]
    for name, files in expected.items():
        skill_records[name] = {"files": files}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and synchronize Fons4AI skills with hash verification"
    )
    parser.add_argument("--target", required=True, help="Global .agents/skills directory")
    parser.add_argument("--skills-root", default="skills", help="Source skills directory")
    parser.add_argument("--check-only", action="store_true", help="Only compare source and target")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    source_root = (root / args.skills_root).resolve()
    target_root = Path(args.target).resolve()
    if not source_root.is_dir():
        print(f"ERROR: source skills directory not found: {source_root}", file=sys.stderr)
        return 1
    if not target_root.is_dir():
        print(f"ERROR: target skills directory not found: {target_root}", file=sys.stderr)
        return 1
    if source_root == target_root:
        print("ERROR: source and target skills directories must differ", file=sys.stderr)
        return 1

    expected = collect_skills(source_root)
    if not expected:
        print(f"ERROR: no Fons4AI skills found in {source_root}", file=sys.stderr)
        return 1

    if args.check_only:
        errors = verify_target(target_root, expected)
        if errors:
            print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
            return 1
        print("OK: global Fons4AI skills match the source hashes")
        return 0

    try:
        validate_repository(root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for skill_name, files in expected.items():
        sync_skill(source_root / skill_name, target_root / skill_name, files)
    errors = verify_target(target_root, expected)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    write_lock(root, expected)
    print(f"OK: synchronized and hash-verified {len(expected)} Fons4AI skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
