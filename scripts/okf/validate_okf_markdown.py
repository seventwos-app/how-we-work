#!/usr/bin/env python3
"""Open Knowledge Format (OKF) v0.2 markdown validator.

Checks that markdown files in this repository carry OKF-conformant YAML
frontmatter. This repo is a single small OKF bundle: `README.md` is the
one concept (`type: Vision`), `index.md` is the reserved bundle index
(`okf_version` frontmatter, not `type`), and `log.md` is the reserved,
frontmatter-free update log. See:
https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

Modes:
  --changed   Check only files changed vs. the merge-base with the default
              branch (falls back to the working tree diff). Exit non-zero
              on any violation. This is what CI runs on pull requests.
  --all       Scan every markdown file in the repo. Never fails the build;
              prints a conformance report. Use to gauge legacy debt.

No third-party dependencies: frontmatter is parsed with a small,
purpose-built scanner (only top-level `key: value` pairs are needed),
not a general YAML parser.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTMATTER_DELIM = "---"

# Reserved OKF bundle filenames. Per this repo's established convention:
# - index.md carries `okf_version` frontmatter, not `type`.
# - log.md is a plain, frontmatter-free update log.
# Neither is required to carry a `type` field the way an ordinary concept
# file (e.g. README.md) is.
RESERVED_INDEX_NAME = "index.md"
RESERVED_LOG_NAME = "log.md"
RESERVED_NAMES = {RESERVED_INDEX_NAME, RESERVED_LOG_NAME}

EXCLUDED_DIR_PARTS = {"node_modules", ".git", "dist", "build", "vendor"}

# GitHub Copilot tooling-config files carry their own contract (or none),
# not OKF's `type` -- out of scope for this content convention, same as
# .agent.md / SKILL.md / .prompt.md files elsewhere.
EXCLUDED_RELATIVE_PATHS = {
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
}


def is_excluded(path):
    try:
        rel_posix = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return False
    return rel_posix in EXCLUDED_RELATIVE_PATHS


class Frontmatter:
    def __init__(self, raw, keys, end_line):
        self.raw = raw
        self.keys = keys
        self.end_line = end_line

    @property
    def has_type(self):
        return "type" in self.keys and bool(self.keys["type"].strip())

    @property
    def has_okf_version(self):
        return "okf_version" in self.keys and bool(self.keys["okf_version"].strip())


def parse_frontmatter(text):
    """Return a Frontmatter if the file opens with a --- block, else None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None
    keys = {}
    end_line = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIM:
            end_line = i
            break
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, _, value = line.partition(":")
            keys[key.strip()] = value.strip()
    if end_line is None:
        return None
    raw = "\n".join(lines[: end_line + 1])
    return Frontmatter(raw, keys, end_line)


def iter_markdown_files():
    for path in REPO_ROOT.rglob("*.md"):
        if any(part in EXCLUDED_DIR_PARTS for part in path.parts):
            continue
        if is_excluded(path):
            continue
        yield path


def changed_markdown_files():
    """Best-effort: diff against origin/main, else HEAD, else working tree."""
    candidates = [
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "origin/main...HEAD"],
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
        ["git", "diff", "--name-only", "--diff-filter=ACMR"],
    ]
    for cmd in candidates:
        try:
            out = subprocess.run(
                cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        files = [
            REPO_ROOT / line.strip()
            for line in out.stdout.splitlines()
            if line.strip().endswith(".md")
        ]
        files = [f for f in files if f.exists() and not is_excluded(f)]
        if files:
            return files
    return []


def check_file(path):
    """Return a list of violation strings for a single file (empty = clean)."""
    violations = []
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    name = path.name

    if name == RESERVED_INDEX_NAME:
        if fm is None or not fm.has_okf_version:
            violations.append(
                "reserved bundle index file must carry an 'okf_version' frontmatter field"
            )
        return violations

    if name == RESERVED_LOG_NAME:
        # log.md is intentionally frontmatter-free in this repo's convention.
        return violations

    if fm is None:
        violations.append("missing YAML frontmatter (no leading '---' block)")
    elif not fm.has_type:
        violations.append("frontmatter present but missing required 'type' field")

    return violations


def run_changed(strict=True):
    files = changed_markdown_files()
    if not files:
        print("okf-validate: no changed markdown files.")
        return 0
    failed = False
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        violations = check_file(path)
        if violations:
            failed = True
            for v in violations:
                print(f"FAIL {rel}: {v}")
        else:
            print(f"OK   {rel}")
    if failed:
        print("\nokf-validate: one or more changed markdown files are non-conformant.")
        return 1 if strict else 0
    print("\nokf-validate: all changed markdown files conform.")
    return 0


def run_all():
    files = list(iter_markdown_files())
    total = len(files)
    clean = 0
    for path in sorted(files):
        rel = path.relative_to(REPO_ROOT)
        violations = check_file(path)
        if violations:
            for v in violations:
                print(f"REPORT {rel}: {v}")
        else:
            clean += 1
    print(f"\nokf-validate baseline: {clean}/{total} markdown files conform.")
    return 0  # report-only, never fails the build


def main():
    parser = argparse.ArgumentParser(description="OKF v0.2 markdown validator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--changed", action="store_true", help="check changed files only (CI mode)")
    group.add_argument("--all", action="store_true", help="scan entire repo, report-only")
    args = parser.parse_args()

    if args.changed:
        return run_changed(strict=True)
    if args.all:
        return run_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
