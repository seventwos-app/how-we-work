#!/usr/bin/env python3
"""Provenance record validator (schema v0.1).

Validates .seventwos/provenance.json against the minimal repository
provenance convention documented in plans/repository-provenance.md:

  workspace intent -> human direction -> agent-assisted change -> review
  -> source outcome

No third-party dependencies: this parses and checks JSON using only the
Python standard library. Error messages intentionally report only the
offending JSON *path* and a stable *rule id* -- never the offending value
-- so a validation failure is safe to print in CI logs or paste into an
issue even if a record accidentally contains sensitive text.

Modes:
  --file PATH   Validate a single provenance record file (default:
                .seventwos/provenance.json). Exit non-zero on any
                violation. This is what CI runs.

Rule ids:
  PROV001  required field is missing
  PROV002  field has the wrong JSON type
  PROV003  field value is not one of the allowed enum values / patterns
  PROV004  field name is not part of the schema (unsupported field)
  PROV005  field name matches a disallowed sensitive-data pattern
"""
import argparse
import json
import re
import sys
from collections import namedtuple
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = REPO_ROOT / ".seventwos" / "provenance.json"

DISCLOSURE_CLASSES = {"public", "internal", "restricted"}
AGENT_INVOLVEMENT_VALUES = {"none", "assisted", "generated-and-reviewed"}
OUTCOME_ORIGINS = {"commit", "pull_request", "release"}

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")

TOP_LEVEL_REQUIRED = {"schema_version", "repository", "disclosure_class", "entries"}
TOP_LEVEL_ALLOWED = TOP_LEVEL_REQUIRED

ENTRY_REQUIRED = {
    "id",
    "intent",
    "human_direction",
    "agent_involvement",
    "review",
    "outcome",
}
ENTRY_ALLOWED = ENTRY_REQUIRED | {"disclosure_class"}

OUTCOME_REQUIRED = {"origin", "reference"}
OUTCOME_ALLOWED = OUTCOME_REQUIRED

# Field *names* (not values) that must never appear anywhere in a
# provenance record, because they signal private workspace/session
# identifiers, raw prompts, customer data, or credentials rather than the
# generalized, public-safe intent/direction/review fields the schema
# defines.
SENSITIVE_FIELD_NAMES = {
    "workspace_id",
    "workspace",
    "prompt",
    "prompts",
    "conversation",
    "conversation_id",
    "session_id",
    "customer",
    "customer_name",
    "customer_id",
    "email",
    "phone",
    "address",
    "ip_address",
    "api_key",
    "secret",
    "token",
    "password",
    "private_key",
}

Violation = namedtuple("Violation", ["path", "rule_id", "message"])


def _sorted(values):
    return sorted(values)


