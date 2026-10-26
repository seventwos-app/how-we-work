# Copilot Instructions

## Autonomous review policy

Follow [Autonomous review and separation of duties](instructions/autonomous-review.instructions.md) for purpose/outcome challenge, CI evidence reuse, independent finding closure, and bounded Copilot adjudication. Use existing review agents; do not add a routine human approval gate or duplicate review rounds. Preserve mandatory specialist gates, required checks, and action authorization.

## Repo purpose
A small OKF (Organizational Knowledge Framework, v0.2) documentation bundle expressing Seventwos' vision/heuristic for how humans and AI agents collaborate ("workspace captures intent, repository captures implementation"). It is not an application repository: it has no application runtime or package manifest, but it does retain lightweight pull-request CI for its in-repository validators.

## Stack
- Pure Markdown content with a small in-repository Python OKF validator and pull-request CI; no application runtime or package manifest.
- Uses OKF bundle conventions via YAML frontmatter (`okf_version: "0.2"` in `index.md`; `type`, `title`, `description`, `tags` in `README.md`).

## Repo shape
- `README.md` — the "How We Work" vision statement (frontmatter-tagged `type: Vision`).
- `stack.md` — a technology-stack specification, including the architecture's licensing posture.
- `plans/` and `runbooks/` — provenance and operational concepts, each indexed as part of the bundle.
- `index.md` — the complete OKF bundle index.
- `log.md` — dated "Update Log" of substantive bundle changes — append-only style, newest section on top per date.

## Commands
- `python scripts/okf/validate_okf_markdown.py --changed` — validates changed markdown against this repo's OKF v0.2 bundle convention (the `lint` CI check on pull requests). `--all` scans everything and reports a baseline without failing.
- `python scripts/provenance/validate_provenance.py --file .seventwos/provenance.json` — validates the repository provenance record against schema v0.1 (the `test` CI job).

## Conventions
- Changes to `README.md` content should be reflected as a new dated entry in `log.md` (pattern observed: `## YYYY-MM-DD` heading with `* **Label**: description` bullets), matching git history where every substantive README edit has a corresponding commit message describing the wording/classification change.
- Preserve YAML frontmatter on `README.md` (`type`, `title`, `description`, `tags`) and on `index.md` (`okf_version`) — these are OKF bundle metadata, not incidental headers.
- Commit messages in history are short, imperative, `docs:`-prefixed for structural changes (e.g. `docs: update Vision description in README frontmatter`) or plain descriptive for content edits.

## Provenance
- `.seventwos/provenance.json` (schema v0.1) records, per change: intent, human direction, agent involvement (`none`/`assisted`/`generated-and-reviewed`), review, and source outcome — see `plans/repository-provenance.md` for the full convention and disclosure classes (`public`/`internal`/`restricted`). It must never contain workspace IDs, prompts, customer data, or credentials.
- `.github/pull_request_template.md` collects exactly the four fields a provenance entry needs: Intent, Human direction, Agent/tool involvement, Verification.
- `scripts/provenance/validate_provenance.py` reports violations as a JSON path plus a rule id (`PROV001`-`PROV005`), never the offending value. Run `python -m unittest discover -s tests` after touching it.

## Gotchas
- This is a docs/vision artifact, not an application — do not add application tooling or CI beyond the existing OKF validator workflow unless explicitly requested.
- Remote has extra branches (`a-tcp-patch-1`, `a-tcp-patch-2`) beyond `main`; default branch is `main` — don't assume those are stale/mergeable without checking.
- Apply repository exclusion rules to paths relative to the repository root, never absolute paths. Local Copilot checkouts commonly live beneath a parent `.copilot` directory; inspecting absolute path parts can silently exclude the entire bundle. Treat a `0/0 markdown files` baseline as a validator failure, not a successful empty scan.

## Agents
This bundle captures intent, so its agents are document-production specialists. Architecture and implementation agents (e.g. `Platform Architect`) live in the implementation repository, not here.

