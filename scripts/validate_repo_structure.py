#!/usr/bin/env python3
"""Repository structure and content validation checks for CI."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "SECURITY.md",
    "requirements.txt",
    "src",
    "tests",
    "docs",
    ".github/workflows",
]

MARKDOWN_GLOBS = ["*.md", "docs/**/*.md"]


def validate_required_paths() -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_PATHS:
        candidate = ROOT / rel_path
        if not candidate.exists():
            errors.append(f"Missing required path: {rel_path}")
    return errors


def iter_markdown_files() -> set[Path]:
    files: set[Path] = set()
    for pattern in MARKDOWN_GLOBS:
        for path in ROOT.glob(pattern):
            if ".git" in path.parts:
                continue
            if path.is_file():
                files.add(path)
    return files


def validate_markdown_files() -> list[str]:
    errors: list[str] = []
    markdown_files = sorted(iter_markdown_files())

    if not markdown_files:
        errors.append("No markdown files were found.")
        return errors

    for md_file in markdown_files:
        rel = md_file.relative_to(ROOT)
        text = md_file.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if line.endswith(" "):
                errors.append(f"{rel}:{line_no} trailing whitespace")
            if "\t" in line:
                errors.append(f"{rel}:{line_no} contains tab character")
    return errors


def validate_workflows() -> list[str]:
    errors: list[str] = []
    workflow_files = sorted((ROOT / ".github/workflows").glob("*.yml"))
    if len(workflow_files) < 3:
        errors.append("Expected at least 3 workflow files in .github/workflows")

    for workflow in workflow_files:
        content = workflow.read_text(encoding="utf-8")
        if "permissions:" not in content:
            errors.append(
                f"{workflow.relative_to(ROOT)} should declare explicit workflow permissions"
            )
    return errors


def main() -> int:
    errors = [
        *validate_required_paths(),
        *validate_markdown_files(),
        *validate_workflows(),
    ]

    if errors:
        print("Repository validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
