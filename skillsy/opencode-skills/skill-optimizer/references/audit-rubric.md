# OpenCode skill audit rubric

Score each dimension from 0 to 3 only to compare revisions of the same skill. The explanation matters more than the total.

| Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Discovery | Missing or misleading | Broad/ambiguous | Mostly discriminating | Clear trigger and useful boundary |
| Decision value | Generic advice | Few useful constraints | Several task-specific decisions | Concise non-obvious guidance throughout |
| Workflow fit | Invalid assumptions | Fragile/manual | Mostly executable | Tools, paths, and fallbacks are realistic |
| Context efficiency | Large unrelated load | Repetitive | Mostly focused | Progressive disclosure matches modes |
| Safety and scope | Expands authority | Important gaps | Boundaries mostly clear | Mutations and stopping conditions are explicit |
| Maintainability | Broken/duplicated | Hard to update | Reasonably organized | One source of truth with validated helpers |

## Activation review

Write at least three requests that should activate the skill and three nearby requests that should not. Evaluate the frontmatter description against those examples. Put task details in the body; the description should identify capability and boundary, not summarize every step.

Check that:

- the directory name equals `name`;
- the name matches `^[a-z0-9]+(-[a-z0-9]+)*$`;
- `description` is specific and between 1 and 1024 characters;
- only OpenCode-supported frontmatter is relied upon;
- duplicate names do not create ambiguous discovery;
- skill permissions do not hide the target from the intended agent.

## Instruction review

Keep instructions that change a capable agent's choices. Challenge lines that merely say to be careful, accurate, concise, or follow best practices. Preserve domain rules, authorization boundaries, ordering constraints, failure behavior, and non-obvious tool choices.

Use progressive disclosure when a mode-specific section is substantial and not needed for most invocations. Every moved reference must be linked from `SKILL.md` at the point where it becomes relevant.

## Evidence review

When session evidence exists, classify each problem as:

- activation failure;
- missing instruction;
- instruction ignored or ambiguous;
- invalid tool/environment assumption;
- excessive context or conflicting guidance;
- unrelated failure that the skill should not absorb.

Prefer fixing the demonstrated class of failure. One unusual session is not enough to add a universal rule unless safety or data loss is involved.

## Validation

Structural validation is necessary but insufficient. For meaningful changes, define:

- a positive trigger request;
- a negative near-neighbor request;
- one realistic task that exercises the changed instruction;
- the observable behavior that would count as success.

Do not benchmark by recursively launching costly agents unless the user asks for an evaluation and approves the relevant cost and side effects.
