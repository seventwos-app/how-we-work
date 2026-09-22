#!/usr/bin/env python3
"""Deterministic workflow-policy and static-HTML security checks."""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


PINNED_ACTION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
PINNED_CONTAINER_RE = re.compile(r"^docker://.+@sha256:[0-9a-fA-F]{64}$")
USES_RE = re.compile(r"^\s*-\s+uses:\s*([^\s#]+)")
WRITE_PERMISSION_RE = re.compile(
    r"^\s*(actions|attestations|checks|contents|deployments|discussions|id-token|"
    r"issues|models|packages|pages|pull-requests|security-events|statuses):\s*write\s*$",
    re.MULTILINE,
)
INLINE_WRITE_PERMISSION_RE = re.compile(r"^\s*permissions:\s*\{[^}]*:\s*write\b", re.MULTILINE)
TOP_LEVEL_PERMISSIONS_RE = re.compile(r"^permissions:\s*(?:$|\{)", re.MULTILINE)
PR_TRIGGER_RE = re.compile(
    r"^\s{2}(pull_request|pull_request_target):\s*(?:\{\}|\[\])?\s*$|"
    r"^\s*on:\s*\[[^\]]*\bpull_request(?:_target)?\b",
    re.MULTILINE,
)
SECRET_REFERENCE_RE = re.compile(r"\$\{\{\s*secrets\.")


class StaticHTMLScanner(HTMLParser):
    """Find active-content patterns that are unsafe in a public static site."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.findings = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)

        if tag == "base":
            self.findings.append((self.getpos()[0], "SECHTML001", "base elements are not allowed"))

        for attribute in ("src", "href", "action"):
            value = values.get(attribute, "").strip()
            if value.lower().startswith(("javascript:", "vbscript:")):
                self.findings.append(
                    (self.getpos()[0], "SECHTML002", f"{attribute} uses an executable URL scheme")
                )

        if tag in {"script", "iframe", "object", "embed"}:
            source = values.get("src") or values.get("data") or ""
            parsed = urlparse(source)
            if parsed.scheme == "http":
                self.findings.append(
                    (self.getpos()[0], "SECHTML003", f"{tag} loads active content over HTTP")
                )
            external_script = tag == "script" and (
                parsed.scheme in {"http", "https"} or source.startswith("//")
            )
            if external_script and "integrity" not in values:
                self.findings.append(
                    (
                        self.getpos()[0],
                        "SECHTML004",
                        "external HTTPS script must declare a subresource-integrity hash",
                    )
                )

        if values.get("target", "").lower() == "_blank":
            rel = set(values.get("rel", "").lower().split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                self.findings.append(
                    (
                        self.getpos()[0],
                        "SECHTML005",
                        'target="_blank" links must use rel="noopener noreferrer"',
                    )
                )


def workflow_findings(path):
    text = path.read_text(encoding="utf-8")
    findings = []

    if re.search(r"^\s{2}pull_request_target:\s*", text, re.MULTILINE):
        findings.append((1, "SECWF001", "pull_request_target is not allowed"))

    if re.search(r"^\s*permissions:\s*(write-all|read-all)\s*$", text, re.MULTILINE):
        findings.append((1, "SECWF002", "permissions must be an explicit least-privilege map"))

    if not TOP_LEVEL_PERMISSIONS_RE.search(text):
        findings.append((1, "SECWF006", "workflow must declare top-level permissions"))

    for line_number, line in enumerate(text.splitlines(), start=1):
        match = USES_RE.match(line)
        if not match:
            continue
        reference = match.group(1)
        if reference.startswith("./"):
            continue
        if reference.startswith("docker://"):
            if not PINNED_CONTAINER_RE.fullmatch(reference):
                findings.append(
                    (line_number, "SECWF003", "container actions must be pinned by sha256 digest")
                )
            continue
        if "@" not in reference or not PINNED_ACTION_RE.fullmatch(reference.rsplit("@", 1)[1]):
            findings.append(
                (line_number, "SECWF004", "third-party actions must be pinned to a full commit SHA")
            )

    if PR_TRIGGER_RE.search(text) and (
        WRITE_PERMISSION_RE.search(text)
        or INLINE_WRITE_PERMISSION_RE.search(text)
        or re.search(r"^\s*permissions:\s*write-all\s*$", text, re.MULTILINE)
        or SECRET_REFERENCE_RE.search(text)
    ):
        findings.append(
            (
                1,
                "SECWF005",
                "pull-request workflows must not receive write permissions or repository secrets",
            )
        )

    return findings


def html_findings(path):
    scanner = StaticHTMLScanner(path)
    scanner.feed(path.read_text(encoding="utf-8"))
    scanner.close()
    return scanner.findings


def scan(root):
    findings = []
    workflow_dir = root / ".github" / "workflows"
    for pattern in ("*.yml", "*.yaml"):
        for path in sorted(workflow_dir.glob(pattern)):
            findings.extend((path, *finding) for finding in workflow_findings(path))

    for pattern in ("*.html", "*.htm"):
        for path in sorted(root.rglob(pattern)):
            if ".git" not in path.parts and "graphify-out" not in path.parts:
                findings.extend((path, *finding) for finding in html_findings(path))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    root = args.root.resolve()
    findings = scan(root)

    for path, line, rule, message in findings:
        relative = path.relative_to(root)
        print(f"::error file={relative},line={line},title={rule}::{message}")

    if findings:
        print(f"Security canary found {len(findings)} violation(s).", file=sys.stderr)
        return 1
    print("Security canary passed: workflow policy and static HTML checks are clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
