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
None — no install/build/test/lint tooling exists in this repo.

## Conventions
- Changes to `README.md` content should be reflected as a new dated entry in `log.md` (pattern observed: `## YYYY-MM-DD` heading with `* **Label**: description` bullets), matching git history where every substantive README edit has a corresponding commit message describing the wording/classification change.
- Preserve YAML frontmatter on `README.md` (`type`, `title`, `description`, `tags`) and on `index.md` (`okf_version`) — these are OKF bundle metadata, not incidental headers.
- Commit messages in history are short, imperative, `docs:`-prefixed for structural changes (e.g. `docs: update Vision description in README frontmatter`) or plain descriptive for content edits.

## Gotchas
- This is a docs/vision artifact, not a project with builds or tests — do not add tooling, package files, or CI unless explicitly requested.
- Remote has extra branches (`a-tcp-patch-1`, `a-tcp-patch-2`) beyond `main`; default branch is `main` — don't assume those are stale/mergeable without checking.

## Agents
- **Architect** (`.github/agents/architect.agent.md`, pinned to `Claude Opus 5`): Strategic planning and architecture design specialist. Use before implementing non-trivial features, evaluating technology stacks, introducing multi-service boundaries, or specifying system architectures. Challenges premises, maps failure modes, enforces Design-It-Twice trade-offs, and produces actionable specifications with high product-quality bars.
- **Fact Checker** (`.github/agents/fact-checker.agent.md`, pinned to `Gemini 3.8 Flash`): Web search, evidence triage, and fact-checking specialist. Use when searching the web for technical specifications, verifying claims, investigating external libraries or desktop frameworks, and validating facts against primary sources before adding them to bundle documentation.
- **System Cartographer** (`.github/agents/system-cartographer.agent.md`, pinned to `Claude Sonnet 5`): System architecture cartography, visual topology, and information design specialist. Use when mapping complex technical architectures, human-agent workflows, sequence lifecycles, and multi-platform boundaries into rigorous, elegant diagrams using C4 modeling, Tufte information design principles, and custom-styled Mermaid charts.

## Skills
- **`mermaid-diagrams`** (`.github/skills/mermaid-diagrams/SKILL.md`): Technical standards for generating clean, syntax-valid, and visually compelling Mermaid diagrams (architecture topologies, sequence flows, state diagrams, class relationships, and system charts).

## Workflow Optimization (quality-neutral, applies to all work in this repo)

- **Parallelize independent work.** Batch every tool call that doesn't depend on another call's output into one response (multiple view/grep/glob/search calls together). Only serialize true dependencies. Use background agents for self-contained sub-investigations instead of polling.
- **Control context size.** Read narrowly (view_range on large files, LIMIT/specific columns on queries, grep/head on shell output). Avoid re-reading data already established in context. Summarize large tool output instead of carrying raw dumps forward turn after turn.
- **Session hygiene.** Prefer a focused session per distinct task/topic over one ever-growing thread.
- **Tool-call efficiency.** Prefer built-in grep/glob/view over shell equivalents (rg/find/cat). Chain related bash commands with `&&`. Suppress verbose/pager output.
- **Right-size delegation.** Delegate only when a sub-task needs substantial separate context; do not delegate anything doable in ≤5 direct calls. Give delegated agents bounded, concrete objectives.
- **Model routing.** Let Auto mode pick per task complexity; do not force larger/slower models for simple mechanical steps. Reasoning effort is a separate, deliberate choice — never reduced silently in the name of speed.
