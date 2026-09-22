# Agreed repository synchronization design

Status: specification only; runtime implementation is pending. This document does not
override the executable contracts in the existing package. See the [guide](../SKILLS-GUIDE.md)
and [prompts](../PROMPTS.md).

The working name is `sync-repository-second-brain`. It will replace bootstrap and the
team daily report, leaving five independent skills. One invocation processes one user-selected
repository and one remote branch configured in fixed-schema YAML. The existing YAML parser
does not support that new branch field yet; do not add it to version 2 configuration.

## Source analysis and publication

- No checkpoint: fully analyze the current pinned source snapshot, not every historical commit.
- Existing checkpoint: analyze the cumulative changes strictly after that commit and complete
  affected flows, including callers of shared dependencies, configuration and SQL/NoSQL changes.
- Expand automatically, up to the entire selected repository, if impact cannot be bounded reliably.
- Start discovery at execution entry points; explicitly account for remaining in-scope files.
  Exclude tests and identified generated/dependency files. Keep repository documents in scope,
  with code winning contradictions. Do not execute project code or connect to databases.
- Use a durable queue of any number of tasks with at most four concurrent workers by default.
  Retire each finished worker and spawn a fresh one for subsequent work. Preserve detailed
  findings, evidence and independent review; never substitute sentence counts for quality.
- Update knowledge directly, with no team summary in inbox. Domain notes remain nontechnical,
  shared across repositories; technical and database details remain properly scoped. New ADRs
  are proposed and accepted decision history is preserved.
- Code automatically wins on implemented behavior in the selected repository. Preserve variants
  belonging to other repositories. Describe only the known side of changed inter-service
  communication and mark the other side for verification during its own synchronization.
- Remove descriptions of deleted behavior and adjust related notes and links. Delete a note
  only when it has no remaining relevant substance, including other-repository variants.
  Do not archive those obsolete knowledge notes. Preserve ADR history.

## Checkpoints and interruptions

- Save a new checkpoint only after complete successful publication of knowledge and links.
  Failed or partial analysis must not skip changes on the next invocation.
- Pin the target once per run. Resume interrupted analysis at that exact snapshot, reusing
  completed tasks. Remote commits arriving meanwhile belong to the next invocation.
- No new commit means no knowledge update. A changed commit with no documentation impact
  still needs accounted analysis before the checkpoint can advance.
- If continuation from the saved checkpoint is impossible, ask the user which commit to use.
  Treat the answer as already documented: the range starts strictly after it. Validate the
  replacement baseline; never silently reset to a full scan or choose another commit.
- Persistent failures block publication and await the user's reaction.
- Do not migrate or import old bootstrap state. There is no existing old-bootstrap
  documentation to support, and no separate repair mode is requested.

## Other skills

Manual inbox distillation remains inbox-based and asks about factual conflicts or ambiguous
scope. Personal daily remains today-only and includes eligible conversations and all own
collected commits, including local alternatives. Thought refinement and finished-note linking
remain independent. All use English Markdown and meaningful links, communicate in Polish,
and avoid reading archive. Deterministic work belongs in bundled Bash/Python stdlib scripts.

## Implementation acceptance scenarios

1. First synchronization covers every included source range before publishing useful detailed
   domain, technical and database topics; no old bootstrap migration is attempted.
2. A second synchronization analyzes changes after the checkpoint, including unchanged callers
   affected by shared logic. A broad configuration change can trigger a complete scan.
3. A failure during analysis or publication leaves the previous published checkpoint intact.
   Resume uses the pinned target and durable task results even if the remote branch advances.
4. Rewritten or unavailable baseline history prompts for a user-selected commit. That commit
   is excluded from the new change range; an invalid answer blocks rather than being guessed.
5. Removed functionality disappears from current documentation without archival or broken links;
   shared notes retain other projects' valid content and architectural history remains available.
6. A cross-service change marks unverified remote-side behavior without scanning another repo.
7. New source synchronization produces no inbox team report and does not consume manual inbox
   sources, personal activity or thought drafts. Existing independent workflows remain usable.
8. No new commit produces no rewrite. A successfully analyzed documentation-neutral change
   advances the checkpoint without manufacturing knowledge content.
