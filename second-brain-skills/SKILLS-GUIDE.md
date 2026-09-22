# Skill guide

This guide describes the executable skills in this package. See [example prompts](PROMPTS.md)
and [setup](SETUP.md). The agreed replacement of bootstrap and the team report is
**not implemented in this package yet**; its separate [specification](docs/repository-sync-design.md)
records the next version without presenting it as an available command.

## Choose a skill

| Your goal | Available skill | Input | Result |
| --- | --- | --- | --- |
| Create initial repository documentation | `bootstrap-second-brain` | One configured repository and a named remote branch | Detailed linked domain, technical, database and architecture notes |
| Collect changes merged on a chosen date | `daily-develop-second-brain` | Configured GitLab projects; all develop-prefixed target branches | One `inbox/YYYY-MM-DD-system.md` |
| Summarize your work today | `my-work-second-brain` | Your local/remote commits and eligible manual inbox sources | `personal/YYYY-MM-DD-daily.md` |
| Turn inbox sources into durable knowledge | `distill-second-brain-inbox` | New inbox notes and relevant existing knowledge | Updated topical notes, essence and proposed ADRs |
| Refine rough thoughts | `refine-second-brain-thoughts` | `thoughts/drafts/` and existing notes for context | Cumulative ideas, topical learnings and reflections |
| Connect finished notes | `link-second-brain-notes` | Finished knowledge, architecture, personal and thought notes | Reciprocal links with meaningful explanations |

## Initial documentation: bootstrap-second-brain

Use once for one repository. It pins a remote source snapshot, discovers execution entry
points and investigates complete flows: endpoints, message consumers, scheduled jobs,
batch/CLI and startup behavior. Explicit residual tasks cover code or documents outside
those flows. Tests, generated code and dependencies are excluded; source configuration,
SQL/NoSQL definitions and repository documents remain in scope. It never connects to a database.

The coordinator schedules as many tasks as needed, with at most four active workers by
default. Each completed worker is retired and a fresh one receives the next task.
Publication requires complete accounted source coverage and independent review. This
accounting cannot guarantee semantic understanding by a model.

Domain notes explain roles, rules, conditions, outcomes and exceptions for nontechnical
readers. Classes, REST paths, transport mechanisms and storage structures belong in
technical notes; database documentation has its own subdirectory. New ADRs are proposed.
An interrupted analysis resumes its pinned snapshot; a completed bootstrap cannot rerun.
There is no repair or old-bootstrap migration feature.

## Team changes: daily-develop-second-brain

Use to collect what was merged on a specific day, including a past date. The report uses
GitLab merge time in the configured timezone, not the original commit date. It groups
outcomes across repositories and develop-prefixed branches without an author/SHA inventory.
Its output is an inbox source, not final knowledge. Run inbox distillation afterward.
No activity means no report file; unavailable evidence is reported as partial coverage.
This skill and bootstrap are scheduled to be replaced by the synchronization design.

## Personal daily: my-work-second-brain

Use at the end of today or rerun when new activity arrives. It includes commits matching
configured author emails across local and remote refs, including unpushed experiments and
alternative approaches. Uncommitted edits are excluded. Manual inbox notes need a valid
event date and `include_in_daily: true`; whole eligible conversations are considered,
while attribution distinguishes your work from other people's statements.

The report groups concrete results, discussions, blockers and explicitly stated next
steps. It is medium-short without dropping distinct activity. The English heading is
`Daily summary — DD MM YYYY`, with today's date. Reruns update the same file and preserve
earlier content whose sources have since been archived. Older supplied event notes appear
as earlier-event updates in today's report. Historical daily generation is unsupported.
Thought drafts and refined thoughts are never daily inputs.

## Durable knowledge: distill-second-brain-inbox

Use after manually saving Teams conversations, emails, meeting notes or other material
using the [inbox template](templates/inbox-note.md). It reads inbox and existing active
knowledge, never repository code or archive. It asks about ambiguous scope and factual
conflicts before generation. Ordinary publication needs no additional confirmation.

It extends matching topics, creates separate files for independent concepts, and preserves
conditions, exceptions and source links. Domain knowledge is shared; technical knowledge
is repository-specific or explicitly shared. SQL/NoSQL details and ADRs have separate
locations. `knowledge/essence.md` is a short linked guide, not a replacement for detail.
Processed sources move to archive after all required stages finish. A source selected for
daily remains in inbox until both knowledge and daily have consumed its current content.

## Personal thinking: refine-second-brain-thoughts

Use after adding rough drafts using the optional [thought template](templates/thought-draft.md).
You can write freely with typos and no manually supplied relationships. Mixed drafts are
split by meaning: ideas extend one `ideas.md`; learnings and reflections use separate
topical files with titles chosen by the agent.

It reads full existing matching notes, adds new substance, omits semantic duplicates and
preserves alternative views. Ambiguous intent triggers a question. Agent suggestions are
identified separately. Relevant knowledge links are automatic, but personal ideas do not
become implemented facts or accepted decisions. Original drafts are archived after
successful publication. This workflow does not update daily.

## Relationships: link-second-brain-notes

Use when finished notes have accumulated and you want a broader connection review. It
reads eligible notes, finds substantive relationships and adds reciprocal links with brief
English explanations. It excludes inbox, drafts and archive. It preserves substantive
prose, does not remove existing links, and does not turn proposals into facts. Links into
domain documentation use language appropriate for nontechnical readers.

## Typical routine

1. Initialize each repository separately using bootstrap while this version is in use.
2. Save work conversations and meeting notes in inbox; put personal thoughts in drafts.
3. If needed, collect the day's team changes into inbox.
4. Generate today's personal daily and distill inbox. Either order works; archival waits
   for both required stages on each source.
5. Refine thought drafts independently. Run relationship review when useful.

All skills communicate in Polish and write English Markdown. They use bundled scripts for
mechanical work and do not commit or push user repositories. Agents never read archive.
After the synchronization replacement is implemented, its direct knowledge update replaces
steps 1 and 3; manual inbox, daily, thoughts and linking retain their separate purposes.
