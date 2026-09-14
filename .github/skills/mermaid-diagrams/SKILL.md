---
name: mermaid-diagrams
description: "Expert guidance for generating clean, syntax-valid, and visually compelling Mermaid diagrams. Use when creating or improving system topologies, sequence flows, state diagrams, class relationships, data pipelines, or architecture charts in markdown documentation."
---

# Mermaid Diagramming Standards

Design diagrams that clarify technical complexity instead of decorating it. Every node, edge, and label must earn its place.

## Core Visual Principles (Tufte & Cairo)

1. **High Data-to-Ink Ratio**: Eliminate redundant borders, decorative icons, and nested frames that don't add structural information.
2. **Predictable Reading Direction**: Default to Top-to-Bottom (`TD`) for component hierarchies and request lifecycles; Left-to-Right (`LR`) for pipelines, data flows, and chronological progressions. Never create diagonal chaos.
3. **Semantic Node Shapes**:
   - `[Service / Process]` — Standard rectangle for computational services and web applications.
   - `([Runtime / Shell])` — Stadium/pill shape for host shells and platforms (e.g. Tauri, Node.js).
   - `[(Database / Storage)]` — Cylinder for persistence stores, databases, and caches.
   - `{{External System}}` — Hexagon for external third-party services and APIs.
   - `[/Queue / Stream/]` — Parallelogram for message brokers, queues, and event streams.
   - `((Start / End))` — Circle for lifecycle boundaries.

## Diagram Rules by Type

### 1. Architecture & Component Diagrams (`graph TD` or `graph LR`)
- **Safe Node IDs**: Use alphanumeric identifiers without spaces or special characters (e.g., `ClientUI["Client UI (React 19)"]`). Always place display strings in double quotes.
- **Meaningful Subgraphs**: Use `subgraph Name ["Display Title"]` to group tightly-coupled modules or trust boundaries (e.g., Presentation, Host Shell, Network, Cloud).
- **Edge Semantics**:
  - `-->|Protocol / Data|` for synchronous request or direct dependency.
  - `-.->|Async / Event|` for asynchronous messages, signals, or background sync.
  - `<-->|Bidirectional IPC|` for duplex communication channels.

### 2. Sequence Diagrams (`sequenceDiagram`)
- **Autonumbering**: Always enable `autonumber` on multi-step workflows.
- **Explicit Participants**: Declare actors and participants at the top with clear display aliases:
  ```mermaid
  sequenceDiagram
      autonumber
      actor User as Human Collaborator
      participant UI as Desktop Client (React)
      participant Core as Host Core (Rust / Tauri)
      participant AI as Agent Service
  ```
- **Control Blocks**: Use `loop`, `alt`, and `opt` frames to illustrate retries, error recovery, or optional paths.
- **Activation Boxes**: Use `activate` / `deactivate` or `+` / `-` only when clarifying which entity holds active execution state.

### 3. State & Flowchart Hygiene
- Keep node label text concise (under 5 words). Put detailed technical parameters in surrounding prose.
- Limit crossing lines: arrange nodes so connecting edges flow naturally without criss-crossing.
- Maximize compatibility: Avoid raw HTML tags (`<br/>`, `<b>`) inside Mermaid strings where plain text or clean newlines work.

## Common Syntax Pitfalls to Avoid
- **Unescaped Quotes**: Never use bare double quotes inside node labels; use single quotes or sanitize.
- **Parentheses in Unquoted Labels**: Writing `Node(Service (API))` breaks Mermaid parsing. Write `Node["Service (API)"]`.
- **Reserved Keywords in IDs**: Do not use `end`, `style`, `graph`, `subgraph` as node IDs.
