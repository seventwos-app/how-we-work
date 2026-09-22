#!/usr/bin/env python3
"""Deterministic workflow-policy and static-HTML security checks."""

import argparse
import base64
import binascii
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


PINNED_ACTION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
PINNED_CONTAINER_RE = re.compile(r"^docker://.+@sha256:[0-9a-fA-F]{64}$")
MAPPING_RE = re.compile(
    r"^(?P<indent>\s*)(?:-\s*)?(?P<quote>['\"]?)(?P<key>[A-Za-z0-9_-]+)"
    r"(?P=quote)\s*:\s*(?P<value>.*)$"
)
SEQUENCE_RE = re.compile(r"^(?P<indent>\s*)-\s+(?P<value>[^#].*?)\s*$")
PERMISSION_KEYS = {
    "actions", "attestations", "checks", "contents", "deployments", "discussions",
    "id-token", "issues", "models", "packages", "pages", "pull-requests",
    "security-events", "statuses",
}
SECRETS_WORD_RE = re.compile(r"\bsecrets\b")
SRI_TOKEN_RE = re.compile(r"^sha(?P<bits>256|384|512)-(?P<digest>[A-Za-z0-9+/]+=*)$")
SRI_DIGEST_BYTES = {"256": 32, "384": 48, "512": 64}
ANCHOR_RE = re.compile(r"^&(?P<name>[A-Za-z0-9_-]+)(?:\s+(?P<rest>.*))?$")
ALIAS_RE = re.compile(r"^\*(?P<name>[A-Za-z0-9_-]+)$")
PR_EVENTS = {"pull_request", "pull_request_target"}


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
            integrity = (values.get("integrity") or "").strip()
            if external_script and not _valid_sri(integrity):
                self.findings.append(
                    (
                        self.getpos()[0],
                        "SECHTML004",
                        "external HTTPS script must declare a valid subresource-integrity hash",
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


def _valid_sri(value):
    """Require at least one syntactically-and-length-valid SRI hash token.

    A bare regex-shaped match is not sufficient: the base64 payload must
    strictly decode (correct alphabet/padding) to the exact digest length
    for its named algorithm (32/48/64 bytes for sha256/384/512). The
    ``integrity`` attribute may list multiple space-separated hashes as
    fallbacks per the SRI spec, so any single valid token is accepted.
    """
    for token in value.split():
        match = SRI_TOKEN_RE.match(token)
        if not match:
            continue
        try:
            decoded = base64.b64decode(match.group("digest"), validate=True)
        except (binascii.Error, ValueError):
            continue
        if len(decoded) == SRI_DIGEST_BYTES[match.group("bits")]:
            return True
    return False


def _strip_yaml_comment(value):
    """Remove YAML comments without treating # inside quoted scalars as a comment."""
    quote = None
    escaped = False
    for index, character in enumerate(value):
        if quote == '"' and character == "\\" and not escaped:
            escaped = True
            continue
        if character in {"'", '"'} and not escaped:
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
        elif character == "#" and quote is None and (
            index == 0 or value[index - 1].isspace()
        ):
            return value[:index].rstrip()
        escaped = False
    return value.rstrip()


def _unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


FLOW_MAP_ITEM_RE = re.compile(
    r"(?P<quote>['\"]?)(?P<key>[A-Za-z0-9_-]+)(?P=quote)\s*:\s*(?P<value>.*)"
)


def _strip_anchor(value):
    """Strip a leading YAML anchor tag (e.g. ``&name``) from a scalar value.

    Anchors are resolved *before* testing for flow-mapping brackets or
    scalar permission values so an anchor prefix (``&step {uses: ...}`` or
    ``&perms write-all``) cannot hide dangerous content from the flow- and
    scalar-value checks below. Aliases (``*name``) are intentionally left
    unresolved: this scanner never executes YAML tags, so an alias that
    only ever appears as a bare reference fails closed (still flagged as
    unpinned/ambiguous by the existing checks) rather than being silently
    trusted. Any real dangerous content defined under an anchor's own block
    body is still ordinary indented text and is scanned independently of
    the anchor tag on its parent line.
    """
    match = ANCHOR_RE.match(value)
    if match:
        return (match.group("rest") or "").strip()
    return value


def _flow_mapping_pairs(value):
    """Split a `{key: value, ...}` flow mapping into key/value pairs.

    This is a best-effort splitter (no nested flow collections/commas inside
    quoted scalars are expected in the action metadata this scanner cares
    about); it never executes or trusts the input as code.
    """
    inner = value.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]
    pairs = []
    for item in inner.split(","):
        item = item.strip()
        if not item:
            continue
        match = FLOW_MAP_ITEM_RE.match(item)
        if match:
            pairs.append((match.group("key"), _unquote(match.group("value").strip())))
    return pairs


def _structural_lines(text):
    """Return simple YAML mapping/sequence records without executing YAML tags."""
    records = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = MAPPING_RE.match(line)
        if match:
            indent = len(match.group("indent").expandtabs(8))
            value = _strip_anchor(_strip_yaml_comment(match.group("value")).strip())
            records.append(
                {
                    "line": line_number,
                    "indent": indent,
                    "key": match.group("key"),
                    "value": value,
                }
            )
            if value.startswith("{") and value.endswith("}"):
                for key, item_value in _flow_mapping_pairs(value):
                    records.append(
                        {"line": line_number, "indent": indent + 1, "key": key, "value": item_value}
                    )
            continue
        match = SEQUENCE_RE.match(line)
        if match:
            indent = len(match.group("indent").expandtabs(8))
            value = _strip_anchor(_strip_yaml_comment(match.group("value")).strip())
            records.append(
                {
                    "line": line_number,
                    "indent": indent,
                    "key": None,
                    "value": value,
                }
            )
            if value.startswith("{") and value.endswith("}"):
                for key, item_value in _flow_mapping_pairs(value):
                    records.append(
                        {"line": line_number, "indent": indent + 1, "key": key, "value": item_value}
                    )
    return records


def _event_names(value):
    """Extract event names from scalar, flow-sequence, or flow-mapping values."""
    value = _unquote(value.strip())
    if not value:
        return set()
    if value.startswith("[") and value.endswith("]"):
        return {
            _unquote(item.strip())
            for item in value[1:-1].split(",")
            if item.strip()
        }
    if value.startswith("{") and value.endswith("}"):
        return {
            _unquote(item.split(":", 1)[0].strip())
            for item in value[1:-1].split(",")
            if ":" in item
        }
    return {value}


def _workflow_events(records):
    if not records:
        return set()
    root_indent = min(record["indent"] for record in records)
    events = set()
    for index, record in enumerate(records):
        if record["indent"] != root_indent or record["key"] != "on":
            continue
        events.update(_event_names(record["value"]))
        for child in records[index + 1 :]:
            if child["key"] is None and child["indent"] == record["indent"]:
                events.update(_event_names(child["value"]))
                continue
            if child["indent"] <= record["indent"]:
                break
            if child["key"] is None:
                events.update(_event_names(child["value"]))
            else:
                events.add(child["key"])
    return events


def _permission_value_present(records, keys, values):
    for record in records:
        if record["key"] in keys and _unquote(record["value"]).strip() in values:
            return True
    return False


def _secrets_referenced(text):
    """Detect any reference to the ``secrets`` context anywhere in the file.

    Deliberately conservative/whole-document: rather than trying to parse
    each ``${{ ... }}`` expression and only inspect its contents (which
    requires correctly locating expression boundaries and handling quotes,
    escaping, and multiline literals), this simply looks for a
    case-sensitive standalone `secrets` token anywhere in the raw workflow
    text -- dotted (`secrets.X`), bracketed (`secrets['X']`), passed as a
    function argument (`toJSON(secrets)`), split across lines inside a
    multiline literal or block scalar, or otherwise embedded in braces.
    `secrets` is a reserved GitHub Actions context name, so this can only
    be triggered by an actual reference to it or, rarely, by the literal
    word appearing in an unrelated comment or string -- an acceptable
    false-positive rate for a fail-closed advisory check that must not be
    evadable by any expression-boundary or quoting trick. This is
    deliberately independent of ``${{ }}`` expression parsing/boundary
    detection entirely, so it cannot be defeated by any way of hiding or
    splitting an expression (unterminated quotes, multiline literals,
    bracket/function-call syntax, or embedded braces).
    """
    return bool(SECRETS_WORD_RE.search(text))


def workflow_findings(path):
    text = path.read_text(encoding="utf-8")
    records = _structural_lines(text)
    events = _workflow_events(records)
    findings = []

    if "pull_request_target" in events:
        findings.append((1, "SECWF001", "pull_request_target is not allowed"))

    if _permission_value_present(records, {"permissions"}, {"write-all", "read-all"}):
        findings.append((1, "SECWF002", "permissions must be an explicit least-privilege map"))

    root_indent = min((record["indent"] for record in records), default=0)
    if not any(
        record["indent"] == root_indent and record["key"] == "permissions"
        for record in records
    ):
        findings.append((1, "SECWF006", "workflow must declare top-level permissions"))

    for record in records:
        if record["key"] != "uses":
            continue
        line_number = record["line"]
        reference = _unquote(record["value"])
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

    grants_write = _permission_value_present(
        records, PERMISSION_KEYS, {"write"}
    ) or _permission_value_present(records, {"permissions"}, {"write-all"})

    if events.intersection(PR_EVENTS) and (grants_write or _secrets_referenced(text)):
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
