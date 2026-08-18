#!/usr/bin/env python3

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT = PROJECT_ROOT / "zephyr_export.txt"

IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

IGNORE_FILES = {
    OUTPUT.name,
}


def should_ignore(path: Path):
    return any(part in IGNORE_DIRS for part in path.parts)


def build_tree(path: Path, prefix=""):
    entries = sorted(
        [
            p
            for p in path.iterdir()
            if p.name not in IGNORE_FILES
            and not should_ignore(p)
        ],
        key=lambda p: (p.is_file(), p.name.lower()),
    )

    lines = []

    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(build_tree(entry, prefix + extension))

    return lines


with OUTPUT.open("w", encoding="utf-8") as out:

    out.write("=" * 80 + "\n")
    out.write("ZEPHYR PROJECT EXPORT\n")
    out.write("=" * 80 + "\n\n")

    out.write("PROJECT TREE\n")
    out.write("-" * 80 + "\n")
    out.write(".\n")

    for line in build_tree(PROJECT_ROOT):
        out.write(line + "\n")

    out.write("\n\n")

    py_files = sorted(PROJECT_ROOT.rglob("*.py"))

    for file in py_files:

        if should_ignore(file):
            continue

        relative = file.relative_to(PROJECT_ROOT)

        out.write("=" * 80 + "\n")
        out.write(f"FILE: {relative}\n")
        out.write("=" * 80 + "\n\n")

        try:
            out.write(file.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            out.write(file.read_text(encoding="latin-1"))

        out.write("\n\n")
