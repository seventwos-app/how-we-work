# Update Log

## 2026-09-13
* **Workflow**: Added a "Bounded PR Process" section to `.github/copilot-instructions.md` requiring recon before starting, validation before first push, batched review responses, sparing base-branch syncs, a two-cycle/30-minute review bound with blocker reporting, and staged (focused-then-full) validation.
* **Tooling**: Added `.github/pull_request_template.md` mirroring the bounded PR checklist, and excluded it from the OKF `type` frontmatter requirement (tooling config, like `copilot-instructions.md`).
* **CI**: Replaced `.github/workflows/okf-markdown.yml` with `.github/workflows/ci.yml`, which reports the `lint`, `test`, and `security` checks the organization ruleset requires on `main`. The previous workflow was path-filtered to `**/*.md` and used a job name the ruleset didn't recognize, so pull requests stayed blocked on checks that never reported.

## 2026-09-12
* **Initialization**: Established the OKF bundle structure.
* **Update**: Classified [How We Work](README.md) as a Vision.
* **Update**: Clarified the opening principle and the company statement.
