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
proves this end-to-end) — reviews
dependencies when the pull request actually changes one of the manifest or
lockfile names GitHub's dependency graph recognizes (deliberately excluding
the GitHub Actions ecosystem, since action pinning is already enforced by
the workflow-policy check below), and applies dependency-free
workflow-policy and static-HTML checks. Its jobs are intentionally not
required status checks.

Repository administrators should enable GitHub secret scanning and push
protection when the organization plan permits them; Gitleaks is the
deterministic fallback while those settings are disabled. Dependabot
security updates are also currently disabled and may be enabled separately
if this repository later gains package manifests.

The workflow-policy check's pull-request `secrets`-context detection
(`SECWF005`) is deliberately conservative: rather than parsing
`${{ ... }}` expression boundaries and quoting (which can be evaded by
unusual quoting, multiline literals, or expression-splitting tricks), it
scans the whole workflow file's raw text for any case-sensitive,
word-bounded `secrets` token — dotted, bracketed, passed to a function
such as `toJSON(secrets)`, or split across lines. This can rarely flag the
bare word appearing in an unrelated comment or string; that false-positive
risk is an accepted trade-off for a fail-closed check that cannot be
defeated by any way of hiding or splitting an actual context reference.
