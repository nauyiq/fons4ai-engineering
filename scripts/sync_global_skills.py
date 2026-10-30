"""Explicitly install the five-skill suite, preserving replaced skills in backups."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from uuid import uuid4

from validate_repository import OBSOLETE_SKILLS, SKILLS, validate_suite


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_link(path):
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def reject_links(path):
    path = Path(path).absolute()
    for item in [path, *path.parents]:
        if is_link(item):
            raise ValueError(f"symlink/junction is not supported: {item}")
    if path.is_dir():
        for item in path.rglob("*"):
            if is_link(item):
                raise ValueError(f"symlink/junction is not supported: {item}")


def collect_skill_files(directory):
    reject_links(directory)
    return {
        path.relative_to(directory).as_posix(): sha256(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and "__pycache__" not in path.relative_to(directory).parts
        and path.suffix not in {".pyc", ".pyo"}
    }


def collect_skills(root):
    root = Path(root)
    return {name: collect_skill_files(root / name)
            for name in sorted(SKILLS) if (root / name / "SKILL.md").is_file()}


def validate_paths(source, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("source and target must not be equal or contain one another")


def obsolete_at(target):
    return sorted(name for name in OBSOLETE_SKILLS if (target / name).exists() or (target / name).is_symlink())


def verify_target(target, expected):
    errors = []
    for name, files in expected.items():
        path = target / name
        actual = collect_skill_files(path) if path.is_dir() else {}
        if actual != files:
            errors.append(f"skill contents differ: {path}")
    for name in obsolete_at(target):
        errors.append(f"obsolete discoverable entry: {target / name}; use --archive-obsolete explicitly")
    return errors


def synchronize(source, target, expected, archive_obsolete=False):
    validate_paths(source, target)
    # Only inspect managed target directories; unrelated user skills are untouched.
    reject_links(source)
    for ancestor in [target, *target.parents]:
        if is_link(ancestor):
            raise ValueError(f"symlink/junction is not supported: {ancestor}")
    errors = validate_suite(source)
    if errors:
        raise ValueError("invalid source suite: " + "; ".join(errors))
    if set(expected) != SKILLS or collect_skills(source) != expected:
        raise ValueError("source suite changed or expected manifest is incomplete")
    obsolete = obsolete_at(target)
    if obsolete and not archive_obsolete:
        raise ValueError("obsolete entries detected; review and use --archive-obsolete: " + ", ".join(obsolete))
    for name in sorted(SKILLS | set(obsolete)):
        path = target / name
        reject_links(path)
        if path.exists() and not path.is_dir():
            raise ValueError(f"managed target is not a directory: {path}")
    changed = [name for name, files in expected.items()
               if not (target / name).is_dir() or collect_skill_files(target / name) != files]
    if not changed and not obsolete:
        return None
    target.mkdir(parents=True, exist_ok=True)
    backup = target.parent / ".fons4ai-backups" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    reject_links(backup.parent)
    with tempfile.TemporaryDirectory(prefix=".fons4ai-stage-", dir=target.parent) as temporary:
        stage = Path(temporary)
        for name, files in expected.items():
            for relative in files:
                destination = stage / name / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / name / relative, destination)
        if verify_target(stage, expected) or validate_suite(stage):
            raise ValueError("staged suite failed verification; target was not changed")
        moved, installed = [], []
        try:
            for name in sorted(set(changed) | set(obsolete)):
                destination = target / name
                if destination.exists():
                    backup.mkdir(parents=True, exist_ok=True)
                    os.replace(destination, backup / name)
                    moved.append(name)
            for name in changed:
                os.replace(stage / name, target / name)
                installed.append(name)
            failures = verify_target(target, expected)
            if failures:
                raise RuntimeError("installed suite verification failed: " + "; ".join(failures))
        except Exception:
            # Only paths installed in this transaction are removed during rollback.
            for name in reversed(installed):
                shutil.rmtree(target / name)
            for name in reversed(moved):
                os.replace(backup / name, target / name)
            raise
    return backup if backup.exists() else None


def write_lock(root, expected):
    payload = {"version": 2, "skills": {name: {"files": files} for name, files in expected.items()}}
    (root / "skills-lock.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_lock(root, expected):
    try:
        payload = json.loads((root / "skills-lock.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cannot read skills-lock.json: {exc}"]
    wanted = {"version": 2, "skills": {name: {"files": files} for name, files in expected.items()}}
    return [] if payload == wanted else ["source lock differs; run sync_global_skills.py --write-lock after reviewing changes"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--archive-obsolete", action="store_true", help="Move known v1 entries to backup outside discovery")
    parser.add_argument("--write-lock", action="store_true", help="Update source hashes only; does not install")
    args = parser.parse_args()
    if args.write_lock and (args.target or args.check_only or args.archive_obsolete):
        parser.error("--write-lock cannot be combined with installation options")
    if not args.write_lock and not args.target:
        parser.error("--target is required unless using --write-lock")
    if args.check_only and args.archive_obsolete:
        parser.error("--check-only cannot archive entries")
    try:
        root = args.root.resolve()
        source = root / "skills"
        errors = validate_suite(source)
        if errors:
            raise ValueError("; ".join(errors))
        expected = collect_skills(source)
        if args.write_lock:
            write_lock(root, expected)
            print("OK: updated source lock for five skills; no installation performed")
            return 0
        # Check supplied path before resolving away a link.
        for item in [args.target.absolute(), *args.target.absolute().parents]:
            if is_link(item):
                raise ValueError(f"symlink/junction is not supported: {item}")
        target = args.target.resolve()
        validate_paths(source, target)
        errors = verify_lock(root, expected)
        if errors:
            raise ValueError("; ".join(errors))
        if args.check_only:
            errors = verify_target(target, expected)
            if errors:
                raise ValueError("; ".join(errors))
            print("OK: installed skills match source; no obsolete entries")
        else:
            backup = synchronize(source, target, expected, args.archive_obsolete)
            print("OK: installed and verified five skills")
            if backup:
                print(f"Previous files preserved at: {backup}")
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
