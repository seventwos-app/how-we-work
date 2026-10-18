---
type: Report
title: Graphify Knowledge Graph Report
description: Generated analysis of the assembled repository knowledge graph.
generated:
  by: graphify 0.9.92
---

# Graph Report - graphify-update  (2026-10-18)

## Corpus Check
- 33 files · ~83,146 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 188 nodes · 279 edges · 28 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f156409`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- validate_okf_markdown.py
- valid_document
- validate_provenance.py
- ConceptFrontmatterTests
- test_validate_okf_markdown.py
- OKF Bundle Index
- ReservedFileTests
- SourcesAndFootnoteTests
- Matrix Homeserver
- Archify.focus
- Copilot Instructions
- Frontmatter
- Diagram Guide Module
- writePngToClipboard
- test_gitleaks_ignore_regression.sh
- Archify Namespace
- Archify.intentTrace
- Archify.presentation
- Archify.readerLayout
- Pull Request Template
- Artifact Integrity Skill
- Decision and Design Skill
- Durable Agent Handoff Skill
- Evidence-First Engineering Skill
- CI Workflow
- Graphify Workflow
- Graphify Semantic Catch-up workflow
- Update Log

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
10. `validate()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Security Canary Workflow` --references--> `Security Reporting`  [INFERRED]
  .github/workflows/security-canary.yml → SECURITY.md
- `How We Work` --conceptually_related_to--> `Repository Provenance Plan`  [INFERRED]
  README.md → plans/repository-provenance.md
- `Graphify Catch-up Workflow` --conceptually_related_to--> `Copilot Instructions`  [INFERRED]
  .github/workflows/graphify-catchup.yml → .github/copilot-instructions.md
- `Technology Stack for User Frontend` --references--> `Architecture Diagram Maintenance`  [EXTRACTED]
  stack.md → diagrams/README.md
- `OKF Bundle Index` --references--> `Architecture Diagram Maintenance`  [EXTRACTED]
  index.md → diagrams/README.md

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
- **Matrix fabric** — diagrams_stack_architecture_desktop, diagrams_stack_architecture_ios, diagrams_stack_architecture_android, diagrams_stack_architecture_homeserver, diagrams_stack_architecture_push, diagrams_stack_architecture_federation [EXTRACTED 1.00]
- **OKF Bundle Components** — index_bundle, readme_vision, stack_specification, security_policy, log_updates [EXTRACTED]
- **Archify Layout & Chrome Management** — diagrams_stack_architecture_archify_readerlayout, diagrams_stack_architecture_archify_viewerchromelayout, diagrams_stack_architecture_archify_radar [INFERRED 0.80]
- **Security Guardrails** — security_policy, github_workflows_security_canary, github_workflows_ci [INFERRED]

## Communities (28 total, 0 thin omitted)

### Community 0 - "validate_okf_markdown.py"
Cohesion: 0.11
Nodes (18): changed_markdown_files(), check_bundle_index(), check_file(), _check_optional_shape(), _check_sources_and_footnotes(), frontmatter_body(), _indent_of(), is_excluded() (+10 more)

### Community 1 - "valid_document"
Cohesion: 0.12
Nodes (7): DuplicateIdTests, InvalidOriginTests, MissingRequiredFieldTests, SafeErrorMessageTests, SensitiveAndUnsupportedFieldTests, valid_document(), ValidRecordTests

### Community 2 - "validate_provenance.py"
Cohesion: 0.24
Nodes (9): _check_entry(), _check_non_empty_string(), _check_outcome(), load(), main(), _require_type(), _scan_sensitive_fields(), _sorted() (+1 more)

### Community 3 - "ConceptFrontmatterTests"
Cohesion: 0.23
Nodes (1): ConceptFrontmatterTests

### Community 4 - "test_validate_okf_markdown.py"
Cohesion: 0.21
Nodes (2): RepoBundleTests, write()

### Community 5 - "OKF Bundle Index"
Cohesion: 0.22
Nodes (8): Architecture Diagram Maintenance, Rendered Architecture Diagram, Security Canary Workflow, OKF Bundle Index, Repository Provenance Plan, How We Work, Security Reporting, Technology Stack for User Frontend

### Community 6 - "ReservedFileTests"
Cohesion: 0.31
Nodes (1): ReservedFileTests

### Community 7 - "SourcesAndFootnoteTests"
Cohesion: 0.33
Nodes (1): SourcesAndFootnoteTests

### Community 8 - "Matrix Homeserver"
Cohesion: 0.28
Nodes (9): Agent Gateway, Android Client, Desktop Client, Federated Homeservers, Matrix Homeserver, iOS Client, Local Extensions, Frontier Models (+1 more)

### Community 9 - "Archify.focus"
Cohesion: 0.31
Nodes (9): Archify.finder, Archify.focus, Archify.guidedViews, Archify.motionGovernor, Archify.radar, Archify.routeProbe, Archify.sourceEvidence, Archify.view (+1 more)

### Community 10 - "Copilot Instructions"
Cohesion: 0.39
Nodes (8): Change Reviewer Agent, Fact Checker Agent, Shared Safety Blocks, Technical Visualizer Agent, Copilot Instructions, Autonomous Review Policy, Mermaid Diagrams Skill, Graphify Catch-up Workflow

### Community 11 - "Frontmatter"
Cohesion: 0.33
Nodes (1): Frontmatter

### Community 12 - "Diagram Guide Module"
Cohesion: 1.00
Nodes (3): Diagram Guide Module, Route Probe Module, Semantic Lens Module

### Community 13 - "writePngToClipboard"
Cohesion: 0.67
Nodes (3): runCopy, runCopyShareCard, writePngToClipboard

### Community 14 - "test_gitleaks_ignore_regression.sh"
Cohesion: 1.00
Nodes (2): run_gitleaks(), test_gitleaks_ignore_regression.sh script

### Community 15 - "Archify Namespace"
Cohesion: 1.00
Nodes (1): Archify Namespace

### Community 16 - "Archify.intentTrace"
Cohesion: 1.00
Nodes (1): Archify.intentTrace

### Community 17 - "Archify.presentation"
Cohesion: 1.00
Nodes (1): Archify.presentation

### Community 18 - "Archify.readerLayout"
Cohesion: 1.00
Nodes (1): Archify.readerLayout

### Community 19 - "Pull Request Template"
Cohesion: 1.00
Nodes (1): Pull Request Template

### Community 20 - "Artifact Integrity Skill"
Cohesion: 1.00
Nodes (1): Artifact Integrity Skill

### Community 21 - "Decision and Design Skill"
Cohesion: 1.00
Nodes (1): Decision and Design Skill

### Community 22 - "Durable Agent Handoff Skill"
Cohesion: 1.00
Nodes (1): Durable Agent Handoff Skill

### Community 23 - "Evidence-First Engineering Skill"
Cohesion: 1.00
Nodes (1): Evidence-First Engineering Skill

### Community 24 - "CI Workflow"
Cohesion: 1.00
Nodes (1): CI Workflow

### Community 25 - "Graphify Workflow"
Cohesion: 1.00
Nodes (1): Graphify Workflow

### Community 26 - "Graphify Semantic Catch-up workflow"
Cohesion: 1.00
Nodes (1): Graphify Semantic Catch-up workflow

### Community 27 - "Update Log"
Cohesion: 1.00
Nodes (1): Update Log

## Knowledge Gaps
- **25 isolated node(s):** `Graphify Semantic Catch-up workflow`, `Mermaid Diagrams Skill`, `Graphify Catch-up Workflow`, `runCopy`, `runCopyShareCard` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 62 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConceptFrontmatterTests` connect `ConceptFrontmatterTests` to `test_validate_okf_markdown.py`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **What connects `Graphify Semantic Catch-up workflow`, `Mermaid Diagrams Skill`, `Graphify Catch-up Workflow` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `validate_okf_markdown.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11491935483870967 - nodes in this community are weakly interconnected._
- **Why does `ReservedFileTests` connect `ReservedFileTests` to `test_validate_okf_markdown.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Should `valid_document` be split into smaller, more focused modules?**
  _Cohesion score 0.12333333333333334 - nodes in this community are weakly interconnected._
- **Why does `SourcesAndFootnoteTests` connect `SourcesAndFootnoteTests` to `test_validate_okf_markdown.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._