- **Fact Checker** (`.github/agents/fact-checker.agent.md`, pinned to `Gemini 3.8 Flash`): Web search, evidence triage, and fact-checking specialist. Use when searching the web for technical specifications, verifying claims, investigating external libraries or desktop frameworks, and validating facts against primary sources before adding them to bundle documentation.
- **Technical Visualizer** (`.github/agents/technical-visualizer.agent.md`, pinned to `Claude Sonnet 5.5`): Technical visualization, system topology, and information design specialist. Use when mapping complex technical architectures, human-agent workflows, sequence lifecycles, and multi-platform boundaries into rigorous, elegant diagrams using C4 modeling, Tufte information design principles, and custom-styled Mermaid charts.

## Skills
- **`mermaid-diagrams`** (`.github/skills/mermaid-diagrams/SKILL.md`): Technical standards for generating clean, syntax-valid, and visually compelling Mermaid diagrams (architecture topologies, sequence flows, state diagrams, class relationships, and system charts).

## OKF Validation (added by explicit request; kept intentionally minimal)

`.github/workflows/ci.yml` provides the three status checks the
organization ruleset requires on `main` (`lint`, `test`, `security`). It
runs on every pull request — a required check that never reports would
leave a PR blocked forever, so it is deliberately *not* path-filtered.

- `lint` — `scripts/okf/validate_okf_markdown.py --changed`
- `test` — both validators compile, the `tests/` unit suite passes, the
  whole bundle's OKF baseline is clean, and the provenance record
  (`.seventwos/provenance.json`) conforms to schema v0.1
- `security` — workflows stay read-only and avoid `pull_request_target`

These only report pass/fail as PR checks — they never open issues,
comment, or write to the repo. This repo is public, so anything more (e.g.
automation that files issues) would be visible to everyone; that tradeoff
is why broader automation used in other repos (monthly spec-drift watch,
push-triggered doc-gap delegation to `@copilot`) was deliberately **not**
added here. Ask before adding either.

The validator understands this repo's actual OKF usage: every non-reserved
bundle-content `.md` file recursively is a concept requiring a parseable YAML frontmatter
block with a non-empty `type`; `index.md` and `log.md` are reserved and
must carry no frontmatter, except the bundle-root `index.md`, which may
carry a frontmatter block containing only `okf_version`. When present, it
also enforces the shape of the optional `tags`/`status`/`generated`/
`verified`/`sources` frontmatter families, requires each `sources[]` entry
to declare a non-empty `resource`, and requires every body footnote label
(`[^id]`) to correspond to a `sources[].id`. Copilot tooling directories
(`.github/` and `.copilot/`) are excluded because they are configuration,
not OKF content. Run `python -m unittest discover -s tests` after touching
the validator. The root `index.md` is also a complete bundle manifest:
every concept document must appear in it, and every linked Markdown document
must exist.

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
- **Right-size delegation.** Use the execution policy below to separate implementation ownership from required independent review. Delegate substantial independent work or required specialist judgment, not merely a small edit; give delegates bounded objectives.
- **Model routing.** Let Auto mode pick per task complexity; do not force larger/slower models for simple mechanical steps. Reasoning effort is a separate, deliberate choice — never reduced silently in the name of speed.

## Pull requests and merge authority

