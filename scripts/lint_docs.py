#!/usr/bin/env python3
"""Lightweight markdown lint for core docs used in pre-commit."""

from __future__ import annotations

from pathlib import Path
import re
import sys

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
TARGET_FILES = [Path("README.md"), Path("docs/README_EN.md")]


def lint_file(path: Path) -> list[str]:
    errors: list[str] = []
    seen_headings: set[str] = set()

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.rstrip() != line:
            errors.append(f"{path}:{line_no} trailing whitespace")

        match = HEADING_RE.match(line)
        if not match:
            continue

        heading_text = match.group(2).strip().lower()
        if heading_text in seen_headings:
            errors.append(f"{path}:{line_no} duplicate heading '{match.group(2).strip()}'")
        else:
            seen_headings.add(heading_text)

    return errors


def main() -> int:
    all_errors: list[str] = []
    for md_file in TARGET_FILES:
        if md_file.exists():
            all_errors.extend(lint_file(md_file))

    if all_errors:
        for error in all_errors:
            print(error)
        return 1

    print(f"Docs lint passed ({len(TARGET_FILES)} markdown files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
