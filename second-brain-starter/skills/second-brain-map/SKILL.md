---
name: second-brain-map
description: Map an existing code repository into a second-brain knowledge base. Use when the user wants the initial repository map, entry-point inventory, and candidate flows before choosing a process to analyze. Do not perform full flow analysis or incremental synchronization.
---

# Map a repository

Read [the shared contract](references/contract.md) before writing anything.

1. Resolve the requested repository and knowledge root. Read applicable project instructions and existing knowledge/configuration. Ask only for missing repository location or configured remote branch. Add the selected repository to configuration without changing other entries.
2. Fetch and pin the configured remote branch using the contract. Record the branch and full SHA in both the map and inventory. The map snapshot is not a completed flow checkpoint.
3. Inspect the tracked source inventory, build files, module layout, configuration, migrations, test layout and existing documentation. Exclude generated output, vendored dependencies and binaries; record exclusions. Existing prose is a hypothesis to verify in code.
4. Identify technologies, module responsibilities, persistence, integrations and observed architectural boundaries. Label tentative interpretations. Do not produce a class-by-class catalog.
5. Discover entry points throughout the in-scope repository: HTTP/GraphQL handlers, message consumers, scheduled jobs, commands, startup hooks, event handlers and framework-specific equivalents. For frontend repositories also inspect routes, UI actions, state effects and API calls. For libraries inspect public APIs. Follow repository-specific registration mechanisms, not only common annotation patterns.
6. Create `repositories/<id>/map.md` and `coverage.md`. Give each entry point a source path/symbol, candidate business flow, and status. Group related entries where justified. List scan limitations and unresolved registrations. Highlight 2-3 useful starting processes without analyzing or selecting one automatically.
7. On rerun, preserve completed analyses and their statuses unless evidence warrants flagging them for review. Do not erase an entry with a completed document just because discovery changed; explain the discrepancy. Preserve every existing flow checkpoint; map never certifies detailed flow analysis.
8. Check paths/symbols against the snapshot, map-to-coverage consistency, and JSON syntax. Only after both outputs are complete and validated, publish them and write `repositories[repo-id].map` in the shared state last, with `document`, configured `branch`, and real full `last_mapped_commit`. Preserve all flow entries and other repositories. If mapping is interrupted or blocked, keep the previous completed map checkpoint; do not publish a partial inventory as completed. Report discovered coverage, exclusions, output paths and the recorded map checkpoint. Suggest an explicit `second-brain-analyze` invocation for a user-selected flow, then stop.

## Done means

A repository map and actionable entry-point inventory exist, with matching snapshot provenance in both documents and the shared map checkpoint, plus explicit gaps. No flow is marked analyzed by this skill. No next skill is invoked automatically.
