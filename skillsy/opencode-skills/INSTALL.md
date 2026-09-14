# OpenCode skills: installation

The bundle contains two independent OpenCode Agent Skills:

- `workflow-optimizer` analyzes sanitized OpenCode session history and recommends workflow improvements.
- `skill-optimizer` audits and improves `SKILL.md` definitions.

## Global installation

Copy both skill directories into the global OpenCode skill directory:

```bash
mkdir -p ~/.config/opencode/skills
cp -R workflow-optimizer skill-optimizer ~/.config/opencode/skills/
```

## Project-only installation

From a repository root:

```bash
mkdir -p .opencode/skills
cp -R workflow-optimizer skill-optimizer .opencode/skills/
```

OpenCode discovers each folder by its `SKILL.md`. Ensure the intended agent has access to the `skill`, `read`, and `bash` tools. The workflow collector requires Python 3 and the `opencode` executable on `PATH`.

Example requests:

```text
Use workflow-optimizer to review my last 30 sessions in this project and tell me how to reduce rework.
```

```text
Use skill-optimizer to audit .opencode/skills/my-skill without editing it.
```
