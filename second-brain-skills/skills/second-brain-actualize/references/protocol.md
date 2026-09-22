# Shared runtime protocol

The three independent skills share brain.py. Actualization additionally uses actualize.py and
its internal bootstrap.py coverage engine. Only actualization delegates to real subagents;
inbox processing and personal daily each use one agent. Speak Polish; write English Markdown.
Read [analysis depth](analysis-depth.md). Archive and personal thoughts are outside reading scope.

## Commands

```bash
bash SKILL_DIR/scripts/brain.sh --config CONFIG check
bash SKILL_DIR/scripts/brain.sh --config CONFIG init
bash SKILL_DIR/scripts/brain.sh --config CONFIG personal
bash SKILL_DIR/scripts/brain.sh --config CONFIG inventory --stage knowledge
bash SKILL_DIR/scripts/brain.sh --config CONFIG inventory --stage daily
bash SKILL_DIR/scripts/brain.sh --config CONFIG read knowledge/domain/case-lifecycle.md
bash SKILL_DIR/scripts/brain.sh --config CONFIG publish PLAN_JSON
bash SKILL_DIR/scripts/brain.sh --config CONFIG validate
```

Default config: ~/.config/second-brain/config.yaml. Configuration uses the demonstrated fixed
YAML subset. Version 3 requires branch per repository; existing version 2 remains readable but
actualization also requires that explicit branch field. Git authentication uses the caller's
normal Git environment; glab login alone only suffices when Git credentials are configured to
use it. Never write credentials into config. No pip dependencies. No code execution from sources.

Commands emit JSON. Save large results under the current workflow's internal working directory
and read all relevant ranges. Do not truncate patches or conversations and claim complete analysis.
Use scripts for deterministic collection, hashes, guarded replacement, links and source movement.
Never use ordinary publish for actualization: it must use its coverage/review/checkpoint publisher.
An interrupted actualization journal blocks other writers until actualize recover completes.
Legacy interrupted bootstrap/thoughts journals also block; recover them with their backed-up
original skill before continuing. Do not delete journals or edit completion flags to bypass gates.

## Knowledge layout

- knowledge/domain/: shared business concepts, written for nontechnical readers.
- knowledge/technical/REPO_ID/: implementation, flow and operational knowledge for that repo.
- knowledge/technical/REPO_ID/database/: SQL and NoSQL definitions and behavior from allowed evidence.
- knowledge/technical/shared/: established common technical principles.
- knowledge/essence.md: short linked guide, not a substitute for detailed topics.
- architecture/REPO_ID/ and architecture/cross-repository/: ADRs; new decisions are proposed.
- personal/YYYY-MM-DD-daily.md: today's personal summary only.

Keep classes, REST calls, Kafka topics and database structures out of domain prose. Use neutral
labels on optional technical/source links. Domain rules still retain conditions and exceptions.
Existing shared project variants must survive updates. Inbox conflicts require human decisions;
actualization automatically corrects selected-project implementation facts from its pinned code.
A planned change in a conversation is not evidence that code already implements it.

## Inbox and personal publication

The model supplies semantic content. Write a JSON plan using the file-writing tool:

```json
{
  "stage":"knowledge",
  "human_review_complete":true,
  "documents":[{
    "path":"knowledge/domain/case-lifecycle.md",
    "content":"# Case lifecycle\n\nExplicit sourced behavior.\n\n[Source material](../../inbox/meeting.md)\n",
    "expected_sha256":"CURRENT_HASH_RETURNED_BY_READ"
  }],
  "processed":[{"path":"inbox/meeting.md","hash":"CONTENT_HASH_FROM_INVENTORY"}]
}
```

Stage is knowledge or daily. For an existing output use the read hash; omit it only for new
files. processed contains only sources fully accounted for in the output. A non-durable source
can be knowledge-processed without a new topic. A daily source cannot be consumed without a
report. Daily headings must contain `# Daily summary — DD MM YYYY` using today's date.
Daily reads existing output before merging; preserve activity whose originals are archived.

Individual writes are atomic; ordinary inbox/daily multi-file publication is not transactional.
If interrupted, inspect active outputs and replan with current hashes. Unmarked sources remain
pending. Do not blindly replay stale plans. Actualization has a separate recoverable transaction
that includes its checkpoint and document deletions.

## Metadata, archive and links

Use templates/inbox-note.md from the unpacked package; the installed
copy is ~/.config/second-brain/inbox-note-template.md. Flat frontmatter has date, type,
repositories, include_in_daily and optional source_url as demonstrated. Repositories are a
comma-separated scalar of configured IDs, shared or unknown. No nested metadata or YAML tags.
Scripts write daily_hash, daily_output and knowledge_hash; never edit them manually. Changes
to source content/date/include_in_daily invalidate prior processing. Invalid dates stay in inbox.

A source moves to archive only after knowledge and, if include_in_daily=true, daily consume the
same content. Either workflow may run first. Archive contents are never opened or rewritten;
active incoming links are adjusted on movement. Do not require backlinks from archived notes.
Every writer adds justified semantic connections to current active knowledge; graph maintenance
then adds reciprocal navigation and index links. Matching keywords alone do not establish a
relationship. Do not read or modify the retired thoughts directory during graph updates.

## Personal Git activity

Collection includes exact configured author emails and today's author date in Europe/Warsaw,
across local branches, remote refs and HEAD, including unpushed alternative approaches. It fetches
the configured remote and reports errors if unavailable while retaining local evidence. It excludes
uncommitted edits, unreachable/deleted commits and work only on another machine. Analyze related
patches together; preserve distinct experiments, completion status and attribution. A user's merge
commit is integration work, not proof of sole authorship of every merged change.
