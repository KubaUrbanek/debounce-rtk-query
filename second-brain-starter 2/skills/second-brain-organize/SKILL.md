---
name: second-brain-organize
description: Organize already analyzed second-brain flow documents into shared business knowledge, per-repository technical knowledge, and an agent navigation index. Use after one or more selected flow analyses. Do not analyze new flows or advance source-code checkpoints.
---

# Organize established knowledge

Read [the shared contract](references/contract.md).

1. Read configuration, state, maps, coverage, completed flow documents and existing shared knowledge. Treat a flow as completed only when its document provenance matches its state entry. Flag absent or mismatched flow checkpoints; exclude drafts and unmatched revisions from established claims. Separately compare map/inventory provenance with the repository map checkpoint. If absent or mismatched, flag the inventory as unverified without preventing organization of independently completed flow evidence.
2. Extract a shared business glossary and rules from completed flow evidence. Link each item to supporting flow documents and original source references. Merge concepts only when their semantics agree. Preserve distinct same-named concepts where evidence differs. Do not silently resolve contradictions or invent business motivation.
3. Write per-repository technical notes only for patterns demonstrated by the analyzed evidence. A single example is an observed local approach, not a repository-wide convention. Keep business knowledge shared and technical implementation details scoped to their repository.
4. Link cross-repository behavior only when both sides are supported by completed analyses, otherwise mark the boundary as unverified. Preserve distinct branch/commit provenance. Do not claim different repository snapshots represent one synchronized runtime deployment.
5. Update `index.md` with a compact system orientation, links to maps, processes, concepts, technical notes, coverage and open questions. Include coding-agent instructions: choose relevant flow notes, inspect their checkpoints and sources, verify current code before changing it, and treat unknowns as unknowns. Avoid loading the entire knowledge base into every task.
6. Reduce duplication carefully. Keep a canonical location for shared rules and link to it, while retaining enough context and evidence in each flow for independent understanding. Preserve flow scope and provenance; do not change behavior claims without source reanalysis. Preserve useful manual notes and unrelated content.
7. Check relative links, duplicate/conflicting terms, draft exclusion, and traceability of shared claims. Do not fetch repositories, reanalyze code, update `state.json`, or mark coverage newly analyzed. If evidence is insufficient, add an open question linked to the affected flow.
8. Report what was organized, inconsistencies and suggested next user-selected analyses. Stop without invoking another skill.

## Done means

The index helps a coding agent locate relevant evidence; shared claims remain traceable to completed analyses; all flow checkpoints remain unchanged.
