#!/usr/bin/env python3
"""Focused unit tests for scripts/okf/validate_okf_markdown.py.

Run with: python -m unittest discover -s tests -v

No third-party test dependencies (stdlib unittest only), matching the
validator's own no-third-party-dependency stance.
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "okf"))

import validate_okf_markdown as okf  # noqa: E402


def write(tmp_path, name, content):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class ConceptFrontmatterTests(unittest.TestCase):
    def test_missing_frontmatter_fails(self):
        text = "# No frontmatter\n\nJust a body.\n"
        self.assertEqual(
            okf.check_file(self._write("concept.md", text)),
            ["missing YAML frontmatter (no leading '---' block)"],
        )

    def test_missing_closing_delimiter_is_malformed(self):
        text = "---\ntype: Note\n\n# Body\n"
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(any("malformed frontmatter" in v for v in violations))

    def test_missing_type_fails(self):
        text = "---\ntitle: Untyped\n---\n\n# Body\n"
        violations = okf.check_file(self._write("concept.md", text))
        self.assertIn(
            "frontmatter present but missing required non-empty 'type' field",
            violations,
        )

    def test_empty_type_fails(self):
        text = '---\ntype: ""\n---\n\n# Body\n'
        violations = okf.check_file(self._write("concept.md", text))
        self.assertIn(
            "frontmatter present but missing required non-empty 'type' field",
            violations,
        )

    def test_minimal_valid_concept_passes(self):
        text = "---\ntype: Vision\n---\n\n# Body\n"
        self.assertEqual(okf.check_file(self._write("concept.md", text)), [])

    def test_tags_must_be_a_list(self):
        text = "---\ntype: Vision\ntags: heuristic\n---\n\nBody\n"
        violations = okf.check_file(self._write("concept.md", text))
        self.assertIn("'tags' must be a YAML list", violations)

    def test_tags_flow_list_passes(self):
        text = "---\ntype: Vision\ntags: [heuristic, agents]\n---\n\nBody\n"
        self.assertEqual(okf.check_file(self._write("concept.md", text)), [])

    def test_status_must_be_known_value(self):
        text = "---\ntype: Vision\nstatus: wip\n---\n\nBody\n"
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(any(v.startswith("'status' must be one of") for v in violations))

    def test_generated_requires_by(self):
        text = "---\ntype: Vision\ngenerated: { at: 2026-06-20T22:53:05Z }\n---\n\nBody\n"
        violations = okf.check_file(self._write("concept.md", text))
        self.assertIn("'generated.by' is required and must be non-empty", violations)

    def test_generated_flow_mapping_passes(self):
        text = (
            "---\ntype: Vision\n"
            "generated: { by: human:ahormati, at: 2026-06-20T22:53:05Z }\n"
            "---\n\nBody\n"
        )
        self.assertEqual(okf.check_file(self._write("concept.md", text)), [])

    def test_verified_bare_mapping_is_one_element_list(self):
        text = (
            "---\ntype: Vision\n"
            "verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }\n"
            "---\n\nBody\n"
        )
        self.assertEqual(okf.check_file(self._write("concept.md", text)), [])

    def test_verified_list_entry_missing_by_fails(self):
        text = (
            "---\ntype: Vision\n"
            "verified:\n"
            "  - at: 2026-06-25T09:00:00Z\n"
            "---\n\nBody\n"
        )
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(
            any("each 'verified' entry must be a mapping" in v for v in violations)
        )

    def _write(self, name, content):
        return write(self.tmp_dir, name, content)

    def setUp(self):
        import tempfile

        self._tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmpdir_obj.name)
        self._orig_root = okf.REPO_ROOT
        okf.REPO_ROOT = self.tmp_dir

    def tearDown(self):
        okf.REPO_ROOT = self._orig_root
        self._tmpdir_obj.cleanup()


class SourcesAndFootnoteTests(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmpdir_obj.name)
        self._orig_root = okf.REPO_ROOT
        okf.REPO_ROOT = self.tmp_dir

    def tearDown(self):
        okf.REPO_ROOT = self._orig_root
        self._tmpdir_obj.cleanup()

    def _write(self, name, content):
        return write(self.tmp_dir, name, content)

    def test_source_missing_resource_fails(self):
        text = (
            "---\ntype: Metric\n"
            "sources:\n"
            "  - id: ga4-schema\n"
            "    title: GA4 schema\n"
            "---\n\nBody\n"
        )
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(
            any("missing a required non-empty 'resource'" in v for v in violations)
        )

    def test_source_with_resource_passes(self):
        text = (
            "---\ntype: Metric\n"
            "sources:\n"
            "  - id: ga4-schema\n"
            "    resource: https://example.com/schema\n"
            "---\n\nBody\n"
        )
        self.assertEqual(okf.check_file(self._write("concept.md", text)), [])

    def test_footnote_without_sources_fails(self):
        text = (
            "---\ntype: Metric\n---\n\n"
            "The table is sharded daily.[^ga4-schema]\n\n"
            "[^ga4-schema]: GA4 schema\n"
        )
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(any("no 'sources[].id'" in v for v in violations))

    def test_footnote_matching_source_id_passes(self):
        text = (
            "---\ntype: Metric\n"
            "sources:\n"
            "  - id: ga4-schema\n"
            "    resource: https://example.com/schema\n"
            "---\n\n"
            "The table is sharded daily.[^ga4-schema]\n\n"
            "[^ga4-schema]: GA4 schema\n"
        )
        self.assertEqual(okf.check_file(self._write("concept.md", text)), [])

    def test_footnote_not_matching_any_source_id_fails(self):
        text = (
            "---\ntype: Metric\n"
            "sources:\n"
            "  - id: ga4-schema\n"
            "    resource: https://example.com/schema\n"
            "---\n\n"
            "The table is sharded daily.[^other-id]\n\n"
            "[^other-id]: Something else\n"
        )
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(any("do not correspond to any 'sources[].id'" in v for v in violations))

    def test_duplicate_source_ids_fail(self):
        text = (
            "---\ntype: Metric\n"
            "sources:\n"
            "  - id: dup\n"
            "    resource: https://example.com/one\n"
            "  - id: dup\n"
            "    resource: https://example.com/two\n"
            "---\n\nBody\n"
        )
        violations = okf.check_file(self._write("concept.md", text))
        self.assertTrue(any("duplicate id 'dup'" in v for v in violations))


class ReservedFileTests(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmpdir_obj.name)
        self._orig_root = okf.REPO_ROOT
        okf.REPO_ROOT = self.tmp_dir

    def tearDown(self):
        okf.REPO_ROOT = self._orig_root
        self._tmpdir_obj.cleanup()

    def _write(self, name, content):
        return write(self.tmp_dir, name, content)

    def test_root_index_with_only_okf_version_passes(self):
        text = '---\nokf_version: "0.2"\n---\n\n# Index\n'
        self.assertEqual(okf.check_file(self._write("index.md", text)), [])

    def test_root_index_missing_okf_version_fails(self):
        text = "# Index\n\nno frontmatter here\n"
        violations = okf.check_file(self._write("index.md", text))
        self.assertTrue(any("must carry an 'okf_version'" in v for v in violations))

    def test_root_index_with_extra_keys_fails(self):
        text = '---\nokf_version: "0.2"\ntitle: Bundle\n---\n\n# Index\n'
        violations = okf.check_file(self._write("index.md", text))
        self.assertTrue(any("may contain only 'okf_version'" in v for v in violations))

    def test_subdirectory_index_must_not_have_frontmatter(self):
        text = '---\nokf_version: "0.2"\n---\n\n# Sub Index\n'
        violations = okf.check_file(self._write("sub/index.md", text))
        self.assertTrue(any("only the bundle-root index.md may" in v for v in violations))

    def test_subdirectory_index_without_frontmatter_passes(self):
        text = "# Sub Index\n\n* [Concept](concept.md)\n"
        self.assertEqual(okf.check_file(self._write("sub/index.md", text)), [])

    def test_log_with_frontmatter_fails(self):
        text = "---\ntype: Log\n---\n\n# Update Log\n"
        violations = okf.check_file(self._write("log.md", text))
        self.assertEqual(violations, ["log.md must not have YAML frontmatter"])

    def test_log_without_frontmatter_passes(self):
        text = "# Update Log\n\n## 2026-01-01\n* **Init**: Started.\n"
        self.assertEqual(okf.check_file(self._write("log.md", text)), [])


class RepoBundleTests(unittest.TestCase):
    """Guards against regressions on the tracked bundle itself."""

    def test_assistant_tooling_directories_are_excluded(self):
        path = REPO_ROOT / ".github" / "agents" / "example.agent.md"
        self.assertTrue(okf.is_excluded(path))

    def test_whole_bundle_conforms(self):
        clean = True
        offenders = []
        for path in okf.iter_markdown_files():
            violations = okf.check_file(path)
            if violations:
                clean = False
                offenders.append((path, violations))
        self.assertTrue(clean, msg=f"non-conformant files: {offenders}")


if __name__ == "__main__":
    unittest.main()
