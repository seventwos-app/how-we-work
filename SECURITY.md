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

The `Security Canary (advisory)` workflow runs on pull requests and pushes
to `main`. It uses read-only permissions, cancels superseded runs, disables
checkout credential persistence, scans Git history with a checksum-verified
`gitleaks` CLI download (no gitleaks-action license dependency) against a
checksum-verified copy of gitleaks' own pinned default ruleset and an empty
ignore-path fetched outside the pull request's checkout, additionally
deleting any `.gitleaks.toml`/`.gitleaksignore` left in the working-tree
checkout before scanning (gitleaks always also checks that path even when
`--gitleaks-ignore-path` points elsewhere) — so a pull request cannot
supply its own config, ignore file, or inline `gitleaks:allow` comment to
weaken the scan of its own diff (`tests/security/test_gitleaks_ignore_regression.sh`
proves this end-to-end) — and reviews dependencies when the pull request
actually changes one of the manifest or lockfile names GitHub's dependency
graph recognizes. Its jobs are intentionally not required status checks.

This canary deliberately covers only secret scanning and dependency
review. It does not implement custom workflow-policy or static-HTML
parsing/linting in this repository: a central, trusted baseline is
expected to enforce those checks (e.g. organization-wide policy tooling
maintained outside pull-request-controlled code), rather than a
repository-local script that a pull request could itself attempt to
influence. `.github/workflows/ci.yml`'s existing lightweight `security`
job continues to run as a required status check, unchanged in spirit by
this canary: it still rejects any `pull_request_target` trigger
repo-wide, and it still requires every workflow to stay read-only,
*except* an explicit, exact allowlist (currently `graphify.yml` and
`graphify-catchup.yml`) that is separately asserted, in the same job,
to have no `pull_request`/`pull_request_target` trigger — those two
workflows only ever run on `push`/`schedule`/`workflow_dispatch`, so
their `contents: write`/`pull-requests: write` permissions (needed to
open their own automated graph-update PRs) are never exercised against
untrusted, pull-request-controlled input.
(`tests/security/test_ci_write_permission_policy.sh` regresses that
policy against fixture workflows.)

Repository administrators should enable GitHub secret scanning and push
protection when the organization plan permits them; Gitleaks is the
deterministic fallback while those settings are disabled. Dependabot
security updates are also currently disabled and may be enabled separately
if this repository later gains package manifests.
