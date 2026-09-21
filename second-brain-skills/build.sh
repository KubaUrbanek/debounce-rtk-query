#!/usr/bin/env bash
set -euo pipefail
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for skill in daily-develop-second-brain my-work-second-brain distill-second-brain-inbox bootstrap-second-brain refine-second-brain-thoughts link-second-brain-notes; do
  mkdir -p "$PACKAGE_DIR/skills/$skill/references"
  cp "$PACKAGE_DIR/runtime/brain.py" "$PACKAGE_DIR/skills/$skill/scripts/brain.py"
  cp "$PACKAGE_DIR/runtime/protocol.md" "$PACKAGE_DIR/skills/$skill/references/protocol.md"
done
for skill in refine-second-brain-thoughts link-second-brain-notes; do
  cp "$PACKAGE_DIR/runtime/thoughts.py" "$PACKAGE_DIR/skills/$skill/scripts/thoughts.py"
  cp "$PACKAGE_DIR/runtime/thoughts-protocol.md" "$PACKAGE_DIR/skills/$skill/references/thoughts-protocol.md"
done
cp "$PACKAGE_DIR/runtime/bootstrap.py" "$PACKAGE_DIR/skills/bootstrap-second-brain/scripts/bootstrap.py"
