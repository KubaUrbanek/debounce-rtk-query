# Second Brain — three workflows

This package contains three executable OpenCode skills. Start with the [skill guide](SKILLS-GUIDE.md)
and [copyable prompts](PROMPTS.md). Actualization replaces both the separate bootstrap and the
team-change inbox report. Personal thought refinement and global linking skills have been removed.

## Install or upgrade

Requirements: Linux, Python 3.11+ with system timezone data, Git, and working Git access to your
remote repositories. No external Python libraries. glab is optional; the new workflows use Git.
If your existing Git credential setup uses glab, it continues to run under your own environment.

Unpack into a new directory, then run:

```bash
bash install.sh
```

The installer moves the six old skill directories and any previous versions of the three new
ones into backup directories outside OpenCode's active skills folder. It installs exactly:

- second-brain-actualize
- second-brain-process-inbox
- second-brain-my-work

Existing knowledge, thoughts, state and configuration are preserved. No bootstrap state cleanup
is needed. No automatic scheduling, Git commits or pushes are configured.

Edit ~/.config/second-brain/config.yaml following [config.example.yaml](config.example.yaml).
For every repository set an explicit `branch`, such as develop or develop-orders. Keep each
existing repository `id` unchanged so its completed bootstrap state can be located. Use version 3
for new configuration; version 2 remains accepted during upgrade with the added branch field.
The installer does not choose branch names or overwrite your existing configuration.

```yaml
version: 3
brain_dir: /home/you/second-brain
timezone: Europe/Warsaw
max_parallel_agents: 4
author_emails:
  - you@company.example
repositories:
  - id: case-service
    path: /home/you/work/case-service
    gitlab_host: gitlab.company.example
    gitlab_project: team/case-service
    remote: origin
    branch: develop-cases
```

The fixed YAML schema uses two/four-space indentation, strings and lists. Full-line comments
are supported. No aliases, tags, general nested structures, multiline values or inline comments.
Do not put tokens into YAML. gitlab_host/project are retained as repository identity fields for
compatibility; Git fetch uses the remote URL in the local configured clone.

```bash
bash ~/.config/opencode/skills/second-brain-actualize/scripts/brain.sh check
bash ~/.config/opencode/skills/second-brain-actualize/scripts/brain.sh init
```

## First update after an existing bootstrap

In OpenCode:

```text
Use second-brain-actualize to update knowledge for repository case-service.
Use the branch configured in YAML and the commit already recorded by the completed bootstrap.
Analyze all subsequent changes and affected complete flows, then update knowledge directly.
```

The skill imports the commit from .state/bootstrap/case-service/state.json only if that bootstrap
is completed. It keeps the old state and documents. That commit is already documented and is
excluded from the new change range. Missing/malformed commit or invalid ancestry leads to a
question for you, not a silent full reset. Incomplete old bootstrap state blocks for resolution.

Without any existing state, the same request starts a full scan of current source. It does not
replay the entire historical commit log. Tests, generated files and dependencies are excluded;
production code, configuration, SQL/NoSQL definitions and repository documents remain in scope.

## Subsequent runs and interruptions

Use the same actualization prompt for one repository each time. The skill pins the configured
remote tip and analyzes all changes after its last published checkpoint. It groups cumulative
results, including unchanged affected callers and complete entry-point flows. It may automatically
expand to the entire repository when impact cannot be bounded. It does not scan other repositories.
Cross-repository compatibility requiring verification is left explicit for that repo's own run.

At most four workers are active by default; the queue can contain any number of flow/residual
tasks. Completed workers are retired and replaced with fresh subagents. OpenCode must provide
real subagent capability; scripts do not call a model or spawn agents themselves.

If interrupted, request resumption. It uses the same pinned target and completed task results;
new remote changes wait for the next invocation. Publication waits for complete scoped coverage
and independent review. Source reads/hashes prove accounting, not model comprehension.

Only a successful publication advances the checkpoint. On interrupted publication use the
actualize recover command via the skill. It rolls back unfinished writes/deletions and keeps the
prior checkpoint. External edits block recovery for your decision. Never remove a journal or
manually set completed. If the old version left a bootstrap/thoughts journal, use its backed-up
original skill to recover that operation before running the new workflows.

A rewritten branch history or changed configured branch prompts for a full ancestor commit SHA
already reflected in documentation. Analysis starts strictly after your selected commit.
No new changes means no documentation update. A reviewed documentation-neutral change still
advances the checkpoint without inventing new knowledge.

## Manual materials and personal daily

Copy [templates/inbox-note.md](templates/inbox-note.md) into inbox with an actual event date.
Save Teams conversations, emails and meeting notes yourself. Set include_in_daily=true for
materials that should also feed personal daily. Run inbox processing and personal daily in either
order; sources wait for all required stages before moving to archive. Agents never read archive.

Personal daily covers today only and updates personal/YYYY-MM-DD-daily.md. Its English title
contains DD MM YYYY. It includes all your collected commits, unpushed experiments and eligible
conversations. It excludes uncommitted changes and personal thought drafts. No thought automation
is included; existing thoughts remain untouched.

## Knowledge layout and quality

Shared domain notes in knowledge/domain explain behavior to nontechnical readers. Implementation
belongs in knowledge/technical/REPO_ID, database details in its database subdirectory, and supported
shared principles in knowledge/technical/shared. New architecture notes under architecture are
proposed ADRs. Accepted history is preserved. knowledge/essence.md is a short linked guide to
substantive topics. Every workflow maintains appropriate relationships and reciprocal navigation.

Actualization corrects selected-repository facts according to code. It removes obsolete behavior
and, when no useful content remains, deletes the obsolete knowledge topic without archival and
repairs links. Other-repository variants and ADR history are retained. Inbox processing asks about
factual conflicts and unknown scope; a conversation about future work is not proof of implementation.

## Verification and implementation references

```bash
python3 -m unittest discover -s tests -q
```

Tests use temporary Git repositories and synthetic findings, not workplace access or a live model.
See [acceptance scenarios](docs/acceptance.md), [actualization protocol](skills/second-brain-actualize/references/actualize-protocol.md),
and [shared protocol](runtime/protocol.md). The package's bootstrap.py is an internal coverage engine,
not a fourth installable skill. Semantic discovery, impact judgments and prose quality still require
an actual model and independent review in your environment.
