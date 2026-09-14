---
type: Plan
title: Repository Provenance
description: A minimal, dependency-free MVP for recording who directed a change, whether an agent assisted, who reviewed it, and where the resulting change lives.
tags: [provenance, mvp, disclosure]
status: stable
sources:
  - id: slsa-provenance
    resource: https://slsa.dev/spec/v1.2/provenance
  - id: graphify-license
    resource: https://github.com/Graphify-Labs/graphify/blob/v8/LICENSE
---

# Repository Provenance

## Outcome

For every substantive change to this repository, an evidence trail should
answer:

1. What was the intent behind the change?
2. Who directed it (human direction), even when an agent produced the diff?
3. Was an agent or tool involved, and how much (none, assisted, or
   generated-and-reviewed)?
4. Who or what reviewed it before it merged?
5. Where does the resulting change actually live (a commit, pull request,
   or release)?

Provenance is verifiable information about where, when, and how an
artifact was produced.[^slsa-provenance] Git history and pull requests
already carry the detailed change record; this convention adds a small,
public-safe summary layer so that chain -- **workspace intent -> human
direction -> agent-assisted change -> review -> source outcome** -- is
explicit and machine-checkable, without duplicating anything Git already
tracks and without exposing anything private.

This replaces an earlier, heavier draft of this plan (YAML manifests,
SBOMs, signed SLSA attestations, and a generated organization catalog).
That scope is out of scope for this repository today; this MVP is
intentionally small enough to adopt, validate, and maintain with no new
dependencies.

## Decision

### Record

Each repository that adopts this convention keeps one file,
`.seventwos/provenance.json`, schema `v0.1`:

```json
{
  "schema_version": "0.1",
  "repository": "seventwos-app/how-we-work",
  "disclosure_class": "public",
  "entries": [
    {
      "id": "2026-09-14-example",
      "intent": "Short, generalized statement of why the change was made.",
      "human_direction": "Who asked for it / what they asked for, in general terms.",
      "agent_involvement": "assisted",
      "review": "reviewed-before-merge",
      "outcome": {
        "origin": "pull_request",
        "reference": "a commit SHA, PR URL, or release tag/description"
      }
    }
  ]
}
```

Field notes:

- `agent_involvement` is one of `none`, `assisted`, or
  `generated-and-reviewed` -- the same three values used in the pull
  request template's "Agent/tool involvement" field, so a PR and its
  provenance entry stay consistent.
- `outcome.origin` is one of `commit`, `pull_request`, or `release`.
- `disclosure_class` may also be set per-entry to override the
  repository-level default (for example, a repository could be `internal`
  overall but publish one `public` entry). This repository's default and
  every entry in it are `public`.

### Disclosure classes

| Class | Meaning | May contain |
|---|---|---|
| `public` | Safe for anyone, including outside the organization, to read | Generalized intent, human direction, and review statements; no workspace IDs, prompts, customer data, or credentials |
| `internal` | Safe for the organization, not for external readers | The above, plus internal team/project names |
| `restricted` | Limited to a named accountable group | Anything `internal` allows, plus details that would otherwise need redaction for a wider audience |

A record's `disclosure_class` states the most sensitive class its content
requires, so a reader (human or tool) can decide whether it's safe to
publish, quote, or merge into a wider catalog. A `public` record must
never contain private workspace identifiers, raw prompts, customer
information, credentials, or any other identity not needed to understand
the intent -> direction -> change -> review -> outcome chain.

### Validation

`scripts/provenance/validate_provenance.py` checks a record against the
schema above using only the Python standard library. It reports every
violation as a JSON path plus a stable rule id (`PROV001`-`PROV005`) --
never the offending value -- so a failing check is always safe to paste
into CI logs, an issue, or a review comment. Rules cover:

- required fields being present (`PROV001`);
- correct JSON types (`PROV002`);
- allowed enum values / patterns, e.g. `disclosure_class`,
  `agent_involvement`, `outcome.origin`, duplicate entry ids (`PROV003`);
- fields outside the schema (`PROV004`);
- field *names* that indicate private workspace/session identifiers, raw
  prompts, customer data, or credentials -- checked recursively, anywhere
  in the document (`PROV005`).

Run it locally with:

```sh
python scripts/provenance/validate_provenance.py --file .seventwos/provenance.json
python -m unittest discover -s tests
```

CI runs both as part of the existing `test` job in
`.github/workflows/ci.yml` -- no new workflow, job runner, or third-party
dependency was added.

### Pull requests

`.github/pull_request_template.md` asks for exactly four fields --
Intent, Human direction, Agent/tool involvement, Verification -- so the
information a provenance entry needs is already collected at review time,
without a separate process.

## Graphify

Graphify remains, at most, an **optional derived reader** of provenance
records: something that can index `.seventwos/provenance.json` files
across repositories for navigation, never an authority for the data
itself. Graphify's earlier license classification question
(`0.9.61`, Apache-2.0 not MIT) is resolved and out of scope for this
plan.[^graphify-license]

## Rollout

- **This repository**: adopt the record, validator, CI check, and PR
  template now (done as part of this change).
- **Other repositories**: adopt the same three artifacts --
  `.seventwos/provenance.json`, the validator, and the four-field PR
  template -- through a reviewed pull request per repository, when
  requested. Do not invent historical entries; start from the repository's
  current state forward.
- **Aggregation, SBOMs, and signed attestations** remain explicitly out of
  scope until there is a concrete need for them.

## Acceptance criteria

- `.seventwos/provenance.json` in this repository validates against
  schema `v0.1` with zero violations.
- The validator's unit tests cover: a valid record, each required-field
  omission, an invalid `outcome.origin`, a disallowed sensitive field
  name, an unsupported field name, and that violation messages never
  contain the offending value.
- CI fails a pull request that introduces an invalid provenance record,
  using the existing `test` job -- no new dependency, workflow, or job
  runner.
- The pull request template collects exactly the four fields a provenance
  entry needs.

[^slsa-provenance]: SLSA defines provenance as verifiable information about where, when, and how an artifact was produced.
[^graphify-license]: The upstream Graphify repository at release line `v8` contains the Apache License 2.0 text; the installed `graphifyy` package (`0.9.61`) declares the same license.