def _scan_sensitive_fields(node, path, violations):
    """Recursively flag disallowed field names anywhere in the document.

    Only the *key* is inspected and reported -- never the associated
    value -- so this never leaks record content into a violation message.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}" if path else key
            if key.lower() in SENSITIVE_FIELD_NAMES:
                violations.append(
                    Violation(
                        child_path,
                        "PROV005",
                        "field name matches a disallowed sensitive-data pattern",
                    )
                )
            _scan_sensitive_fields(value, child_path, violations)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            _scan_sensitive_fields(item, f"{path}[{idx}]", violations)


def _require_type(value, expected_types, path, violations):
    if not isinstance(value, expected_types):
        violations.append(Violation(path, "PROV002", "field has the wrong JSON type"))
        return False
    return True


def _check_non_empty_string(value, path, violations):
    if not _require_type(value, str, path, violations):
        return
    if not value.strip():
        violations.append(Violation(path, "PROV003", "field must be a non-empty string"))


def _check_outcome(outcome, path, violations):
    if not _require_type(outcome, dict, path, violations):
        return
    for key in OUTCOME_REQUIRED:
        if key not in outcome:
            violations.append(Violation(f"{path}.{key}", "PROV001", "required field is missing"))
    for key in outcome:
        if key not in OUTCOME_ALLOWED:
            violations.append(
                Violation(f"{path}.{key}", "PROV004", "field name is not part of the schema")
            )
    if "origin" in outcome:
        origin = outcome["origin"]
        if not (isinstance(origin, str) and origin in OUTCOME_ORIGINS):
            violations.append(
                Violation(
                    f"{path}.origin",
                    "PROV003",
                    f"field must be one of {_sorted(OUTCOME_ORIGINS)}",
                )
            )
    if "reference" in outcome:
        _check_non_empty_string(outcome["reference"], f"{path}.reference", violations)


def _check_entry(entry, path, violations):
    if not _require_type(entry, dict, path, violations):
        return
    for key in ENTRY_REQUIRED:
        if key not in entry:
            violations.append(Violation(f"{path}.{key}", "PROV001", "required field is missing"))
    for key in entry:
        if key not in ENTRY_ALLOWED:
            violations.append(
                Violation(f"{path}.{key}", "PROV004", "field name is not part of the schema")
            )

    for key in ("id", "intent", "human_direction", "review"):
        if key in entry:
            _check_non_empty_string(entry[key], f"{path}.{key}", violations)

    if "agent_involvement" in entry:
        value = entry["agent_involvement"]
        if not (isinstance(value, str) and value in AGENT_INVOLVEMENT_VALUES):
            violations.append(
                Violation(
                    f"{path}.agent_involvement",
                    "PROV003",
                    f"field must be one of {_sorted(AGENT_INVOLVEMENT_VALUES)}",
                )
            )

    if "disclosure_class" in entry:
        value = entry["disclosure_class"]
        if not (isinstance(value, str) and value in DISCLOSURE_CLASSES):
            violations.append(
                Violation(
                    f"{path}.disclosure_class",
                    "PROV003",
                    f"field must be one of {_sorted(DISCLOSURE_CLASSES)}",
                )
            )

    if "outcome" in entry:
        _check_outcome(entry["outcome"], f"{path}.outcome", violations)


def validate(data):
    """Return a list of Violation objects for a decoded provenance document."""
    violations = []

    if not isinstance(data, dict):
        return [Violation("$", "PROV002", "document root must be a JSON object")]

    for key in TOP_LEVEL_REQUIRED:
        if key not in data:
            violations.append(Violation(key, "PROV001", "required field is missing"))

    for key in data:
        if key not in TOP_LEVEL_ALLOWED:
            violations.append(
                Violation(key, "PROV004", "field name is not part of the schema")
            )

    if "schema_version" in data:
        value = data["schema_version"]
        if value != "0.1":
            violations.append(
                Violation("schema_version", "PROV003", "field must equal '0.1'")
            )

    if "repository" in data:
        value = data["repository"]
        if not (isinstance(value, str) and REPOSITORY_RE.match(value)):
            violations.append(
                Violation(
                    "repository",
                    "PROV003",
                    "field must match the 'owner/repo' pattern",
                )
            )

    if "disclosure_class" in data:
        value = data["disclosure_class"]
        if not (isinstance(value, str) and value in DISCLOSURE_CLASSES):
            violations.append(
                Violation(
                    "disclosure_class",
                    "PROV003",
                    f"field must be one of {_sorted(DISCLOSURE_CLASSES)}",
                )
            )

    if "entries" in data:
        entries = data["entries"]
        if not _require_type(entries, list, "entries", violations):
            entries = []
        seen_ids = set()
        for idx, entry in enumerate(entries):
            entry_path = f"entries[{idx}]"
            _check_entry(entry, entry_path, violations)
            if isinstance(entry, dict):
                entry_id = entry.get("id")
                if isinstance(entry_id, str) and entry_id:
                    if entry_id in seen_ids:
                        violations.append(
                            Violation(
                                f"{entry_path}.id",
                                "PROV003",
                                "field duplicates another entry's id",
                            )
                        )
                    seen_ids.add(entry_id)

    _scan_sensitive_fields(data, "", violations)

    return violations


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Provenance record validator (schema v0.1)")
    parser.add_argument(
        "--file",
        default=str(DEFAULT_PATH),
        help="path to the provenance record to validate (default: .seventwos/provenance.json)",
    )
    args = parser.parse_args(argv)

    path = Path(args.file)
    try:
        data = load(path)
    except FileNotFoundError:
        print(f"FAIL {path}: [PROV000] file does not exist")
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL {path}: [PROV000] file is not valid JSON (line {exc.lineno}, column {exc.colno})")
        return 1

    violations = validate(data)
    if violations:
        for v in violations:
            print(f"FAIL {path}: [{v.rule_id}] {v.path}: {v.message}")
        print(f"\nprovenance-validate: {len(violations)} violation(s) in {path}.")
        return 1

    print(f"OK   {path}")
    print("\nprovenance-validate: record conforms to schema v0.1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
