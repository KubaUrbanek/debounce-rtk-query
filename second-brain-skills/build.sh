#!/usr/bin/env bash
set -euo pipefail
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for skill in second-brain-actualize second-brain-my-work second-brain-process-inbox; do
  mkdir -p "$PACKAGE_DIR/skills/$skill/references" "$PACKAGE_DIR/skills/$skill/scripts"
  cp "$PACKAGE_DIR/runtime/brain.py" "$PACKAGE_DIR/skills/$skill/scripts/brain.py"
  cp "$PACKAGE_DIR/runtime/protocol.md" "$PACKAGE_DIR/skills/$skill/references/protocol.md"
  cp "$PACKAGE_DIR/runtime/analysis-depth.md" "$PACKAGE_DIR/skills/$skill/references/analysis-depth.md"
done
for file in bootstrap.py actualize.py; do
  cp "$PACKAGE_DIR/runtime/$file" "$PACKAGE_DIR/skills/second-brain-actualize/scripts/$file"
done
