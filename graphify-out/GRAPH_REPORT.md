---
type: Report
title: Graphify Knowledge Graph Report
description: Generated analysis of the assembled repository knowledge graph.
generated:
  by: graphify cluster-only
---

# Graph Report - How We Work (2026-10-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 196 nodes · 288 edges · 27 communities (11 shown, 16 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a8394f5e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 14
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28

## God Nodes (most connected - your core abstractions)
1. `ConceptFrontmatterTests` - 16 edges
2. `valid_document()` - 14 edges
3. `ReservedFileTests` - 11 edges
4. `SourcesAndFootnoteTests` - 10 edges
5. `_parse_block_mapping()` - 9 edges
6. `check_file()` - 8 edges
7. `Frontmatter` - 7 edges
8. `RepoBundleTests` - 7 edges
9. `_parse_scalar_or_flow()` - 7 edges
10. `write()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `How We Work` --conceptually_related_to--> `Repository Provenance Plan`  [INFERRED]
  README.md → plans/repository-provenance.md
- `Security Canary Workflow` --references--> `Security Reporting`  [INFERRED]
  .github/workflows/security-canary.yml → SECURITY.md
- `How We Work Index` --references--> `Architecture Diagram Maintenance`  [EXTRACTED]
  index.md → diagrams/README.md
- `Graphify Catch-up Workflow` --conceptually_related_to--> `Copilot Instructions`  [INFERRED]
  .github/workflows/graphify-catchup.yml → .github/copilot-instructions.md
- `Technology Stack for User Frontend` --references--> `Architecture Diagram Maintenance`  [EXTRACTED]
  stack.md → diagrams/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Archify Viewer Core Systems** — diagrams_stack_architecture_archify_view, diagrams_stack_architecture_archify_focus, diagrams_stack_architecture_archify_guidedviews, diagrams_stack_architecture_archify_motiongovernor [EXTRACTED 0.90]
- **Agent Catalog** — github_agents_change_reviewer, github_agents_fact_checker, github_agents_technical_visualizer [EXTRACTED 1.00]
- **Agent path** — diagrams_stack_architecture_homeserver, diagrams_stack_architecture_agent_gateway, diagrams_stack_architecture_models [EXTRACTED 1.00]
- **Agent Safety Framework** — github_agents_shared_safety_blocks, github_agents_change_reviewer, github_agents_fact_checker, github_agents_technical_visualizer [EXTRACTED 1.00]
- **Archify Viewer Subsystems** — diagrams_stack_architecture_routeprobe, diagrams_stack_architecture_semanticlens, diagrams_stack_architecture_guide [EXTRACTED 1.00]
- **Client foundations** — diagrams_stack_architecture_desktop, diagrams_stack_architecture_ios, diagrams_stack_architecture_android, diagrams_stack_architecture_local_extensions [EXTRACTED 1.00]
- **Engineering Discipline Pack** — github_skills_artifact_integrity, github_skills_decision_and_design, github_skills_durable_agent_handoff, github_skills_evidence_first_engineering [EXTRACTED 1.00]
- **Engineering Discipline Pack** — github_skills_artifact_integrity_third_party_notices, github_skills_decision_and_design_third_party_notices, github_skills_durable_agent_handoff_third_party_notices, github_skills_evidence_first_engineering_third_party_notices [EXTRACTED 1.00]
- **Matrix fabric** — diagrams_stack_architecture_desktop, diagrams_stack_architecture_ios, diagrams_stack_architecture_android, diagrams_stack_architecture_homeserver, diagrams_stack_architecture_push, diagrams_stack_architecture_federation [EXTRACTED 1.00]
- **Archify Layout & Chrome Management** — diagrams_stack_architecture_archify_readerlayout, diagrams_stack_architecture_archify_viewerchromelayout, diagrams_stack_architecture_archify_radar [INFERRED 0.80]
- **Security Guardrails** — security_policy, github_workflows_security_canary, github_workflows_ci [INFERRED]

## Communities (27 total, 16 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (19): changed_markdown_files(), check_bundle_index(), check_file(), _check_optional_shape(), _check_sources_and_footnotes(), Frontmatter, frontmatter_body(), _indent_of() (+11 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (7): DuplicateIdTests, InvalidOriginTests, MissingRequiredFieldTests, SafeErrorMessageTests, SensitiveAndUnsupportedFieldTests, valid_document(), ValidRecordTests

### Community 3 - "Community 3"
Cohesion: 0.28
Nodes (9): _check_entry(), _check_non_empty_string(), _check_outcome(), load(), main(), _require_type(), _scan_sensitive_fields(), _sorted() (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (10): Architecture Diagram Maintenance, Rendered Architecture Diagram, Security Canary Workflow, Knowledge Graph Report, How We Work Index, Repository Provenance, Repository Provenance Plan, How We Work (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (3): RepoBundleTests, ReservedFileTests, write()

### Community 7 - "Community 7"
Cohesion: 0.28
Nodes (9): Agent Gateway, Android Client, Desktop Client, Federated Homeservers, Matrix Homeserver, iOS Client, Local Extensions, Frontier Models (+1 more)

### Community 8 - "Community 8"
Cohesion: 0.31
Nodes (9): Archify.finder, Archify.focus, Archify.guidedViews, Archify.motionGovernor, Archify.radar, Archify.routeProbe, Archify.sourceEvidence, Archify.view (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.39
Nodes (8): Change Reviewer Agent, Fact Checker Agent, Shared Safety Blocks, Technical Visualizer Agent, Copilot Instructions, Autonomous Review Policy, Mermaid Diagrams Skill, Graphify Catch-up Workflow

### Community 10 - "Community 10"
Cohesion: 0.53
Nodes (6): Artifact Integrity Third-party Notices, Decision and Design Third-party Notices, Durable Agent Handoff Third-party Notices, Evidence-first Engineering Third-party Notices, Paperthin, Skills

### Community 11 - "Community 11"
Cohesion: 1.00
Nodes (3): Diagram Guide Module, Route Probe Module, Semantic Lens Module

### Community 12 - "Community 12"
Cohesion: 0.67
Nodes (3): runCopy, runCopyShareCard, writePngToClipboard

## Knowledge Gaps
- **27 isolated node(s):** `Graphify Semantic Catch-up workflow`, `runCopy`, `runCopyShareCard`, `Archify.intentTrace`, `Archify.presentation` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 64 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConceptFrontmatterTests` connect `Community 4` to `Community 1`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **What connects `Graphify Semantic Catch-up workflow`, `runCopy`, `runCopyShareCard` to the rest of the system?**
  _27 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0858974358974359 - nodes in this community are weakly interconnected._
- **Why does `ReservedFileTests` connect `Community 6` to `Community 1`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.10591133004926108 - nodes in this community are weakly interconnected._
- **Why does `SourcesAndFootnoteTests` connect `Community 2` to `Community 1`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._