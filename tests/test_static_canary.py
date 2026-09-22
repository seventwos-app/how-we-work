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


if __name__ == "__main__":
    unittest.main()
