import base64
import re
import tempfile
import unittest
from pathlib import Path

from scripts.security.static_canary import html_findings, workflow_findings


class WorkflowPolicyTests(unittest.TestCase):
    def _workflow(self, contents):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "workflow.yml"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_accepts_read_only_pr_workflow_with_sha_pinned_action(self):
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    steps:
      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09
"""
        )
        self.assertEqual([], workflow_findings(path))

    def test_rejects_movable_action_tag(self):
        path = self._workflow(
            "permissions:\n  contents: read\n"
            "jobs:\n  check:\n    steps:\n      - uses: actions/checkout@v5\n"
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF004", rules)

    def test_rejects_pr_workflow_with_write_permissions_or_secrets(self):
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: write
jobs:
  check:
    env:
      TOKEN: ${{ secrets.DEPLOY_TOKEN }}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_rejects_missing_top_level_permissions(self):
        path = self._workflow("on: push\njobs:\n  check:\n    runs-on: ubuntu-latest\n")
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF006", rules)

    def test_rejects_four_space_mapping_pull_request_target(self):
        path = self._workflow(
            """
    on:
        pull_request_target:
    permissions:
        contents: read
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF001", rules)

    def test_rejects_scalar_pull_request_target(self):
        path = self._workflow(
            """
on: pull_request_target
permissions:
  contents: read
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF001", rules)

    def test_inline_event_list_enforces_pr_trust_boundary(self):
        path = self._workflow(
            """
on: [push, pull_request]
permissions:
  contents: write
jobs: {}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_inline_event_list_rejects_pull_request_target(self):
        path = self._workflow(
            """
on: [push, pull_request_target]
permissions:
  contents: read
jobs: {}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF001", rules)

    def test_block_event_list_rejects_pull_request_target(self):
        path = self._workflow(
            """
on:
  - push
  - pull_request_target
permissions:
  contents: read
jobs: {}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF001", rules)

    def test_zero_indent_event_list_enforces_pull_request_target_boundary(self):
        path = self._workflow(
            """
on:
- push
- pull_request_target
permissions:
  contents: write
jobs: {}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF001", rules)
        self.assertIn("SECWF005", rules)

    def test_rejects_quoted_write_all_permission_scalar(self):
        path = self._workflow(
            'on: push\npermissions: "write-all"\njobs: {}\n'
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF002", rules)

    def test_rejects_quoted_write_permission_scalar_on_pr_workflow(self):
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: 'write'
jobs: {}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_rejects_flow_mapping_sequence_item_with_movable_action_tag(self):
        path = self._workflow(
            """
on: push
permissions:
  contents: read
jobs:
  check:
    steps:
      - {uses: actions/checkout@v5}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF004", rules)

    def test_accepts_flow_mapping_sequence_item_with_pinned_action(self):
        path = self._workflow(
            """
on: push
permissions:
  contents: read
jobs:
  check:
    steps:
      - {name: Checkout, uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertNotIn("SECWF004", rules)

    def test_rejects_bracket_notation_secret_reference_on_pr_workflow(self):
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    env:
      TOKEN: ${{ secrets['DEPLOY_TOKEN'] }}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_rejects_tojson_secrets_reference_on_pr_workflow(self):
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    env:
      ALL: ${{ toJSON(secrets) }}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_rejects_multiline_named_step_with_movable_action_tag(self):
        path = self._workflow(
            """
on: push
permissions:
  contents: read
jobs:
  check:
    steps:
      - name: Checkout
        uses: actions/checkout@v5
"""
        )
        findings = workflow_findings(path)
        rules = {finding[1] for finding in findings}
        self.assertIn("SECWF004", rules)
        self.assertIn(9, {finding[0] for finding in findings if finding[1] == "SECWF004"})

    def test_rejects_job_level_movable_reusable_workflow(self):
        path = self._workflow(
            """
on: push
permissions:
  contents: read
jobs:
  delegated:
    uses: owner/repository/.github/workflows/check.yml@main
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF004", rules)

    def test_rejects_anchored_flow_mapping_permissions_bypass(self):
        # An anchor tag on the same line as a flow mapping must not hide the
        # mapping's own keys from the write-permission scan: a PR-triggered
        # workflow granting `contents: write` through an anchored flow
        # mapping must still trip the PR trust-boundary check.
        path = self._workflow(
            """
on:
  pull_request:
permissions: &perms {contents: write}
jobs:
  check:
    steps:
      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_rejects_anchored_flow_mapping_sequence_uses_bypass(self):
        # An anchor tag prefixing a flow-mapping sequence item must not hide
        # its `uses:` key from the action-pinning scan.
        path = self._workflow(
            """
on: push
permissions:
  contents: read
jobs:
  check:
    steps:
      - &step {uses: actions/checkout@v5}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF004", rules)

    def test_accepts_anchored_flow_mapping_sequence_with_pinned_action(self):
        path = self._workflow(
            """
on: push
permissions:
  contents: read
jobs:
  check:
    steps:
      - &step {uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09}
"""
        )
        self.assertEqual([], workflow_findings(path))

    def test_rejects_anchored_scalar_write_all_permission_bypass(self):
        path = self._workflow(
            "permissions: &perms write-all\n"
            "jobs:\n  check:\n    steps:\n"
            "      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09\n"
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF002", rules)

    def test_rejects_secrets_hidden_after_embedded_closing_braces_in_quoted_literal(self):
        # A quoted decoy literal containing a `}}` substring must not let a
        # non-greedy `${{ ... }}` scan truncate before the real secrets use.
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    env:
      TOKEN: ${{ format('{0}}}', secrets.DEPLOY_TOKEN) }}
"""
        )
        rules = {finding[1] for finding in workflow_findings(path)}
        self.assertIn("SECWF005", rules)

    def test_accepts_quoted_closing_braces_literal_without_secrets(self):
        path = self._workflow(
            """
on:
  pull_request:
permissions:
  contents: read
jobs:
  check:
    env:
      LABEL: ${{ format('{0}}}', github.run_id) }}
"""
        )
        self.assertEqual([], workflow_findings(path))


class ManifestDiffPatternTests(unittest.TestCase):
    """Mirrors the grep pattern used by the dependency-review workflow job."""

    PATTERN = (
        r"(^|/)(package\.json|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|"
        r"requirements\.txt|Pipfile|Pipfile\.lock|poetry\.lock|pyproject\.toml|"
        r"setup\.py|go\.mod|go\.sum|Gemfile|Gemfile\.lock|[^/]+\.gemspec|"
        r"Cargo\.toml|Cargo\.lock|pom\.xml|packages\.config|packages\.lock\.json|"
        r"[^/]+\.(csproj|fsproj|vbproj|vcxproj|nuspec)|composer\.json|"
        r"composer\.lock|pubspec\.yaml|pubspec\.lock|Package\.resolved|"
        r"Manifest\.toml|Project\.toml|deno\.json|deno\.jsonc|deno\.lock|"
        r"MODULE\.bazel|MODULE\.bazel\.lock|WORKSPACE|maven_install\.json|"
        r"[^/]+\.MODULE\.bazel)$"
    )

    def _matches(self, relative_path):
        return re.search(self.PATTERN, relative_path) is not None

    def test_matches_previously_missing_manifests(self):
        for name in ("package.json", "Cargo.toml", "composer.json", "go.mod", "pubspec.yaml"):
            with self.subTest(name=name):
                self.assertTrue(self._matches(name))

    def test_matches_nested_lockfiles(self):
        self.assertTrue(self._matches("frontend/package-lock.json"))

    def test_does_not_match_unrelated_files(self):
        for name in ("README.md", ".github/workflows/ci.yml", "src/foo.js"):
            with self.subTest(name=name):
                self.assertFalse(self._matches(name))


class StaticHTMLTests(unittest.TestCase):
    def _html(self, contents):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "index.html"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_accepts_self_contained_script_and_hardened_blank_target(self):
        path = self._html(
            '<script>console.log("local")</script>'
            '<a href="https://example.com" target="_blank" rel="noopener noreferrer">link</a>'
        )
        self.assertEqual([], html_findings(path))

    def test_rejects_unverified_remote_script_and_reverse_tabnabbing(self):
        path = self._html(
            '<script src="//example.com/app.js"></script>'
            '<a href="https://example.com" target="_blank">link</a>'
        )
        rules = {finding[1] for finding in html_findings(path)}
        self.assertEqual({"SECHTML004", "SECHTML005"}, rules)

    def test_rejects_empty_integrity_attribute_on_remote_script(self):
        path = self._html('<script src="https://example.com/app.js" integrity=""></script>')
        rules = {finding[1] for finding in html_findings(path)}
        self.assertIn("SECHTML004", rules)

    def test_accepts_remote_script_with_valid_sri_hash(self):
        path = self._html(
            '<script src="https://example.com/app.js" '
            'integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC" '
            'crossorigin="anonymous"></script>'
        )
        rules = {finding[1] for finding in html_findings(path)}
        self.assertNotIn("SECHTML004", rules)

    def test_rejects_regex_shaped_sri_hash_with_wrong_decoded_length(self):
        # Syntactically matches sha(256|384|512)-<base64> but the base64
        # payload decodes to the wrong number of bytes for the declared
        # algorithm, so it must still be rejected as invalid.
        wrong_length = base64.b64encode(b"x" * 16).decode()
        path = self._html(
            f'<script src="https://example.com/app.js" '
            f'integrity="sha256-{wrong_length}"></script>'
        )
        rules = {finding[1] for finding in html_findings(path)}
        self.assertIn("SECHTML004", rules)

    def test_accepts_correctly_sized_sha256_sri_hash(self):
        correct_length = base64.b64encode(b"x" * 32).decode()
        path = self._html(
            f'<script src="https://example.com/app.js" '
            f'integrity="sha256-{correct_length}"></script>'
        )
        rules = {finding[1] for finding in html_findings(path)}
        self.assertNotIn("SECHTML004", rules)

    def test_rejects_sri_hash_with_invalid_base64_characters(self):
        path = self._html(
            '<script src="https://example.com/app.js" '
            'integrity="sha256-not_valid_base64!!"></script>'
        )
        rules = {finding[1] for finding in html_findings(path)}
        self.assertIn("SECHTML004", rules)


if __name__ == "__main__":
    unittest.main()
