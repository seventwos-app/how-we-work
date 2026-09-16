---
type: Guide
title: Architecture Diagram Maintenance
description: Reproducible instructions for validating and rendering the Archify source used by the Technology Stack specification.
tags: [architecture, diagrams, archify, documentation]
---

# Architecture Diagram Maintenance

[`stack.architecture.json`](stack.architecture.json) is the maintainable source for the system architecture diagram in [Technology Stack](../stack.md). It targets Archify `v2.16.0`; the generated HTML is self-contained and can be opened without installing application dependencies.

**Live, interactive view**: once this change lands on `main`, the rendered diagram is published via GitHub Pages at [seventwos-app.github.io/how-we-work/diagrams/stack.architecture.html](https://seventwos-app.github.io/how-we-work/diagrams/stack.architecture.html) — no download required to click through it. This is a work-in-progress reference; regenerate and re-publish it (by pushing the updated HTML) whenever the source JSON changes.

Archify is a documentation tool, not a runtime dependency. Download its pinned MIT-licensed release outside the repository, verify it, and use that copy to regenerate the artifact:

```sh
ARCHIFY_HOME="${TMPDIR:-/tmp}/archify-v2.16.0"
ARCHIFY_ZIP="${TMPDIR:-/tmp}/archify-v2.16.0.zip"

curl -fL \
  https://github.com/tt-a1i/archify/releases/download/v2.16.0/archify.zip \
  -o "$ARCHIFY_ZIP"
printf '%s  %s\n' \
  '4c59fa6557a2385beaaef8c7219cc414573acc9f0c30a932d5053b0b20689a46' \
  "$ARCHIFY_ZIP" |
  shasum -a 256 -c -
mkdir -p "$ARCHIFY_HOME"
unzip -q -o "$ARCHIFY_ZIP" -d "$ARCHIFY_HOME"

ARCHIFY_UPDATE_CHECK_DISABLED=1 \
node "$ARCHIFY_HOME/archify/bin/archify.mjs" deliver \
  architecture \
  diagrams/stack.architecture.json \
  diagrams/stack.architecture.html \
  --quality standard \
  --json
```

After regeneration, open `diagrams/stack.architecture.html` and inspect the complete view plus each guided view. Commit the JSON and HTML together so future changes remain reproducible and reviewable.
