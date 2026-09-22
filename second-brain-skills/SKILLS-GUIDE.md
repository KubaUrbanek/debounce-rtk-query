# Which skill to use

Exactly three workflows are installed. See [setup](SETUP.md) and [example prompts](PROMPTS.md).
All communicate in Polish, produce English Markdown, use bundled scripts for mechanical work,
and add meaningful links to existing notes. No workflow reads archive or processes personal thoughts.

| Goal | Skill | Input | Output |
| --- | --- | --- | --- |
| Document the system as implemented | second-brain-actualize | One remote repository branch plus existing knowledge | Updated domain, technical, database notes, proposed ADRs and linked essence |
| Extract knowledge from supplied materials | second-brain-process-inbox | New manual inbox sources and existing active knowledge | Updated topical knowledge and archived processed sources |
| Summarize your work today | second-brain-my-work | Your local/remote commits and eligible inbox conversations | Today's summary in personal |

## second-brain-actualize

Use both for initial documentation and every later code update. Select one configured repository;
its branch comes from YAML. No prior state means a full current-source analysis. A completed old
bootstrap supplies its already documented commit. Later runs collect all changes after the last
successful checkpoint and analyze their cumulative impact, including complete affected flows.

Discovery starts with endpoints, message consumers, jobs and other execution entry points. It
traces guards, transformations, storage, integrations and failure paths, and explicitly covers
remaining relevant sources. The task queue can be larger than the four concurrent worker slots;
each finished worker is replaced with a fresh one. Detailed evidence and independent review gate
publication. Impact uncertainty can expand the analysis to the whole selected repository.

It updates knowledge directly, without a team report in inbox. Domain notes are nontechnical;
implementation and SQL/NoSQL details have separate technical locations. Code wins on implemented
behavior in this repository, but cannot establish internals of another service. Obsolete topics
are deleted only when no current substance or other-repository variant remains; ADR history stays.

Interrupted analysis resumes the pinned target. Only successful publication advances the checkpoint.
An invalid baseline triggers a question for an already documented ancestor commit. It never silently
resets. No new changes means no update. See [actualization protocol](skills/second-brain-actualize/references/actualize-protocol.md).

## second-brain-process-inbox

Use after saving conversations, emails, meeting notes or factual working notes in inbox using the
[inbox template](templates/inbox-note.md). It reads all eligible new materials and relevant existing
knowledge, but never inspects repository source. It preserves explicit rules, exceptions, conditions,
agreed actions and decision rationale. Scope ambiguities and factual conflicts lead to questions.

It extends matching topics and splits independent concepts into stable English Markdown filenames.
Domain knowledge is shared, technical knowledge is scoped to the appropriate project or shared
principle, and database documentation is separate. New architectural decisions are proposed ADRs.
Future plans remain plans until implementation is evidenced; this skill does not infer deployed code.

Sources move to archive after knowledge and, if include_in_daily=true, daily have consumed the same
content. Either skill may run first. Invalid dates remain in inbox. Personal ideas/reflections are
not an automated refinement workflow; do not place them here expecting the retired thoughts behavior.

## second-brain-my-work

Use at the end of today and rerun when more activity arrives. It collects commits matching your
configured author emails across local and remote refs, including unpushed experiments and alternative
approaches. It reads entire eligible inbox conversations, while preserving attribution and distinguishing
others' work from yours. Uncommitted edits and personal thoughts are excluded.

It groups concrete outcomes, discussions, blockers and explicitly stated next steps into a medium-short
report, preserving distinct activity. The file is personal/YYYY-MM-DD-daily.md with heading
`Daily summary — DD MM YYYY`. Reruns update the same file and retain activity whose sources have
already been archived. Older supplied event notes are labeled as earlier-event updates in today's
report. Historical personal daily generation is unsupported.

## Typical routine

1. Run actualize when you want current source knowledge, one repository at a time.
2. Save work conversations in inbox. Run process-inbox to distill their explicit knowledge.
3. Run my-work for today's activity; repeat later if needed.

There is no mandatory daily source synchronization and no global linking or thought-refinement
command. Each remaining workflow finds and maintains relationships while updating its own notes.
