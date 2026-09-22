# Copyable prompts

Paste a prompt into OpenCode. Replace REPO_ID with its YAML id, not a project URL. Names below
request loading a skill; they are not slash commands or shell commands. Equivalent Polish prompts
are welcome; generated notes remain English. See [skill guide](SKILLS-GUIDE.md) and [setup](SETUP.md).

## First analysis or subsequent update

```text
Use second-brain-actualize to synchronize knowledge for repository REPO_ID using its
remote branch configured in YAML. Use the completed bootstrap commit if available;
otherwise use the last successful actualization checkpoint or perform a full initial
analysis when there is no state. Analyze cumulative changes and complete affected flows,
then update knowledge directly. Keep domain documentation understandable to nontechnical users.
```

The same request works on later runs; no date or manual commit list is needed.

## Resume an interrupted run

```text
Use second-brain-actualize to resume the interrupted run for REPO_ID. Keep its pinned
target and completed task results. Follow publication recovery if needed; leave newer
remote commits for the next invocation. Report any blocker requiring my decision.
```

## Answer a baseline question

Only use this when the skill asks because its saved baseline cannot be used:

```text
For REPO_ID, COMMIT_SHA is already reflected in the documentation. Validate it as an
ancestor of the pinned target and analyze only changes after it. Do not silently choose
another baseline or reset the documentation.
```

## Process manually supplied inbox materials

```text
Use second-brain-process-inbox to process all new eligible inbox notes. Read complete
conversations and update existing topics where they match. Preserve explicit rules,
conditions, exceptions and agreements. Separate domain, technical and database knowledge.
Ask me about factual conflicts or unclear scope before writing. Maintain meaningful links.
```

## Create today's work summary

```text
Use second-brain-my-work to create or update today's personal daily. Include all my
collected commits, local unpushed experiments and alternative approaches, plus eligible
inbox conversations, emails and meeting notes. Group by topic and preserve attribution,
concrete outcomes and explicit next steps. Include today's DD MM YYYY in the title.
```

## Add activity later today

```text
Use second-brain-my-work to update today's existing daily with newly available activity.
Preserve previously documented work whose sources are now archived. Do not read archive
or include personal thoughts. Keep the report concise without losing distinct outcomes.
```

## Ask for a status explanation

```text
Use second-brain-actualize to inspect status for REPO_ID without starting a new run.
Explain the saved checkpoint, any pinned target, unfinished tasks and blockers in Polish.
```

No removed skill names or planned-only commands are required. Completed bootstrap state is
imported automatically by the actualization script; never edit state.json by hand to advance it.
