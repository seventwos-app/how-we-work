# Update Log

## 2026-09-14 (2)
* **Plan**: Replaced the [Repository Provenance](plans/repository-provenance.md) plan with a practical MVP: a minimal, dependency-free `.seventwos/provenance.json` (schema v0.1) capturing intent, human direction, agent involvement, review, and source outcome; three disclosure classes (`public`/`internal`/`restricted`); Graphify reconfirmed as an optional derived reader only, its license question already resolved and out of scope.
* **Tooling**: Added `scripts/provenance/validate_provenance.py`, a dependency-free validator that reports violations as a JSON path plus a stable rule id (`PROV001`-`PROV005`) and never the offending value, and `tests/test_validate_provenance.py` covering a valid record, each missing required field, an invalid `outcome.origin`, disallowed sensitive/unsupported fields, and safe (value-free) error messages.
* **CI**: Wired the provenance validator and its unit tests into the existing `test` job in `.github/workflows/ci.yml` -- no new workflow, job, or third-party dependency.
* **Process**: Replaced `.github/pull_request_template.md` with four fields -- Intent, Human direction, Agent/tool involvement (none/assisted/generated-and-reviewed), Verification -- matching the provenance record schema.
## 2026-09-14
* **Plan**: Added [Repository Provenance](plans/repository-provenance.md), defining a layered per-repository manifest, Git/SBOM/attestation evidence, a generated organization catalog, Graphify's non-authoritative indexing role, and a phased rollout. Corrected the installed Graphify `0.9.61` license classification to Apache-2.0 rather than MIT.
* **Tooling**: Fixed OKF markdown discovery to apply excluded-directory rules only to repository-relative paths. Local checkouts stored beneath a parent `.copilot` directory no longer produce a false-clean `0/0 markdown files` baseline, and the test suite now guards against empty bundle discovery and excluded parent-directory regressions.
* **Tooling**: Rewrote `scripts/okf/validate_okf_markdown.py` to enforce OKF v0.2 strictly and recursively: every non-reserved markdown file must carry a parseable YAML frontmatter block with a non-empty `type`; `index.md`/`log.md` must have no frontmatter, except the bundle-root `index.md`, which may carry frontmatter containing only `okf_version`; the optional `tags`/`status`/`generated`/`verified`/`sources` frontmatter families are shape-checked when present; each `sources[]` entry must declare a non-empty `resource`; and every body footnote label (`[^id]`) must correspond to a `sources[].id`. Added a small in-house YAML-subset parser (no third-party dependency) to support the richer shapes, and a `tests/` unit suite (`python -m unittest discover -s tests`) covering the new rules, wired into the `test` CI job.

## 2026-09-13 (4)
* **Organization**: Moved the [Emergency Cloud Handoff](runbooks/emergency-cloud-handoff.md) runbook into `runbooks/`, keeping bundle entrypoints and the Vision at the repository root.

## 2026-09-13 (3)
* **Runbook**: Bounded the [Emergency Cloud Handoff](runbooks/emergency-cloud-handoff.md) procedure to a 1-hour checkpoint per cloud session -- it must push its state and check in at the hour mark (or on completion) instead of running unbounded, so you can choose to extend or stop. The paired "Emergency Cloud Handoff" automation now also nudges existing handoffs approaching their bound.

## 2026-09-13 (2)
* **Runbook**: Added [Emergency Cloud Handoff](runbooks/emergency-cloud-handoff.md), a procedure for moving busy local agent sessions to cloud sessions when you need to shut down suddenly -- force-push in-flight work, open a cloud session per PR from the pushed branch, hand it a resume prompt, then stop the local session.

## 2026-09-13
* **Workflow**: Added a "Bounded PR Process" section to `.github/copilot-instructions.md` requiring recon before starting, validation before first push, batched review responses, sparing base-branch syncs, a two-cycle/30-minute review bound with blocker reporting, and staged (focused-then-full) validation.
* **Tooling**: Added `.github/pull_request_template.md` mirroring the bounded PR checklist, and excluded it from the OKF `type` frontmatter requirement (tooling config, like `copilot-instructions.md`).
* **CI**: Replaced `.github/workflows/okf-markdown.yml` with `.github/workflows/ci.yml`, which reports the `lint`, `test`, and `security` checks the organization ruleset requires on `main`. The previous workflow was path-filtered to `**/*.md` and used a job name the ruleset didn't recognize, so pull requests stayed blocked on checks that never reported.

## 2026-09-12
* **Initialization**: Established the OKF bundle structure.
* **Update**: Classified [How We Work](README.md) as a Vision.
* **Update**: Clarified the opening principle and the company statement.
