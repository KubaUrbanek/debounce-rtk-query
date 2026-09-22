# Second Brain v2

Start with the [skill guide](SKILLS-GUIDE.md) and [copyable example prompts](PROMPTS.md).
The [agreed repository synchronization replacement](docs/repository-sync-design.md) is
documented separately and is not implemented in this package yet.

Six independent OpenCode skills. Ongoing workflows use one agent. Initial
repository analysis delegates exploration and independent review to subagents, with at most
`max_parallel_agents` active workers (default 4). User interaction is Polish; all generated
documents are English. This version replaces the earlier key=value package.

## Install

Requirements: Linux, Python 3.11+ with system timezone data, Git, authenticated glab.
No external Python libraries or pip installation. Authenticate glab on each configured
GitLab host using your normal workplace-approved mechanism; never put tokens in YAML.

Run `bash install.sh` from the unpacked package. Existing skill versions are moved to
backup directories; an existing config.yaml is preserved. Alternatively,
copy the six directories inside skills/ into ~/.config/opencode/skills/.
Replace previous versions of these skill directories; do not mix old helpers
with this version. Copy config.example.yaml to ~/.config/second-brain/config.yaml,
then edit the fixed fields. brain_dir is the root of your second brain. Configure exact
author email addresses, stable repository IDs, paths, GitLab hosts/projects and remotes.
Set `max_parallel_agents` to a positive integer; omitting it preserves the default of 4.
This limits active workers only. Bootstrap may plan dozens of tasks: when a worker completes
its task, its result is saved, the worker is closed, and a fresh subagent takes the next task.
It does not divide the whole repository into four fixed assignments.

Only the demonstrated YAML subset is supported: fixed fields, scalar strings and lists,
two/four-space indentation. Full-line comments are allowed; aliases, tags, inline comments
and general nested YAML are rejected. Quote strings using double quotes if needed.

Run:

```bash
bash ~/.config/opencode/skills/daily-develop-second-brain/scripts/brain.sh check
bash ~/.config/opencode/skills/daily-develop-second-brain/scripts/brain.sh init
```

Copy templates/inbox-note.md into inbox/ for each conversation/email/meeting note.
Replace YYYY-MM-DD with the actual event date. The template intentionally has an invalid
placeholder date so unfinished notes cannot be silently archived. include_in_daily defaults
to false. Set it true to include the entire conversation in personal daily.

## Invoke separately in OpenCode

- “Use daily-develop-second-brain to summarize system changes merged on 2026-09-16.”
- “Use my-work-second-brain to update today's daily.”
- “Use distill-second-brain-inbox to process my inbox.”
- “Use bootstrap-second-brain to initialize repository case-service from remote branch develop.”
- “Use refine-second-brain-thoughts to process my thought drafts.”
- “Use link-second-brain-notes to connect my finished notes.”

Skill names are not automatically slash commands. Ask OpenCode to load the named skill.
No combined command, scheduling, automatic commits or pushes are configured.

## Layout

