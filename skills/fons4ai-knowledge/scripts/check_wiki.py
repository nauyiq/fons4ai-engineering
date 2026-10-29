"""Check root navigation, inline Markdown file links and Wiki reachability.

Fenced/inline code and external links are ignored. Fragment anchors are not
validated. Inline destinations support balanced parentheses, punctuation escapes
and angle brackets. Reference-style/HTML links and semantic accuracy are not checked.
"""
import argparse
from pathlib import Path
import re
import string
import sys
from urllib.parse import unquote, urlsplit


def markdown_text(text):
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def inline_destinations(text):
    """Read inline destinations without truncating nested or escaped parentheses."""
    for match in re.finditer(r"!?\[(?:\\.|[^\]\\\n])*\]\(", text):
        pos = match.end()
        while pos < len(text) and text[pos].isspace():
            pos += 1
        angled = pos < len(text) and text[pos] == "<"
        start = pos = pos + int(angled)
        depth = 0
        while pos < len(text):
            char = text[pos]
            if char == "\\" and pos + 1 < len(text) and text[pos + 1] in string.punctuation:
                pos += 2
                continue
            if angled:
                if char in ">\r\n":
                    break
            else:
                if char.isspace() or (char == ")" and depth == 0):
                    break
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
            pos += 1
        raw = text[start:pos]
        if depth or pos >= len(text):
            continue
        if angled:
            if text[pos] != ">":
                continue
            pos += 1
        # A destination may be followed by whitespace and an optional link title.
        end = pos
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos > end and pos < len(text) and text[pos] in "\"'(":
            closing = ")" if text[pos] == "(" else text[pos]
            pos += 1
            while pos < len(text) and text[pos] != closing:
                if text[pos] == "\\" and pos + 1 < len(text) and text[pos + 1] in string.punctuation:
                    pos += 1
                pos += 1
            if pos >= len(text):
                continue
            pos += 1
            while pos < len(text) and text[pos].isspace():
                pos += 1
        if pos < len(text) and text[pos] == ")":
            yield re.sub(r"\\([" + re.escape(string.punctuation) + r"])", r"\1", raw)


def local_targets(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    if not path.is_relative_to(root):
        return [], [f"outside allowed root: {path}"]
    text = markdown_text(path.read_text(encoding="utf-8-sig"))
    targets, errors = [], []
    for raw in inline_destinations(text):
        parsed = urlsplit(raw)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(root):
            errors.append(f"{path}: link outside allowed root: {raw}")
        elif not target.exists():
            errors.append(f"{path}: missing link target: {raw}")
        else:
            targets.append(target)
    return targets, errors


def check_links(path, root):
    return local_targets(path, root)[1]


def check_wiki(root):
    root = Path(root).resolve()
    errors = []
    for name in ("README.md", "AGENTS.md"):
        variants = sorted(p for p in root.iterdir() if p.name.casefold() == name.casefold() and p.is_file())
        if not variants:
            errors.append(f"missing root navigation: {root / name}")
        for page in variants:
            errors.extend(check_links(page, root))
    wiki = root / "docs/wiki"
    index = wiki / "index.md"
    if not index.is_file():
        return errors + [f"missing Wiki entry: {index}"]
    pages = {path.resolve() for path in wiki.rglob("*.md")}
    graph = {}
    for page in sorted(pages):
        targets, issues = local_targets(page, root)
        graph[page] = set(targets) & pages
        errors.extend(issues)
    seen, pending = set(), [index.resolve()]
    while pending:
        page = pending.pop()
        if page not in seen:
            seen.add(page)
            pending.extend(graph.get(page, ()))
    errors.extend(f"Wiki page not reachable from index: {page}" for page in sorted(pages - seen))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        errors = check_wiki(args.root)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if not errors:
        print("OK: root navigation, Wiki file links and index reachability (anchors/semantics not checked)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
