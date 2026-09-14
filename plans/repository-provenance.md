---
type: Plan
title: Repository Provenance
description: A phased plan for recording the origin, ownership, licensing, and build lineage of every Seventwos repository.
tags: [provenance, repositories, supply-chain, attribution]
status: draft
sources:
  - id: slsa-provenance
    resource: https://slsa.dev/spec/v1.2/provenance
  - id: spdx-specification
    resource: https://spdx.dev/use/specifications/
  - id: graphify-package
    resource: https://pypi.org/pypi/graphifyy/0.9.61/json
  - id: graphify-license
    resource: https://github.com/Graphify-Labs/graphify/blob/v8/LICENSE
---

# Repository Provenance

## Outcome

Every Seventwos repository should answer, from evidence stored with or linked
from the repository:

1. Where did this repository and its imported material come from?
2. Who owns and maintains it?
3. Under which licenses may it be used and redistributed?
4. Which people, agents, tools, and source revisions produced an artifact?
5. Which evidence was generated automatically, and who verified it?

Provenance is verifiable information about where, when, and how an artifact was
produced.[^slsa-provenance] Git history remains the detailed change record; the
provenance system provides a stable summary and verifiable links into that
history.

## Decision

Use a layered model:

| Layer | Record | Authority |
|---|---|---|
| Repository | `.seventwos/provenance.yaml` | Human-readable declaration of identity, origin, ownership, and policy |
| Source history | Git commits, pull requests, reviews, and issues | Detailed attribution and change lineage |
| Dependencies | SPDX SBOM | Package, version, supplier, and license inventory |
| Builds/releases | Signed SLSA provenance attestation | Verifiable source-to-artifact lineage |
| Organization | Generated provenance catalog | Search and reporting across repositories |
| Knowledge graph | Graphify output | Navigation and relationship discovery only |

The repository manifest is the entrypoint, not a replacement for Git, SBOMs,
or attestations. The organization catalog must be generated from repository
manifests so there is one maintained source of truth.

## Repository manifest

Add this file to each repository:

```yaml
schema_version: "1.0"

repository:
  id: github:seventwos-app/example
  url: https://github.com/seventwos-app/example
  created_at: 2026-09-14T00:00:00Z
  created_by: github:username

purpose:
  summary: Short statement of why the repository exists.
  intent: workspace:<stable-reference>

origin:
  kind: original # original | fork | imported | generated
  upstream: null
  upstream_revision: null

ownership:
  accountable_team: team:example
  maintainers:
    - github:username

licensing:
  repository: Apache-2.0
  evidence: LICENSE
  dependencies: sbom/spdx.json

production:
  human_directed: true
  tools:
    - name: GitHub Copilot
      role: implementation
  generated_content_policy: reviewed-before-merge

verification:
  manifest_reviewers:
    - github:username
  last_verified_at: 2026-09-14T00:00:00Z
```

Use durable identifiers such as GitHub logins, team slugs, repository URLs,
commit SHAs, pull-request URLs, and workspace record IDs. Do not put prompts,
credentials, private conversation content, or unverifiable claims in the
manifest.

For imported or forked work, `origin.upstream` and
`origin.upstream_revision` are required. For generated repositories,
`purpose.intent` and at least one `production.tools` entry are required.

## Graphify

Graphify `0.9.61` is licensed under **Apache-2.0, not MIT**, according to both
its published package metadata and repository license.[^graphify-package]
[^graphify-license]

Graphify already records source files and source locations on graph entities,
and merged graphs can retain repository identity. Use it to:

- connect repositories, concepts, decisions, dependencies, and source files;
- query cross-repository relationships;
- expose missing or conflicting provenance records;
- link graph nodes back to the authoritative manifest, commit, or attestation.

Do not use `graphify-out/graph.json` as the provenance authority. It is derived
output, may contain inferred edges, and can be rebuilt. Every provenance edge
shown in the graph should retain its evidence URL and confidence
(`declared`, `verified`, or `inferred`).

## Automation

Create a reusable organization workflow that:

1. validates `.seventwos/provenance.yaml` against a versioned JSON Schema;
2. confirms the declared repository identity matches the GitHub repository;
3. verifies that the declared license evidence exists;
4. generates an SPDX SBOM for release-producing repositories; SPDX is an
   international open standard for software bill-of-materials data.
   [^spdx-specification]
5. creates a signed SLSA provenance attestation for release artifacts;
6. publishes only normalized, non-sensitive fields to the central catalog;
7. fails on invalid claims, but reports missing optional maturity fields as
   warnings during rollout.

The workflow should never rewrite a repository's declaration. Proposed
ownership, origin, or license changes require a reviewed pull request.

## Rollout

### Phase 0: Pilot

- Use `how-we-work` plus one application repository and one imported/forked
  repository.
- Agree on identifiers, required fields, privacy boundaries, and who can
  verify each claim.
- Record the Graphify installation as Apache-2.0 and link its exact version.

### Phase 1: Declare

- Publish the schema and a reusable validation workflow.
- Add the manifest to active repositories through reviewed pull requests.
- Mark unknown values explicitly; do not invent historical provenance.

### Phase 2: Verify

- Generate SPDX SBOMs for repositories that build or release software.
- Generate signed SLSA attestations for release artifacts.
- Require provenance validation for new repositories and releases.

### Phase 3: Aggregate

- Build a read-only organization catalog from default-branch manifests.
- Store the source repository, commit SHA, collection time, and verification
  result with every catalog entry.
- Add Graphify relationships from catalog entries to code and documentation.

### Phase 4: Enforce and maintain

- Add a repository-creation template that includes the manifest.
- Reverify on ownership, license, upstream, or release-workflow changes.
- Run a scheduled drift report for stale verification dates, missing SBOMs,
  broken evidence links, and conflicting licenses.

## Acceptance criteria

The pilot is successful when:

- every pilot repository has a schema-valid manifest on its default branch;
- each declared license has repository evidence;
- forks/imports identify an immutable upstream revision;
- a released artifact can be traced to its repository and commit through a
  signed attestation;
- application repositories publish an SPDX SBOM;
- the catalog identifies its source commit for every field;
- Graphify can navigate the records without being required to verify them;
- unknown history remains visibly unknown rather than being guessed.

[^slsa-provenance]: SLSA defines provenance as verifiable information about where, when, and how an artifact was produced.
[^spdx-specification]: SPDX is standardized as ISO/IEC 5962:2021.
[^graphify-package]: PyPI metadata for `graphifyy` version `0.9.61` declares the license expression `Apache-2.0`.
[^graphify-license]: The upstream Graphify repository at release line `v8` contains the Apache License 2.0 text.
