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

The `Gitleaks Secret-Scan Canary (advisory)` workflow
(`.github/workflows/security-canary.yml`) runs on pull requests and
pushes to `main`. It uses read-only permissions, cancels superseded
runs, disables checkout credential persistence, and scans Git history
with a checksum-verified `gitleaks` CLI download (no gitleaks-action
license dependency) against a checksum-verified copy of gitleaks' own
pinned default ruleset and an empty ignore-path fetched outside the
pull request's checkout, additionally deleting any
`.gitleaks.toml`/`.gitleaksignore` left in the working-tree checkout
before scanning (gitleaks always also checks that path even when
`--gitleaks-ignore-path` points elsewhere) — so a pull request cannot
supply its own config, ignore file, or inline `gitleaks:allow` comment to
weaken the scan of its own diff
(`tests/security/test_gitleaks_ignore_regression.sh` proves this
end-to-end). All third-party actions it uses are pinned to immutable
commit SHAs. Its job is intentionally **advisory**, not a required
status check, and does not modify branch protection.

**Dependency review is not currently available and is not run.** An
earlier version of this canary included a `dependency-review` job using
`actions/dependency-review-action`, but that action failed outright with
`Dependency review is not supported on this repository. Please ensure
that Dependency graph is enabled` — confirmed independently by probing
the same `dependency-graph/compare` REST endpoint the action calls,
which returns HTTP 403 for this repository. GitHub's Dependency Graph
feature itself is disabled or unsupported here, which the workflow
cannot enable or work around from inside a PR-controlled checkout; no
amount of conditional logic in this repository turns that into a
working scan, and treating the resulting no-op as a passing check would
misrepresent an operational gap as a clean result. The job has been
removed entirely rather than papered over with `continue-on-error` or a
silent skip: **dependency review is a known, explicitly blocked gap in
this repository's security coverage until an administrator enables
Dependency Graph** (see the administrator follow-ups below). Any
process reconciling this repository's security posture (this canary,
manual review, or an external dashboard) should treat "dependency review
coverage" as absent, not as advisory-passing, until that setting changes.

This canary deliberately covers only secret scanning; it does not
attempt to enforce workflow-permission or trigger-event policy (e.g.
rejecting `pull_request_target` or write permissions on untrusted
triggers) from within this repository. Earlier iterations of *this pull
request* added such checks as grep-based scripts — first a standalone
Python YAML scanner (`scripts/security/static_canary.py`), later inline
additions to `.github/workflows/ci.yml`'s pre-existing `security` job (a
repo-wide "no write permissions" grep, then a trusted-file allowlist for
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
deterministic fallback while those settings are disabled. Dependency
review cannot run at all until an administrator enables GitHub's
**Dependency Graph** for this repository (Settings > Security > Code
security), which is required before `actions/dependency-review-action`
can function; Dependabot security updates should be considered alongside
it once this repository gains package manifests. Administrators should
also consider adopting an organization-level required workflow or
repository ruleset to enforce workflow-permission/trigger-event policy
outside of pull-request-controlled code, since this repository's own
canary cannot credibly do so.
