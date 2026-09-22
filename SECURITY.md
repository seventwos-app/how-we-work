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
end-to-end) — and reviews dependencies on every pull request, rather than
gating that step on a hand-maintained list of manifest/lockfile names.
`dependency-review-action` is itself a no-op when a pull request touches
no manifest it recognizes, so running it unconditionally costs nothing
in practice and avoids silently losing coverage if GitHub's dependency
graph later adds or renames a supported ecosystem (e.g. a new
Gradle/Swift manifest) that a hand-maintained gate hadn't been updated
for. All third-party actions it uses are pinned to immutable commit
SHAs. Its jobs are intentionally **advisory**, not required status
checks, and do not modify branch protection.

This canary deliberately covers only secret scanning and dependency
review; it does not attempt to enforce workflow-permission or
trigger-event policy (e.g. rejecting `pull_request_target` or write
permissions on untrusted triggers) from within this repository. Earlier
iterations of *this pull request* added such checks as grep-based
scripts — first a standalone Python YAML scanner
(`scripts/security/static_canary.py`), later inline additions to
`.github/workflows/ci.yml`'s pre-existing `security` job (a repo-wide "no
write permissions" grep, then a trusted-file allowlist for
`graphify.yml` / `graphify-catchup.yml`) — but any such policy
enforcement is itself just more pull-request-controlled YAML/shell that
a sufficiently motivated pull request could target, weaken, or evade in
ways a repository-local reviewer may not catch (as several rounds of
review on this PR demonstrated), and a workflow change to `ci.yml`,
`graphify.yml`, or `graphify-catchup.yml` cannot meaningfully enforce
anything about *itself*. All of those additions introduced by this pull
request have been removed.

`ci.yml`'s `security` job predates this pull request and already
contained a narrow, standalone check that workflows avoid the
`pull_request_target` trigger; that pre-existing check is unchanged and
still runs. Its broader "no write permissions anywhere in
`.github/workflows`" grep — also pre-existing in `ci.yml` before this
pull request touched it — was dropped rather than restored, because it
is structurally incompatible with this repository's own legitimate
automation: `graphify.yml` and `graphify-catchup.yml` are
push/`workflow_dispatch`-triggered (never PR-triggered) and need
`contents`/`pull-requests: write` to open their own update PRs, so a
blanket write-permission grep can never pass alongside them without
either false-failing on trusted automation or growing into exactly the
kind of trigger-aware allowlist logic this repository has chosen not to
maintain. `graphify.yml` and `graphify-catchup.yml` themselves are
unchanged by this PR. These pre-existing `ci.yml` checks are partial,
grep-based, and not a substitute for the trigger-aware policy this PR
declined to build in-repo — they are noted here only to avoid
overstating what was removed, not as a claim that they are sufficient.
Enforcing workflow-permission/trigger policy credibly requires either
GitHub's own required-workflow/ruleset features or a review process
anchored outside this repository, not a repository-local script running
inside a PR-controlled workflow. Until an organization-level required
workflow or ruleset is in place, this is a known limitation: a pull
request that also modifies this repository's
own workflow files (including their permissions or triggers) is only
caught by ordinary code review, not by an automated check.

Repository administrators should enable GitHub secret scanning and push
protection when the organization plan permits them; Gitleaks is the
deterministic fallback while those settings are disabled. Dependabot
security updates are also currently disabled and may be enabled separately
if this repository later gains package manifests. Administrators should
also consider adopting an organization-level required workflow or
repository ruleset to enforce workflow-permission/trigger-event policy
outside of pull-request-controlled code, since this repository's own
canary cannot credibly do so.
