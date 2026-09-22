# Acceptance scenarios

See [setup](../SETUP.md), [skill guide](../SKILLS-GUIDE.md) and [prompts](../PROMPTS.md).

| Scenario | Expected result |
| --- | --- |
| No prior state | Full current-source scan, entry-point tasks and residual coverage before publication |
| Completed legacy bootstrap | Import its commit as already documented, preserving old state and knowledge |
| Missing/invalid imported commit | Ask user for an already documented valid ancestor; no silent reset |
| Incomplete legacy bootstrap | Block and explain that its checkpoint is not published |
| New commits | Cumulative baseline-to-target changes and affected complete flows |
| Shared dependency changes | Include unchanged impacted entry points; full expansion is allowed |
| Changed file omitted from scope | Script rejects impact plan |
| History rewritten or configured branch changed | Ask for replacement ancestor, exclude that commit from range |
| Interrupted analysis | Same pinned target and durable completed results on resume |
| New remote commits during a run | Process them on the next invocation |
| Interrupted publication | Recover documents, deletions and links; keep previous checkpoint |
| External edit during interrupted publication | Stop recovery before erasing external changes |
| No new commits | No document or state rewrite |
| Only documentation-neutral changes | Account for changes and review before checkpoint advancement |
| Removed feature | Remove obsolete descriptions and topics, repair links, no archival |
| Shared note or accepted ADR | Preserve other-project variants and decision history |
| Technical domain prose | Independent review requests nontechnical wording and separate technical notes |
| Inbox and daily in either order | Archive only after all required stages consume the current source |
| Local unpushed experiments | Included in today's personal activity |
| Retired thoughts | No reads, writes, graph changes or automatic refinement |
| Package upgrade | Exactly three active skill directories; old versions backed up outside active directory |

Runtime tests exercise temporary real Git repositories, synthetic analysis/review results, guarded
publication, rollback, source hashes, links and date handling. They do not measure a live model's
understanding or prove workplace authentication. Test the initial actualization on one selected
repository and inspect its domain/technical depth before relying on generated knowledge.
