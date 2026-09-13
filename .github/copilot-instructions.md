# Copilot Instructions

## Repo purpose
A small OKF (Organizational Knowledge Framework, v0.2) documentation bundle expressing Seventwos' vision/heuristic for how humans and AI agents collaborate ("workspace captures intent, repository captures implementation"). Not a code repo — no app, no dependencies, no CI.

## Stack
- Pure Markdown content. No package manifest, no language runtime, no `.github/workflows/`.
- Uses OKF bundle conventions via YAML frontmatter (`okf_version: "0.2"` in `index.md`; `type`, `title`, `description`, `tags` in `README.md`).

## Repo shape
- `README.md` — the actual content: the "How We Work" vision statement (frontmatter-tagged `type: Vision`).
- `index.md` — OKF bundle index; links to `README.md` as the bundle's single entry.
- `log.md` — dated "Update Log" of substantive changes to the bundle (init, classification, wording edits) — append-only style, newest section on top per date.

## Commands
- `python scripts/okf/validate_okf_markdown.py --changed` — validates changed markdown against this repo's OKF v0.2 bundle convention (used by CI on pull requests). `--all` scans everything and reports a baseline without failing.

## Conventions
- Changes to `README.md` content should be reflected as a new dated entry in `log.md` (pattern observed: `## YYYY-MM-DD` heading with `* **Label**: description` bullets), matching git history where every substantive README edit has a corresponding commit message describing the wording/classification change.
- Preserve YAML frontmatter on `README.md` (`type`, `title`, `description`, `tags`) and on `index.md` (`okf_version`) — these are OKF bundle metadata, not incidental headers.
- Commit messages in history are short, imperative, `docs:`-prefixed for structural changes (e.g. `docs: update Vision description in README frontmatter`) or plain descriptive for content edits.

## Gotchas
- This is a docs/vision artifact, not a project with builds or tests — do not add more tooling, package files, or CI beyond the OKF validator below unless explicitly requested.
- Remote has extra branches (`a-tcp-patch-1`, `a-tcp-patch-2`) beyond `main`; default branch is `main` — don't assume those are stale/mergeable without checking.

## OKF Validation (added by explicit request; kept intentionally minimal)

`.github/workflows/okf-markdown.yml` runs
`scripts/okf/validate_okf_markdown.py --changed` on every pull request
touching a `.md` file. It only reports pass/fail as a PR check — it never
opens issues, comments, or writes to the repo. This repo is public, so
anything more (e.g. automation that files issues) would be visible to
everyone; that tradeoff is why broader automation used in other repos
(monthly spec-drift watch, push-triggered doc-gap delegation to
`@copilot`) was deliberately **not** added here. Ask before adding either.

The validator understands this repo's actual OKF usage: `README.md` is a
`type: Vision` concept, `index.md` is the reserved bundle index
(`okf_version` frontmatter, not `type`), and `log.md` is the reserved,
frontmatter-free update log — `.github/copilot-instructions.md` itself is
excluded (tooling config, not OKF content).

## Workflow Optimization (quality-neutral, applies to all work in this repo)

- **Parallelize independent work.** Batch every tool call that doesn't depend on another call's output into one response (multiple view/grep/glob/search calls together). Only serialize true dependencies. Use background agents for self-contained sub-investigations instead of polling.
- **Control context size.** Read narrowly (view_range on large files, LIMIT/specific columns on queries, grep/head on shell output). Avoid re-reading data already established in context. Summarize large tool output instead of carrying raw dumps forward turn after turn.
- **Session hygiene.** Prefer a focused session per distinct task/topic over one ever-growing thread.
- **Tool-call efficiency.** Prefer built-in grep/glob/view over shell equivalents (rg/find/cat). Chain related bash commands with `&&`. Suppress verbose/pager output.
- **Right-size delegation.** Delegate only when a sub-task needs substantial separate context; do not delegate anything doable in ≤5 direct calls. Give delegated agents bounded, concrete objectives.
- **Model routing.** Let Auto mode pick per task complexity; do not force larger/slower models for simple mechanical steps. Reasoning effort is a separate, deliberate choice — never reduced silently in the name of speed.
