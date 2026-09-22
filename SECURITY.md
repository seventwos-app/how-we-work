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
`gitleaks` CLI download (no gitleaks-action license dependency), reviews
dependencies when the pull request actually changes a supported manifest,
and applies dependency-free workflow-policy and static-HTML checks. Its
jobs are intentionally not required status checks.

Repository administrators should enable GitHub secret scanning and push
protection when the organization plan permits them; Gitleaks is the
deterministic fallback while those settings are disabled. Dependabot
security updates are also currently disabled and may be enabled separately
if this repository later gains package manifests.
