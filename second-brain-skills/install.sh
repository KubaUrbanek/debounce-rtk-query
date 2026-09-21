#!/usr/bin/env bash
set -euo pipefail
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"
CONFIG_DIR="$HOME/.config/second-brain"
command -v python3 >/dev/null
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
command -v git >/dev/null
command -v glab >/dev/null
mkdir -p "$SKILLS_DIR" "$CONFIG_DIR"
for skill in daily-develop-second-brain my-work-second-brain distill-second-brain-inbox bootstrap-second-brain refine-second-brain-thoughts link-second-brain-notes; do
  if [[ -e "$SKILLS_DIR/$skill" ]]; then
    backup_dir="$(mktemp -d "$CONFIG_DIR/skill-backup.XXXXXX")"
    mv "$SKILLS_DIR/$skill" "$backup_dir/$skill"
    printf 'Previous version preserved: %s\n' "$backup_dir/$skill"
  fi
  cp -R "$PACKAGE_DIR/skills/$skill" "$SKILLS_DIR/$skill"
done
if [[ ! -e "$CONFIG_DIR/config.yaml" ]]; then
  cp "$PACKAGE_DIR/config.example.yaml" "$CONFIG_DIR/config.yaml"
fi
cp "$PACKAGE_DIR/templates/inbox-note.md" "$CONFIG_DIR/inbox-note-template.md"
cp "$PACKAGE_DIR/templates/thought-draft.md" "$CONFIG_DIR/thought-draft-template.md"
printf 'Installed. Edit %s, then run check and init as described in SETUP.md.\n' "$CONFIG_DIR/config.yaml"
