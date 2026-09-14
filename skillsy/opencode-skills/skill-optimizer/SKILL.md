---
name: skill-optimizer
description: Audit, debug, or improve OpenCode Agent Skills for activation quality, instruction usefulness, progressive disclosure, portability, safety, and maintainability. Use when asked to review or optimize one or more SKILL.md definitions; not for ordinary tasks that merely use a skill.
metadata:
  version: "1.0.0"
  target-spec: "opencode-agent-skills"
---

# Skill Optimizer

Improve skills with the smallest evidence-backed changes. Preserve the skill author's intent and avoid turning one failure into a universal rule.

## Select the mode

- **Audit:** inspect and report; do not edit.
- **Optimize:** inspect, patch the requested skill, validate it, and show the diff.
- **Debug activation:** focus on discovery paths, name/description quality, duplicates, and skill permissions.
- **Evidence review:** compare the skill with relevant session failures or successes supplied by the user.

Infer the mode from the request. `Review`, `audit`, or `why does this trigger` is read-only. `Fix`, `improve`, `optimize`, or `update` authorizes edits only to the named skill.

## Establish the target

Use an explicit path when supplied. Otherwise search the current project first, followed by OpenCode's global locations:

- `.opencode/skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`
- `~/.config/opencode/skills/*/SKILL.md`
- `~/.agents/skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

If several skills plausibly match the user's name, list the candidates and ask which one to change. Never silently edit all duplicates.

Run the structural checker before semantic review:

```bash
python3 <skill-directory>/scripts/check_skills.py <target-skill-directory> --format text
```

Read [references/audit-rubric.md](references/audit-rubric.md) for semantic review. If real sessions are supplied, use them as stronger evidence than hypothetical examples.

## Audit

Inspect the complete `SKILL.md` and every supporting file that its workflow requires. Check:

- whether the name and description cause correct activation and avoid nearby unrelated tasks;
- whether instructions add non-obvious decisions instead of generic advice;
- whether constraints reflect real correctness or safety needs;
- whether conditional detail is moved to linked references;
- whether scripts replace repeated fragile mechanics and actually run;
- whether paths, tool names, and assumptions are valid in OpenCode;
- whether the skill preserves user authorization boundaries;
- whether references are reachable and duplicated guidance has one source of truth.

Do not optimize for brevity alone. A shorter skill is better only when it retains the decisions that make it useful.

## Optimize

Before editing, state the main failure mode and intended minimal correction. Then:

1. Preserve supported frontmatter and the original capability.
2. Tighten the description only when activation is part of the problem.
3. Remove repetition, generic model instructions, and speculative edge cases.
4. Move substantial conditional procedures to references when that reduces default context.
5. Add scripts only for deterministic work likely to recur.
6. Update links and callers when moving content.
7. Run the structural checker and any changed script.
8. Review the final diff for scope creep.

Do not rewrite a functioning skill wholesale when a narrow patch fixes the demonstrated issue. Do not edit OpenCode configuration, other skills, or shared rules unless the user explicitly includes them.

## Report

For an audit, provide a compact table with `finding`, `evidence`, `impact`, and `recommended change`, ordered by impact. Distinguish structural errors from judgment calls.

For an optimization, summarize what behavior changed, report validation results, and show the important diff. Mention remaining uncertainty and propose a realistic positive and negative trigger test. Do not claim improvement without either observed session evidence or a clearly stated hypothesis.
