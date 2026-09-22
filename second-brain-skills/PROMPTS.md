# Example prompts

Copy a prompt into OpenCode and replace placeholders such as `REPO_ID`, `BRANCH`,
`YYYY-MM-DD` and draft paths. `REPO_ID` is the YAML repository `id`, not its GitLab URL.
Names below request that OpenCode load a skill; they are not shell or slash commands.
Prompts are English, as are generated documents; you can ask equivalent questions in Polish.
See the [skill guide](SKILLS-GUIDE.md) for inputs, outputs and boundaries.

## Initial repository documentation — available

```text
Use bootstrap-second-brain to initialize repository REPO_ID from remote branch BRANCH.
Trace real entry points end to end. Queue all necessary flow and residual tasks with
at most four active workers, replacing each completed worker with a fresh one.
Preserve detailed rules, exceptions and failure behavior. Write domain documentation
for nontechnical readers; put implementation and database details in technical notes.
Publish only after complete source coverage and independent review.
```

Resume an interrupted bootstrap, not a completed one:

```text
Use bootstrap-second-brain to inspect and resume the interrupted analysis of REPO_ID.
Keep its pinned snapshot and completed task results. Follow the recovery protocol
if publication was interrupted, and report any blocker requiring my decision.
```

## Team changes for a date — available

```text
Use daily-develop-second-brain to summarize everything merged on YYYY-MM-DD into
develop-prefixed target branches across configured repositories. Group changes by
meaningful outcome in one inbox file. Clearly identify incomplete evidence.
```

## Today's personal work — available

```text
Use my-work-second-brain to create or update today's personal daily. Include all my
collected commits, including local unpushed experiments and alternative approaches,
and all eligible inbox conversations, emails and meeting notes. Group by topic and
preserve concrete outcomes and explicit agreements. Use today's DD MM YYYY in the title.
```

After adding more notes later today:

```text
Use my-work-second-brain to update today's existing daily with newly available activity.
Keep earlier documented activity even if its source has already been archived.
Do not read archive or include my thought drafts.
```

## Inbox into knowledge — available

```text
Use distill-second-brain-inbox to process all new eligible inbox notes. Read complete
sources and update existing topics when they match. Preserve business rules, conditions
and exceptions. Separate nontechnical domain knowledge, technical knowledge and SQL/NoSQL
documentation. Ask me about factual conflicts or unclear repository scope before writing.
Update the linked essence and archive sources only after their required stages finish.
```

## Refine thoughts — available

```text
Use refine-second-brain-thoughts to process my pending drafts. Split ideas, learnings
and reflections by meaning. Extend the single ideas note and matching topical learning
or reflection notes. Preserve my reasoning and alternative views; add only new substance.
Find relevant links yourself and ask if my intended meaning is unclear. Do not update daily.
```

For one selected draft:

```text
Use refine-second-brain-thoughts to process only thoughts/drafts/MY-DRAFT.md.
Choose suitable titles and existing target notes yourself. Keep any suggestions you
add distinct from my own thoughts, and archive the original after successful publication.
```

## Connect finished notes — available

```text
Use link-second-brain-notes to review all eligible finished notes and add meaningful
reciprocal links with brief explanations. Preserve substantive text and distinguish
personal proposals from implemented behavior. Do not inspect inbox, drafts or archive.
```

## Repository synchronization — planned, not executable in this package

The following prompts describe the agreed replacement workflow. The working name
`sync-repository-second-brain` has no installed skill or script in this version.
Do not run these prompts until that implementation is delivered. See the
[synchronization specification](docs/repository-sync-design.md).

First run and subsequent runs deliberately use the same request:

```text
Use sync-repository-second-brain to synchronize knowledge for repository REPO_ID.
Use its remote branch configured in YAML. With no checkpoint, analyze the complete
current source snapshot; otherwise analyze changes after the last published checkpoint
and all affected end-to-end flows. Update knowledge directly without an inbox report.
```

Resume interrupted work:

```text
Use sync-repository-second-brain to resume REPO_ID at its already pinned target commit,
reusing completed tasks. Leave newer remote changes for the next invocation.
```

Answer only when the skill asks for a replacement baseline:

```text
For REPO_ID, use COMMIT_SHA as the baseline already covered by the documentation.
Analyze only changes after it. Validate that it belongs to the configured branch's
history before continuing; do not silently choose a different baseline.
```
