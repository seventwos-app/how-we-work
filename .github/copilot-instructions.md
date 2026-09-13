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
- `python scripts/okf/validate_okf_markdown.py --changed` — validates changed markdown against this repo's OKF v0.2 bundle convention (the `lint` CI check on pull requests). `--all` scans everything and reports a baseline without failing.

## Conventions
- Changes to `README.md` content should be reflected as a new dated entry in `log.md` (pattern observed: `## YYYY-MM-DD` heading with `* **Label**: description` bullets), matching git history where every substantive README edit has a corresponding commit message describing the wording/classification change.
- Preserve YAML frontmatter on `README.md` (`type`, `title`, `description`, `tags`) and on `index.md` (`okf_version`) — these are OKF bundle metadata, not incidental headers.
- Commit messages in history are short, imperative, `docs:`-prefixed for structural changes (e.g. `docs: update Vision description in README frontmatter`) or plain descriptive for content edits.

## Gotchas
- This is a docs/vision artifact, not a project with builds or tests — do not add more tooling, package files, or CI beyond the OKF validator below unless explicitly requested.
- Remote has extra branches (`a-tcp-patch-1`, `a-tcp-patch-2`) beyond `main`; default branch is `main` — don't assume those are stale/mergeable without checking.

## OKF Validation (added by explicit request; kept intentionally minimal)

`.github/workflows/ci.yml` provides the three status checks the
organization ruleset requires on `main` (`lint`, `test`, `security`). It
runs on every pull request — a required check that never reports would
leave a PR blocked forever, so it is deliberately *not* path-filtered.

- `lint` — `scripts/okf/validate_okf_markdown.py --changed`
- `test` — validator compiles, its `tests/` unit suite passes, and the
  whole bundle's OKF baseline is clean
- `security` — workflows stay read-only and avoid `pull_request_target`

These only report pass/fail as PR checks — they never open issues,
comment, or write to the repo. This repo is public, so anything more (e.g.
automation that files issues) would be visible to everyone; that tradeoff
is why broader automation used in other repos (monthly spec-drift watch,
push-triggered doc-gap delegation to `@copilot`) was deliberately **not**
added here. Ask before adding either.

The validator understands this repo's actual OKF usage: every non-reserved
`.md` file recursively is a concept requiring a parseable YAML frontmatter
block with a non-empty `type`; `index.md` and `log.md` are reserved and
must carry no frontmatter, except the bundle-root `index.md`, which may
carry a frontmatter block containing only `okf_version`. When present, it
also enforces the shape of the optional `tags`/`status`/`generated`/
`verified`/`sources` frontmatter families, requires each `sources[]` entry
to declare a non-empty `resource`, and requires every body footnote label
(`[^id]`) to correspond to a `sources[].id`. `.github/copilot-instructions.md`
and `.github/pull_request_template.md` are excluded (tooling config, not
OKF content). Run `python -m unittest discover -s tests` after touching
the validator.

## Engineering Workflow: Bounded PR Process (applies to all agent-driven PR work)

Goal: keep every PR-based task on a predictable, bounded path and prevent
unbounded push/review/fix loops.

- **Start with reconnaissance.** Before writing code, check for an existing
  PR/issue for the task, the target branch's protection rules, any open
  review threads on a PR you're resuming, and what has changed on the base
  branch (`main`) since the branch was created. Don't duplicate work or
  reopen settled discussion.
- **Implement and validate before the first push.** Finish the intended
  change and run the relevant targeted validation (e.g. the OKF validator,
  or any check that applies to the files you touched) locally before
  pushing anything. Don't push partial or unvalidated work to open a PR
  "to see what CI says."
- **Batch review feedback.** When a reviewer (human or automated) leaves
  findings, collect and address all valid points from that round in a
  single follow-up push rather than pushing once per comment.
- **Sync sparingly.** Only merge/rebase onto the latest base branch
  immediately before what you expect to be your final push, not on every
  iteration — this avoids churn from repeatedly re-resolving the same
  conflicts.
- **Bound the review loop.** Plan for at most two automated review cycles
  or 30 minutes of iteration on a single PR, whichever comes first. If the
  PR isn't mergeable by then, stop and report a concrete blocker (what's
  failing, what was tried, what decision or input is needed) instead of
  continuing to iterate silently.
- **Report progress regularly.** Post a short status update at each
  meaningful stage transition (recon done, implementation done, validation
  run, review addressed) and at least every 10 minutes during longer work,
  so a human can follow along or intervene.
- **Validate in two tiers.** Run focused/targeted checks while iterating
  (e.g. just the file(s) you changed), then run the full validation gate
  exactly once, right before the final push, to confirm nothing else
  regressed.

## Workflow Optimization (quality-neutral, applies to all work in this repo)

- **Parallelize independent work.** Batch every tool call that doesn't depend on another call's output into one response (multiple view/grep/glob/search calls together). Only serialize true dependencies. Use background agents for self-contained sub-investigations instead of polling.
- **Control context size.** Read narrowly (view_range on large files, LIMIT/specific columns on queries, grep/head on shell output). Avoid re-reading data already established in context. Summarize large tool output instead of carrying raw dumps forward turn after turn.
- **Session hygiene.** Prefer a focused session per distinct task/topic over one ever-growing thread.
- **Tool-call efficiency.** Prefer built-in grep/glob/view over shell equivalents (rg/find/cat). Chain related bash commands with `&&`. Suppress verbose/pager output.
- **Right-size delegation.** Delegate only when a sub-task needs substantial separate context; do not delegate anything doable in ≤5 direct calls. Give delegated agents bounded, concrete objectives.
- **Model routing.** Let Auto mode pick per task complexity; do not force larger/slower models for simple mechanical steps. Reasoning effort is a separate, deliberate choice — never reduced silently in the name of speed.
