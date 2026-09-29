---
name: second-brain-analyze
description: Analyze one user-selected business flow from existing source code and tests, document its behavior, and record its branch and completed analysis commit in the shared state.json. Use for a named process, endpoint, consumer, job, or entry method. Never automatically analyze every flow.
---

# Analyze one selected flow

Read [the shared contract](references/contract.md) and [the flow template](references/flow-template.md).

1. Read configuration, the repository map, coverage and existing flow/state entries. Resolve the user's named process, endpoint, consumer, job or method. If several plausible processes match, ask one focused question. Do not select another process or expand to all remaining flows. If no map exists, explain the missing prerequisite and request `second-brain-map` first; do not invoke it automatically.
2. Fetch and pin the configured branch. Apply the contract's old-checkpoint ancestry checks before replacing an existing flow. This skill performs a complete selected-flow analysis at the pinned version, not a diff-only refresh. Compare `map.last_mapped_commit` with the pinned analysis snapshot. If the map is older or its checkpoint is missing, verify the selected entry against the new snapshot and flag relevant inventory changes. Never advance the map checkpoint or its discovery metadata from a selected-flow analysis.
3. Trace the selected operation through actual dispatch and implementations: inputs, permissions, validation, decisions, persistence, configuration, transactions, external calls, events, return values and error paths. Inspect relevant implementations behind interfaces; do not stop at a facade. Inspect consumers of emitted events within the selected repository when needed to understand the operation's effects. Include all materially different branches of this flow.
4. Read relevant tests and fixtures. Use them to find edge cases and expected behavior. Inspect migrations or configuration where they alter behavior. Do not run tests or application code by default. Never call read-only inspection an executed test. Track unresolved reachable local paths as unfinished work.
5. Write a draft using the template. Cite paths and symbols next to important rules and effects. Record business meaning, not a call-stack dump. Document external boundaries and conflicting evidence honestly. Preserve the prior completed document while working. A clearly bounded external unknown can coexist with completed local analysis; unexplored reachable local logic cannot.
6. Validate the description against implementation and tests: all entry variants accounted for, rules traceable, failures considered, links valid, no unsupported intent or guarantees. If interrupted, retain a labeled draft and leave the previous checkpoint unchanged. On a later invocation revalidate draft provenance; if the pinned source version changed, reread affected evidence before publication.
7. Publish `repositories/<repo-id>/flows/<flow-id>.md`, link it from coverage, and mark the corresponding entries analyzed. Write the shared state entry last under `repositories[repo-id].flows[flow-id]` with document path, configured branch and actual full SHA. Follow preservation and safe-write rules in the contract.
8. Report the selected scope, branch/SHA, documented evidence, external unknowns, and whether publication/checkpoint succeeded. Stop. Offer another analyze invocation or organize as next manual steps without executing them.

## Done means

One requested flow has a validated English description, coverage links and a matching completed checkpoint. If this is impossible, provide a draft and precise blockers without claiming completion.