| Location | Purpose |
|---|---|
| inbox/YYYY-MM-DD-system.md | One system-change source per day across all repositories |
| inbox/*.md | Manually supplied sources |
| personal/YYYY-MM-DD-daily.md | Today's personal summary, updated in place |
| archive/ | Processed original sources, for the user only |
| knowledge/domain/ | Shared domain concepts |
| knowledge/technical/shared/ | Reusable technical concepts |
| knowledge/technical/REPO_ID/ | Repository-specific implementation knowledge |
| knowledge/technical/REPO_ID/database/ | SQL and NoSQL models, migrations and access patterns |
| knowledge/essence.md | Short guide linking the concepts |
| architecture/REPO_ID/ | Proposed/accepted/historical ADRs |
| architecture/cross-repository/ | Decisions spanning repositories |
| conflicts/ | Deferred contradictions with both sources |
| index.md | Script-maintained graph navigation |
| .state/bootstrap/REPO_ID/ | Internal pinned snapshot, coverage receipts and unpublished draft |
| thoughts/drafts/ | Rough personal drafts; never included in personal daily |
| thoughts/notes/ideas.md | One cumulative ideas document with topical headings |
| thoughts/notes/learnings/ | Learning notes split by topic |
| thoughts/notes/reflections/ | Reflection notes split by topic |
| archive/thoughts/ | Original processed thought drafts; never read by agents |

## Personal thoughts

Copy templates/thought-draft.md to thoughts/drafts/ with a unique filename. The three
optional sections are Ideas, What I learned and Loose reflections. Write freely in Polish
or English; no metadata or manually supplied links are needed. Blank sections are allowed.
The refinement skill asks about ambiguous intent before generation, chooses English topic
titles, extends matching notes, omits semantic duplicates and preserves alternative positions.
Only ideas share a single file; learning and reflection topics have separate notes.
Agent suggestions, when useful, are explicitly separated from your own thoughts.

Refinement reads current knowledge for context and adds meaningful links, but cannot publish
your thoughts as factual domain/technical knowledge. It archives drafts after successful
publication and preserves provenance. These drafts and notes never feed personal daily.
The original knowledge distillation workflow remains inbox-based.

The connection skill runs separately on demand, reads finished knowledge, ADRs, personal
and thought notes, and adds reciprocal links with short explanations automatically.
It excludes inbox, drafts and archive and preserves substantive note content. It does not
delete existing links. See [thoughts protocol](runtime/thoughts-protocol.md) and
[thoughts acceptance scenarios](docs/thoughts-tests.md).

If a thought/link publication is interrupted, run the installed thoughts.sh recover command
before any other writer. Recovery rolls back the unfinished operation; external edits stop
recovery for your decision. Regenerate the plan from current sources after recovery.

## Behavior

Domain notes in knowledge/domain/ are documentation for nontechnical users: roles, processes,
conditions, business rules, visible outcomes and exceptions. Implementation details such as
REST calls, classes and database structures belong in technical notes. The bootstrap still
traces code end to end internally; it translates established behavior into business language.
See templates/domain-topic.md for the intended audience and structure. Optional links to
technical notes remain neutral and do not require the reader to understand the implementation.
Inbox distillation preserves this separation when updating topics. Installing this version
does not automatically rewrite already generated notes; the linking skill only adds links.

System reports use MR merge dates in Europe/Warsaw, not commit dates. They include all
develop-prefixed target branches and summarize cumulative outcomes with MR links, without
author/SHA inventories. Historical evidence comes from merged diffs, not current code.
Incomplete diffs or unavailable repositories are clearly reported as partial.

Personal daily is today-only: exact author emails, author dates, all reachable local and
remote commits (including unpushed experiments) plus eligible inbox materials. No
uncommitted changes. Late notes are included with their original event dates.
Earlier daily content is preserved when its source is already archived.

Ongoing knowledge is extracted only from explicit inbox content; existing active knowledge provides
context. Conflicts and ambiguous scope trigger questions before generation. New ADRs are
proposed. No generated personal daily is recycled into knowledge.
Database knowledge has its own technical directory and links to domain and application notes;
both initial analysis and ongoing inbox updates use the same structure.

Initial analysis is a separate, one-time operation for one configured repository at a time.
It pins the selected remote branch and reads its current production sources, configuration,
SQL/NoSQL definitions, scripts, CI and repository documents. Tests and identified generated
or dependency files are excluded. No project code, build, commit history or live database is
used. Code wins over contradictory prose and existing facts about the analyzed project;
other projects' variants are preserved. Later changes are handled through the inbox workflow.

Bootstrap discovery starts from real execution entry points: endpoints, message/Kafka consumers,
cron/scheduled jobs, batch, CLI and startup hooks. Each queued flow investigation traces behavior
end to end through domain guards, persistence, integration and failure paths. Shared dependencies
may belong to multiple flow investigations. Configuration, migrations, library APIs and documents
without a discovered entry point receive explicit residual tasks; they are not skipped.
Discovery examines registrations and wiring as well as source declarations. Areas organize file
accountability and documentation; the number of flow tasks is independent of the worker limit.

The bootstrap script accounts for every included file and character range. Subagents supply
findings; the coordinator synthesizes useful linked concepts and cross-file flows; a fresh
reviewer checks the exact staged draft. Publication waits for complete coverage and approved
review. Receipts prove which material was supplied, not that an agent understood it. Missing
capabilities or persistent failures block the run for your decision. Resume the same snapshot;
successful initialization cannot be repeated for that repository ID.

After a publication interruption, inspect bootstrap `status` and use its `recover` command
before continuing. Keep other writers paused during recovery. Never delete state or alter
completion markers to bypass the coverage, review or one-time gates. Internal JSON and bare
Git state are implementation artifacts; all user-facing knowledge remains linked Markdown.

Processing hashes track the current source content independently for knowledge and daily.
After both required stages, scripts move the source into archive and repair active links.
Invalid dates remain in inbox. A note without durable knowledge can be marked done without
creating a topic. Backlinks are generated for active notes; archive content is never read
or rewritten. System reports may be restored by known filename for a requested rerun.

## Fresh bootstrap and interrupted runs

Install this updated package with `bash install.sh`; your YAML is preserved. There is no repair
mode. The user handles any cleanup before requesting a fresh bootstrap for a selected repository.
The skill does not automatically erase existing knowledge or completed state. Retained completed
state blocks a second initialization. Do not erase unrelated repositories or shared knowledge.
In OpenCode ask:

> Use bootstrap-second-brain to initialize repository REPO_ID from remote branch BRANCH.
> Discover entry points and queue end-to-end flow tasks plus explicit residual work.
> Use fresh workers with at most four running concurrently, preserve detailed domain and
> technical findings, and require independent review before publishing.

For a merely interrupted run, resume its existing pinned snapshot normally instead of starting
again. The state and durable task results preserve progress across context limits and failures.

See [analysis upgrade and acceptance](docs/analysis-upgrade.md). This version requires functional
planning, entry-flow/residual task completion and finding-to-document mappings in bootstrap plans;
older staged plans must be expanded
and reviewed again. Other workflows keep their existing publication JSON shape.

## Verification details

Run `python3 -m unittest discover -s tests -v` in the unpacked package.
Tests use temporary repositories and stubbed GitLab responses. Live workplace glab access
and model synthesis require validation in your environment. Scripts gather evidence and
manage files; the LLM supplies semantic content through the documented publish plan.
Multi-file publication is recoverable via unmarked sources, but not a full transaction.
MR diffs may be limited by the GitLab server; these gaps are reported, not silently ignored.

See [implementation plan](docs/second-brain-plan.md) and
[business scenarios](docs/second-brain-tests.md), plus the
[bootstrap plan](docs/bootstrap-plan.md), [bootstrap scenarios](docs/bootstrap-tests.md)
and [bootstrap command protocol](skills/bootstrap-second-brain/references/bootstrap-protocol.md).
