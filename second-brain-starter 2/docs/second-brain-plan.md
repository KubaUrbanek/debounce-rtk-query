# Second Brain Starter — implementation record

Date: 2026-09-29. Status: Implemented as instruction-based skills; application-specific analysis has not been performed.

See [acceptance scenarios](second-brain-tests.md).

## Goal and scope

Build English Markdown knowledge from existing code through three manually invoked skills. Keep the default knowledge root at `/Projects/pkr-tool-docs`. Add repositories gradually. The user chooses each analyzed flow. Incremental updates, automation, scheduling and automatic commits are deferred.

## Agreed rules

- BR1: Map creates a repository overview, entry inventory and coverage without certifying flows. After successful validation, it records its own branch and full last_mapped_commit in the shared state, preserving flow checkpoints.
- BR2: Analyze traces only the requested flow, including relevant code and test evidence.
- BR3: Use one shared state object, keyed by repository and flow, with a repository map checkpoint and individual flow checkpoints, each containing document, branch and its full source SHA.
- BR4: Preserve completed state on interruptions; publish map or flow checkpoints only after the corresponding validated outputs are saved. Missing legacy map provenance is not inferred; it is established by the next successful map invocation.
- BR5: Organize derives shared business knowledge and per-repository technical notes from completed evidence; it does not advance checkpoints.
- BR6: Read a pinned version of the configured remote branch; protect working-tree changes and report unreachable prior checkpoints.
- BR7: Keep evidence, inference and unknowns distinct. Never certify one repository using another repository's SHA.

## Implementation steps and acceptance

| Step | Implementation | Completion criterion |
| --- | --- | --- |
| P1 | Shared file/config/state contract | AC1: All skills agree on layout and provenance rules |
| P2 | Map skill | AC2: Validated map and inventory have a matching map checkpoint and do not certify process analysis |
| P3 | Analyze skill and document template | AC3: One selected flow produces a source-backed document and matching state while preserving other entries |
| P4 | Organize skill | AC4: Shared claims trace to completed flows; state is unchanged |
| P5 | OpenCode README, V1 configuration template and package | AC5: User can configure, invoke each step, and interpret incomplete work without a coordinator |

## Limits and handoff

These are agent instructions, not a deterministic parser or transactional persistence service. A filesystem write sequence cannot atomically commit every Markdown and JSON file together; state is written last and mismatches require revalidation. Run invocations sequentially. Map coverage depends on discovered entry mechanisms and must state limitations. The supplied archive does not contain production repository access or analysis results.

Start with README, configure one source repository, then invoke map. Update process notes through an explicit selected-flow analysis; do not add an incremental framework without a later request.

## OpenCode packaging

Use project-local `.opencode/skills` in the central knowledge workspace. Provide one OpenCode V1 permission template. Keep agent/provider choices untouched. Keep all repository-specific outputs, including flows and drafts, under repositories/<repo-id>/. Source projects are added individually to the same knowledge root.
