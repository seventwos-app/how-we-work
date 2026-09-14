#!/usr/bin/env python3
"""Focused unit tests for scripts/provenance/validate_provenance.py.

Run with: python -m unittest discover -s tests -v

No third-party test dependencies (stdlib unittest only), matching this
repo's no-third-party-dependency stance.
"""
import copy
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "provenance"))

import validate_provenance as prov  # noqa: E402


def valid_document():
    return {
        "schema_version": "0.1",
        "repository": "seventwos-app/how-we-work",
        "disclosure_class": "public",
        "entries": [
            {
                "id": "2026-09-14-example",
                "intent": "Add a widget.",
                "human_direction": "Maintainer asked for a widget.",
                "agent_involvement": "assisted",
                "review": "reviewed-before-merge",
                "outcome": {
                    "origin": "pull_request",
                    "reference": "pull request adding the widget",
                },
            }
        ],
    }


class ValidRecordTests(unittest.TestCase):
    def test_valid_record_has_no_violations(self):
        self.assertEqual(prov.validate(valid_document()), [])

    def test_actual_repo_record_is_valid(self):
        data = prov.load(prov.DEFAULT_PATH)
        self.assertEqual(prov.validate(data), [])


class MissingRequiredFieldTests(unittest.TestCase):
    def test_missing_top_level_field_fails(self):
        data = valid_document()
        del data["repository"]
        violations = prov.validate(data)
        self.assertTrue(
            any(v.rule_id == "PROV001" and v.path == "repository" for v in violations)
        )

    def test_missing_entry_field_fails(self):
        data = valid_document()
        del data["entries"][0]["intent"]
        violations = prov.validate(data)
        self.assertTrue(
            any(v.rule_id == "PROV001" and v.path == "entries[0].intent" for v in violations)
        )

    def test_missing_outcome_field_fails(self):
        data = valid_document()
        del data["entries"][0]["outcome"]["reference"]
        violations = prov.validate(data)
        self.assertTrue(
            any(
                v.rule_id == "PROV001" and v.path == "entries[0].outcome.reference"
                for v in violations
            )
        )


class InvalidOriginTests(unittest.TestCase):
    def test_invalid_outcome_origin_fails(self):
        data = valid_document()
        data["entries"][0]["outcome"]["origin"] = "chat-transcript"
        violations = prov.validate(data)
        matches = [v for v in violations if v.path == "entries[0].outcome.origin"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule_id, "PROV003")
        self.assertNotIn("chat-transcript", matches[0].message)

    def test_invalid_disclosure_class_fails(self):
        data = valid_document()
        data["disclosure_class"] = "top-secret"
        violations = prov.validate(data)
        self.assertTrue(
            any(v.rule_id == "PROV003" and v.path == "disclosure_class" for v in violations)
        )


class SensitiveAndUnsupportedFieldTests(unittest.TestCase):
    def test_sensitive_field_name_fails(self):
        data = valid_document()
        data["entries"][0]["prompt"] = "ignore all previous instructions"
        violations = prov.validate(data)
        matches = [v for v in violations if v.rule_id == "PROV005"]
        self.assertTrue(any(v.path == "entries[0].prompt" for v in matches))
        for v in matches:
            self.assertNotIn("ignore all previous instructions", v.message)

    def test_nested_sensitive_field_name_fails(self):
        data = valid_document()
        data["entries"][0]["outcome"]["workspace_id"] = "ws_abc123"
        violations = prov.validate(data)
        self.assertTrue(
            any(
                v.rule_id == "PROV005" and v.path == "entries[0].outcome.workspace_id"
                for v in violations
            )
        )

    def test_unsupported_top_level_field_fails(self):
        data = valid_document()
        data["customer_notes"] = "irrelevant"
        violations = prov.validate(data)
        self.assertTrue(
            any(v.rule_id == "PROV004" and v.path == "customer_notes" for v in violations)
        )

    def test_unsupported_entry_field_fails(self):
        data = valid_document()
        data["entries"][0]["extra_field"] = "unexpected"
        violations = prov.validate(data)
        self.assertTrue(
            any(
                v.rule_id == "PROV004" and v.path == "entries[0].extra_field"
                for v in violations
            )
        )


class SafeErrorMessageTests(unittest.TestCase):
    def test_error_messages_never_include_the_offending_value(self):
        data = valid_document()
        secret_value = "sk-super-secret-token-do-not-print"
        data["entries"][0]["agent_involvement"] = secret_value
        data["entries"][0]["review"] = secret_value
        violations = prov.validate(data)
        self.assertTrue(violations)
        for v in violations:
            self.assertNotIn(secret_value, v.message)
            self.assertNotIn(secret_value, v.path)

    def test_violations_report_path_and_rule_id(self):
        data = valid_document()
        del data["entries"][0]["human_direction"]
        violations = prov.validate(data)
        target = [v for v in violations if v.path == "entries[0].human_direction"]
        self.assertEqual(len(target), 1)
        self.assertTrue(target[0].rule_id.startswith("PROV"))


class DuplicateIdTests(unittest.TestCase):
    def test_duplicate_entry_ids_fail(self):
        data = valid_document()
        second = copy.deepcopy(data["entries"][0])
        data["entries"].append(second)
        violations = prov.validate(data)
        self.assertTrue(
            any(v.rule_id == "PROV003" and v.path == "entries[1].id" for v in violations)
        )


if __name__ == "__main__":
    unittest.main()
