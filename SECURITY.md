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
ignore-path fetched outside the pull request's checkout — so a pull request
cannot supply its own `.gitleaks.toml`/`.gitleaksignore` or inline
`gitleaks:allow` comment to weaken the scan of its own diff — reviews
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
