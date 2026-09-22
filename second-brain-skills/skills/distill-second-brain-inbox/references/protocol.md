# Runtime protocol

Domain output under knowledge/domain/ is for nontechnical users. Preserve business rules,
conditions and outcomes, while routing class names, REST calls, transport and storage internals
to technical notes. Technical/source links on domain pages use neutral labels. This audience
separation changes presentation, not the allowed evidence sources or the requirement for detail.

The six skills contain identical copies of this versioned brain runtime; each can run
independently. The bootstrap skill additionally contains its own snapshot/coverage runtime
and publication protocol. Thought refinement and linking use their additional thoughts runtime.
The five ongoing skills use one agent; bootstrap delegates real
explorers and a fresh reviewer, capped by `max_parallel_agents` (default 4) active workers.
This is a concurrency cap, not a cap on task count or total worker identities. Bootstrap
discovers execution entry points, queues end-to-end flow and residual tasks, and replaces
completed workers with fresh subagents as slots become free. Its task queue commands belong
to bootstrap.sh only; the other five workflows keep their single-agent/source restrictions.
Use Bash explicitly if execute permission was lost during unzip:

```bash
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml check
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml init
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml system --date 2026-09-16
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml personal
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml inventory --stage knowledge
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml read knowledge/domain/case-lifecycle.md
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml publish /tmp/brain-plan.json
bash SKILL_DIR/scripts/brain.sh --config /absolute/config.yaml validate
```

Collection prints JSON to stdout. Redirect it to a temporary directory outside second brain
if needed. Read every relevant result; do not truncate patches and pretend complete analysis.
Temporary data may contain source code. Remove your own temporary files after completion.
All persistent user-facing notes are Markdown. Configuration is YAML; runtime locks, internal
bootstrap JSON and bare snapshot storage are implementation artifacts, not knowledge notes.
Never scan `.state/` as active knowledge or use ordinary `publish` for a bootstrap draft.
An interrupted bootstrap publication blocks other writes until bootstrap recovery completes.

## Shared knowledge layout

Use `knowledge/domain/` for shared domain topics, `knowledge/technical/REPO_ID/` for project
implementation and `knowledge/technical/shared/` for supported common principles. SQL and
NoSQL knowledge belongs separately in `knowledge/technical/REPO_ID/database/`, linked to the
relevant domain and application notes. This applies to inbox updates and initial analysis.
Keep `knowledge/essence.md` as a concise navigation guide; ADRs remain under `architecture/`.
The ordinary inbox workflow asks about contradictions before changing knowledge. The one-time
bootstrap workflow instead corrects selected-project facts using its pinned source code,
preserving unrelated project variants. Do not apply that exception to inbox distillation.

## Publication schema

Write the semantic payload into a temporary JSON plan using your file-writing tool.
File placement, replacement, hashing, graph maintenance and archival are performed only by publish.

```json
{
  "stage": "knowledge",
  "human_review_complete": true,
  "documents": [
    {
      "path": "knowledge/domain/case-lifecycle.md",
      "content": "# Case lifecycle\n\nExplicit sourced knowledge.\n\n## Sources\n\n- [Meeting](../../inbox/meeting.md)\n",
      "expected_sha256": "hash returned by read, omit for new files"
    }
  ],
  "processed": [
    {"path": "inbox/meeting.md", "hash": "hash returned by inventory"}
  ]
}
```

stage is system, daily or knowledge. processed is empty for system.
For daily, include only eligible notes actually reflected in the report.
For knowledge, a source with no durable content may have no generated topic.
The agent must verify that all processed sources were fully accounted for; hashes prove
the version consumed, not the semantic quality of the synthesis.

Before an update, use read to get exact content and expected_sha256. On mismatch reread
and merge; never remove the guard to bypass it. No partial document is marked complete
until graph validation succeeds. Individual writes are atomic, but multi-file publication
is not transactional: after interruption inspect active outputs and replan; do not replay
the same plan blindly. Unmarked inputs remain pending and are safe to reprocess.

## Metadata

Flat YAML frontmatter uses the fixed fields in the template. No YAML aliases, tags,
arbitrary nested structures, inline comments, or multiline scalar syntax. Repositories
are a comma-separated list of configured IDs, shared or unknown.
The runtime automatically writes daily_hash, daily_output and knowledge_hash.
Do not edit these manually. Hashes exclude processing fields and generated graph links.
Changing date, content or include_in_daily invalidates completion. Notes without a valid
date stay in inbox even after knowledge extraction.

## Source movement and links

Inbox and archive mirror relative paths. Archive is not scanned for content.
Only existence checks and renames of known system report paths are allowed for restore.
Use restore before regenerating an archived system report; it preserves identity.
Archive on publication only after the current content has been consumed by knowledge
and, if include_in_daily=true, daily. Invalid dates stay pending.
Generated graph blocks are owned by the runtime. It creates a root index and reciprocal
links for active notes. Links to archived sources remain navigable for the user, but
archive files themselves are not opened or rewritten. Do not demand backlinks from
archive as that would conflict with the archive policy.

## Historical evidence and local commits

System collection uses merged MR diffs and merge timestamps, never today's working tree.
Describe what those changes established by the requested date; do not claim a complete
historical system snapshot from a day's diffs. Order overlapping changes by merge time.
MR descriptions can be edited later, so use historical diff evidence for implementation
claims and qualify unsupported rationale. Diff limitations are explicit errors.
Personal collection includes commits reachable from local branches, remote refs and HEAD.
Unreachable/deleted history and commits on another machine are unavailable.
SHA deduplication removes branch duplicates, not distinct experimental commits.
Merge commits may contain others' changes: describe the user's integration work without
claiming sole authorship of the entire merged patch.