- Use a branch and PR for changes targeting the default branch, `main`, or `develop`. The organization-wide [Copilot review and owner-led merge ruleset](https://github.com/organizations/seventwos-app/settings/rules/25233290) requests Copilot review on PR creation and subsequent pushes; draft PRs are reviewed when ready.
- `tcp-a` and `a-tcp` may each merge their own PR after required CI/security checks pass and review threads are resolved. Do not request the other account's approval merely because the author cannot approve their own PR. Human approval count is zero; code-owner, last-push, and extra unattributed-change approvals are not required.
- Agents must check the latest-head Copilot review and address valid findings before recommending merge. Automatic review requests are not a GitHub-enforced review-completion gate and depend on Copilot access/credits; report unavailable or pending review as a blocker, not a completed review.
- Preserve existing security/review agents, required checks, and unrelated protections. Do not impersonate a human approver, switch accounts to manufacture approval, bypass failed gates, or reintroduce cross-user approval requirements.
- This policy removes only cross-user PR approval requirements. It does not authorize an agent to merge, deploy, publish, spend money, or perform destructive actions without the authorization otherwise required for that task.
- Read live GitHub rules for the target branch when resuming PR work. Repository instructions record intent; Graphify is a derived index, not authority for external GitHub settings. Refresh it through the existing workflow after documentation merges; do not claim it has learned unindexed changes.

## Efficient execution and delegation

- Start with the repo's existing instructions, agent catalog, and relevant skill. Inspect the actual diff and reuse existing implementations before adding machinery. Load only context needed for the current phase.
- For a known-owner, bounded, low-risk task with focused proof, the current owner may implement directly without an implementation handoff. Required independent purpose/outcome reviews, customization audits, pre-push review, and risk-triggered specialist gates still apply; direct implementation is not self-approval. Unknown ownership or risk follows existing specialist routing. Delegate substantial independent work, not a continuous investigation already owned by another agent.
- Give each delegate a concrete objective, relevant context, allowed paths, ownership, acceptance checks, and a stop condition. Use the configured model/risk policy rather than overriding pins for speed.
- Parallelize only independent work with non-overlapping write ownership. Keep a continuous investigation with one owner; do not duplicate a delegate's search or implementation. Use background agents only while doing independent work, and collect their result without polling.
- Batch related edits and review feedback. Run the smallest relevant validation; expand only when risk or failures justify it. Do not add a second review tool merely because it is available, retry CI blindly, or treat an installed skill/agent as proof that it runs in CI.
- Reuse validation only for the revision or exact diff, inputs, environment, and coverage it actually proves. Count a hook-run canonical gate as that cycle's run; do not repeat it manually. Preserve deliberately independent security checks and stricter latest-head requirements.
- Give long operations a justified runtime deadline and progress signal. A progress checkpoint or tool initial wait is not a cancellation deadline: do not kill a healthy build just because a checkpoint expires. If an operation-specific deadline expires, cancel only its task-owned process tree, verify termination, and report the failure.
- Preserve the existing review-loop ceiling across resumes: record its wall-clock start, completed cycles, reviewed SHA, pending operations, and any authorized continuation in the existing task/PR record. At the ceiling stop further autonomous corrections and pushes, report the blocker, and keep healthy pending builds separate from the review clock; restarting a session does not reset the budget.
- The coordinating agent owns integration, verifies acceptance evidence, and reports what changed, what remains blocked, and whether the result is merged. Instruction files guide compatible agents; they do not guarantee every tool loads them.

## Engineering discipline routing

Apply these skills only during the matching phase, within the current agent's
existing role and permissions. Load through the client's skill tool when
available, or read the linked document as a reference; never claim a tool ran
when it did not. Existing workflow routers, authorization, read-only boundaries,
specialist review gates, model settings, and publishing rules remain unchanged.
Skip duplicate process when an existing workflow already supplies the evidence.

| Current work | Skill | Relevant owners |
|---|---|---|
| Features, bugs, performance, tests, evaluations | [evidence-first-engineering](skills/evidence-first-engineering/SKILL.md) | Implementing, infrastructure, data, and test specialists |
| Specs, interfaces, architectural trade-offs | [decision-and-design](skills/decision-and-design/SKILL.md) | Architect, planner, and implementing specialist |
| Claims, research, durable docs, instruction changes, conflicting sources | [artifact-integrity](skills/artifact-integrity/SKILL.md) | Reviewers, researchers, fact checkers, writers, and task owner |
| Resume, transfer, blocked work, recurring-failure lessons | [durable-agent-handoff](skills/durable-agent-handoff/SKILL.md) | Current task owner |

Routine acknowledgements and direct one-command lookups need none of these.
Read-only reviewers assess and report evidence; they do not gain edit or
execution authority. These skills do not authorize deployments or publishing.
See the [pinned mirror manifest](skills/engineering-pack.lock.json) for the
authoritative source and digests, and [behavior scenarios](skills/engineering-scenarios.json)
for expected and forbidden behavior. File presence, valid structure, actual
activation, and improved outcomes are separate claims.
