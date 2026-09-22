---
type: Policy
title: Security Reporting
description: How to report security vulnerabilities in this repository.
tags: [security]
---

# Reporting a Vulnerability

If you find a security vulnerability in this repository, please
[report it privately through GitHub Security Advisories](https://github.com/seventwos-app/how-we-work/security/advisories/new).

Do not disclose security vulnerabilities in public issues.

## Advisory Security Canary

The `Security Canary (advisory)` workflow (`.github/workflows/security-canary.yml`)
runs on pull requests and pushes to `main`. It uses read-only permissions,
cancels superseded runs, disables checkout credential persistence, scans
Git history with a checksum-verified `gitleaks` CLI download (no
gitleaks-action license dependency) against a checksum-verified copy of
gitleaks' own pinned default ruleset and an empty ignore-path fetched
outside the pull request's checkout, additionally deleting any
`.gitleaks.toml`/`.gitleaksignore` left in the working-tree checkout
before scanning (gitleaks always also checks that path even when
`--gitleaks-ignore-path` points elsewhere) — so a pull request cannot
supply its own config, ignore file, or inline `gitleaks:allow` comment to
weaken the scan of its own diff
(`tests/security/test_gitleaks_ignore_regression.sh` proves this
end-to-end) — and reviews dependencies when the pull request actually
changes one of the manifest or lockfile names GitHub's dependency graph
recognizes. All third-party actions it uses are pinned to immutable
commit SHAs. Its jobs are intentionally **advisory**, not required status
checks, and do not modify branch protection.

This canary deliberately covers only secret scanning and dependency
review; it does not attempt to enforce workflow-permission or
trigger-event policy (e.g. rejecting `pull_request_target` or write
permissions on untrusted triggers) from within this repository. An
earlier iteration of this change added such a check as a grep-based
script inside `.github/workflows/ci.yml`, but any policy enforcement
implemented as a workflow step is itself just more pull-request-controlled
YAML/shell that a sufficiently motivated pull request could target,
weaken, or evade in ways a repository-local reviewer may not catch (as
several rounds of review on this PR demonstrated) — and a workflow
change to `ci.yml`, `graphify.yml`, or `graphify-catchup.yml` cannot
meaningfully enforce anything about *itself*. That check has been
removed; `ci.yml`, `graphify.yml`, and `graphify-catchup.yml` are
unchanged by this PR. Enforcing workflow-permission/trigger policy
credibly requires either GitHub's own required-workflow/ruleset
features or a review process anchored outside this repository, not a
repository-local script running inside a PR-controlled workflow. Until
an organization-level required workflow or ruleset is in place, this is
a known limitation: a pull request that also modifies this repository's
own workflow files is only caught by ordinary code review, not by an
automated check.

Repository administrators should enable GitHub secret scanning and push
protection when the organization plan permits them; Gitleaks is the
deterministic fallback while those settings are disabled. Dependabot
security updates are also currently disabled and may be enabled separately
if this repository later gains package manifests. Administrators should
also consider adopting an organization-level required workflow or
repository ruleset to enforce workflow-permission/trigger-event policy
outside of pull-request-controlled code, since this repository's own
canary cannot credibly do so.
