# Personal OpenCode + Superpowers Workflow

Version 1.1 · 8 September 2026

## 1. Purpose and implementation status

This guide defines the agreed personal workflow: deliberate planning, lower-cost implementation, independent review, separate testing, and separately requested domain documentation for future coding agents. It is technology-neutral.

**Status:** this is the operating specification for the updated installer, which includes `/sp-plan`, `/sdd`, `/sp-tests` and `/sp-docs`. Run the updated `install-superpowers-flow.sh` to install or update your configuration, then restart OpenCode. Existing task artifacts are preserved. The installer passed syntax checks and 13 isolated tests; remote installation was simulated and model behavior has not been tested end to end.

The target setup uses the standard Superpowers plugin, two configured model IDs, custom agents and four custom OpenCode commands. It deliberately overrides Superpowers defaults concerning automatic activation, TDD, worktrees, commits and artifact locations. These are personal workflow rules, not claims about stock Superpowers behavior.

## 2. Quick start

Start OpenCode inside the repository and on the branch you want to modify. Existing staged, unstaged and untracked changes are allowed.

1. Run `/sp-plan <task description>`.
2. Discuss requirements and approve the proposed design. Review the saved design when requested.
3. Receive an implementation plan and a separate test-scenario document. Read them before execution.
4. Run `/sdd <task-directory>` to authorize implementation of that plan.
5. Inspect the implementation and compilation result. No tests have been written, changed or run.
6. When ready, run `/sp-tests <task-directory>` to generate, adapt and run tests.
7. When ready, run `/sp-docs <task-directory>` to write domain documentation for future coding agents.
8. Request commits or other Git operations explicitly when desired.

There is no automatic transition between phases. You may pause between phases or execute the next phase in a new session. `/sp-docs <feature or scope description>` can also document an existing feature independently, without a previous plan. The documentation phase neither checks nor requires evidence that tests were run; the user chooses when to invoke it.

## 3. Activation and ordinary work

Superpowers workflow behavior is inactive by default. Only `/sp-plan`, `/sdd`, `/sp-tests` and `/sp-docs` activate it for the identified task and phase. This activation also applies to subagents explicitly delegated work within that phase.

Mentioning Superpowers, opening a plan file, asking a question about the workflow or having an unfinished task directory does not activate it. Directly selecting a workflow agent is not a substitute for invoking a phase command.

After completion or cancellation, the phase is inactive. Follow-up discussion can clarify its results, but new implementation, testing or workflow documentation work requires the corresponding command. During a running phase, answers and corrections remain part of that phase.

Ordinary work uses `build` on the low model. It does not automatically start this workflow or generate its documents. It does not create, modify or run tests unless explicitly requested. Small edits do not require subagents or a planning document.

All agent communication, generated task documents and reports are in English. Follow existing project conventions for source code identifiers and user-facing product language; do not translate the application merely because agent communication is English.

### What the global activation rule does—and does not do

The standard plugin still loads bootstrap instructions into context. The global `AGENTS.md` instructs the model when to use the workflow; it does not unload the plugin or eliminate that context cost. Superpowers explicitly gives user instructions, including `AGENTS.md`, precedence over its skills. This is instruction-based control, not an absolute technical guarantee. [Superpowers instruction precedence](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md#user-instructions)

## 4. Setup responsibilities

The installer asks for two exact OpenCode model identifiers:

- **high:** planning, coordination, reviews and difficult implementation.
- **low:** ordinary work, bounded implementation, test writing, domain documentation and focused exploration.

These are labels used in this guide, not literal OpenCode model IDs. Select actual `provider/model-id` values available through your configured providers. The setup does not create provider credentials or grant access to a model.

Useful terminal checks:

```bash
opencode --version
opencode models
```

The installer must preserve existing provider configuration and unrelated settings, back up files it changes, and print the actual installation and backup paths. It must not silently retain obsolete permissions or prompts for agents it manages. Global rules added to an existing `AGENTS.md` should be clearly delimited and replaceable without discarding unrelated instructions.

### Configuration layout

| Location, relative to the OpenCode configuration directory | Responsibility |
| --- | --- |
| `opencode.jsonc` or the selected existing configuration | Plugin, model assignments, agent definitions and permissions |
| `AGENTS.md` | General working agreements and command-only activation |
| `commands/sp-plan.md` | Planning phase contract |
| `commands/sdd.md` | Implementation phase contract |
| `commands/sp-tests.md` | Testing phase contract |
| `commands/sp-docs.md` | Domain documentation phase contract |
| `superpowers/<project-id>/<task-id>/` | Persistent task artifacts |

The default configuration directory in this guide is `~/.config/opencode`. Use the actual configured directory if it differs. Custom commands are OpenCode prompt templates; `$ARGUMENTS` supplies the text after the command, and the command can select its agent. [OpenCode custom commands](https://opencode.ai/docs/commands/)

The standard plugin install entry is `superpowers@git+https://github.com/obra/superpowers.git`. Restart OpenCode after setup. Recheck activation and routing after significant updates; a plugin update can change its workflow instructions. [Superpowers OpenCode installation](https://github.com/obra/superpowers/blob/main/docs/README.opencode.md)

## 5. Agents and cost control

The following role names define the intended agent configuration. Test workers are separate from implementation workers so their editing and execution rules can differ.

| Agent | Model | Responsibility |
| --- | --- | --- |
| `build` | low | Ordinary work outside the workflow |
| `designer` | high | Requirements, design, implementation plan and test scenarios |
| `orchestrator` | high | Coordinate the active implementation, testing or documentation phase |
| `coder` | low | Bounded production implementation and fixes; no test work |
| `coder-strong` | high | Complex or escalated production work; no test work |
| `tester` | low | Test implementation, existing-test adaptation and execution |
| `tester-strong` | high | Difficult or escalated test work |
| `documenter` | low | Write domain documentation for future coding agents |
| `reviewer` | high | Independent stage and final review, scoped to the active phase |
| `explore` | low | Focused read-only repository investigation |

The high orchestrator delegates routine code changes rather than implementing everything itself. It provides each worker with the exact task, relevant decisions, repository path, applicable project rules and report location. Workers do not need the entire conversation history.

Use low first for well-specified work. A task identified in the plan as requiring difficult reasoning, subtle concurrency or complex integration may start on high. Otherwise, after two unsuccessful attempts at the same problem, escalate automatically and briefly announce why. First distinguish missing information from insufficient capability: supply missing context or split an oversized task instead of blindly retrying.

Workers do not spawn additional workers. Implementation is sequential within the shared working directory. Independent reviews are coordinated centrally to avoid duplicate reviews and conflicting edits.

Model assignment belongs in OpenCode configuration. The orchestrator chooses an agent; that agent's configured model determines execution. Prompt-based routing is not deterministic. Inspect actual agent/model metadata on an initial small task instead of relying on an agent's statement about its own model.

## 6. Task documents and identity

Each task has a persistent directory outside the repository:

```text
~/.config/opencode/superpowers/<project-id>/<task-id>/
```

The installer/commands must define a stable project ID that distinguishes repositories with the same name. A readable repository name plus a short hash of its canonical local path is one suitable implementation. A task ID should be readable and unique, for example a date plus a feature name. These IDs are storage identifiers, not branch names.

| File | Required content |
| --- | --- |
| `design.md` | Goal, scope, exclusions, decisions, constraints, acceptance criteria and approval record |
| `plan.md` | Spec reference, coherent stages, concrete files/interfaces, task dependencies, high/low suitability and compilation approach |
| `test-scenarios.md` | Individually identified scenarios, expected behavior, priorities and suggested test levels |
| `progress.md` | Repository identity, observed branch, active phase, completed work, decisions, review findings, verification and deferred test issues |
| `documentation.md` | Domain concepts, business rules, processes, state transitions, examples, decisions and limitations; created by `/sp-docs` |

Supporting briefs, review reports and baseline records may live in a `support/` subdirectory of the same task directory. Do not place workflow documentation or scratch reports inside the repository. Source code and test files still belong in the repository's established locations.

`/sp-docs` reuses the selected task directory. A standalone documentation request creates a task directory using the same repository identity rules, with identity/progress records and `documentation.md`; it does not require or fabricate design, plan or test-scenario files. Existing documentation is updated in place for the same scope, preserving useful user-authored content.

Documents are retained after completion. They are not automatically committed, shared or deleted. Because they live outside Git, repository history does not back them up.

## 7. `/sp-plan`: design and plan

```text
/sp-plan Add scheduled notification processing with duplicate prevention
```

The high designer reads relevant project instructions, implementation and existing tests before asking questions. Reading tests is allowed; running or changing them is not part of this phase.

The designer clarifies material uncertainty that cannot be resolved from the repository, proposes a design and waits for approval. Approved decisions should not be repeatedly reopened without new evidence. The written design is reviewed with the user before the final implementation plan is prepared.

The plan defines concrete files, interfaces, behavioral requirements, dependencies and coherent implementation stages. It must be sufficiently explicit for a cheaper worker without turning every trivial edit into a separate delegation and review. It separates production tasks from deferred test work and identifies work requiring high reasoning.

The designer also inspects how this project already tests similar behavior: fake objects, mock dependencies, in-memory adapters and available local harnesses. It creates test scenarios in a separate file, not test source code.

### Scenario format

Each scenario includes:

- Stable ID and linked requirement.
- Preconditions and test data.
- Action.
- Concrete expected outcome.
- Priority.
- Suggested level: unit, local integration or E2E.
- Existing fake/mock/harness to reuse and any coverage limitation.

Example:

| Field | Example |
| --- | --- |
| ID | TS-003 |
| Requirement | Processing a completed item must not send another notification |
| Preconditions | In-memory repository contains a completed item; fake sender records calls |
| Action | Invoke processing for that item again |
| Expected outcome | No sender call; completion state remains unchanged |
| Priority / level | High / unit or local component integration |

Scenarios cover normal behavior, relevant boundaries, failure paths and regressions. Concurrent or retry behavior is included where the feature requires it. They are a behavioral specification, not a promise of full real-service integration coverage.

The phase finishes with the artifact paths, a short summary and the exact `/sdd` invocation. No implementation, branch changes, worktrees or commits occur.

## 8. `/sdd`: production implementation

```text
/sdd ~/.config/opencode/superpowers/<project-id>/<task-id>
```

Invoking `/sdd` authorizes implementation of the selected plan. It does not authorize tests or commits. The orchestrator reads the design, plan and progress, checks repository identity and records the starting state.

Existing modifications do not block work. Before editing affected files, the workflow preserves enough baseline information to distinguish pre-existing changes from new ones. A plain diff against `HEAD` is not sufficient when the repository was already dirty. Baseline capture must not stash, reset, stage or discard user changes, and must not collect unrelated secret files.

The orchestrator dispatches production tasks, runs independent review after coherent stages and arranges corrections. Ordinary implementation decisions within the approved design are made autonomously and recorded.

### Allowed verification

Compilation only, using the project's established command with test execution disabled. Do not run tests, lint or a separate typecheck. If the normal build bundles those operations, inspect its scripts and use a compilation-only route when available. Do not blindly assume that a command called `build` has no additional effects.

Compilation may inherently perform type checks; this is acceptable. It does not authorize a separate typechecking pass. If compilation cannot be isolated, record it as not run instead of silently widening verification.

### Strict test boundary

During `/sdd`, neither workers nor reviewers:

- Create new tests.
- Modify existing tests, fixtures or shared test helpers.
- Execute existing or new tests.
- Add test tooling or change test expectations to make checks pass.

If a changed interface is likely to break an existing test, record the affected test and reason in `progress.md` for `/sp-tests`. Do not repair it during implementation. Such observations must be labeled as inspection-based unless actual evidence exists; no tests were run.

### Reviews and escalation

Review checks specification compliance, correctness, regression risks and the actual scope of changed code. Missing new tests does not block this phase. Suspected bugs can still be reported from inspection; deferred testing is not a reason to ignore them.

Confirmed defects and deviations within the approved design are corrected automatically. Stylistic suggestions, optional refactors and scope expansions are reported without automatic implementation. Ask before material changes to behavior, public API, data model or dependencies.

### Completion report

Report implementation status, changed areas, stage/final review findings, compilation command and result, and deferred test issues. Explicitly state that tests were not created, modified or run. “Implementation complete” does not mean “fully tested” or “ready to merge.”

Do not automatically start `/sp-tests`.

## 9. `/sp-tests`: test generation and execution

```text
/sp-tests ~/.config/opencode/superpowers/<project-id>/<task-id>
```

The high orchestrator reads the design, test scenarios, deferred issues and current implementation. It checks existing coverage before generating tests so it does not duplicate equivalent checks.

Low test workers write missing tests and adapt existing tests to approved behavior. High reviews assertion quality, scenario alignment and the realism of fakes. Use the same two-attempt escalation policy as implementation.

### Environment and tooling

Use the project's existing test framework and established fake/mock/in-memory patterns. Tests must not require Docker, containers, a shared environment or a real external service. Do not install or launch such dependencies to make a test pass.

Default coverage is unit tests and local integration/component tests where appropriate. E2E is only included when explicitly requested and must still satisfy the local environment constraint. Any new framework, tool or dependency requires agreement.

If a requirement genuinely depends on real database, broker or service semantics, a fake cannot prove that behavior. Test the local contract where useful, document the limitation and leave the real-service scenario unverified. Do not weaken the requirement or silently claim equivalent coverage.

### Execution order

1. Run newly written and adapted tests.
2. Run related existing module tests that satisfy the environment restrictions.
3. Run the full application's suite only on explicit request, still respecting those restrictions.

Inspect the selected runner configuration before running a suite: module tests can include container-backed tests. If safe selection is unavailable, skip the suite and report why.

### Failures

Fix errors in the tests themselves and rerun the affected tests. If a valid test exposes a production defect, retain the meaningful assertion and report the defect. Do not change production code, manipulate fakes to hide the problem, skip the assertion or mark the scenario passed.

A production fix needs separate authorization. For a fix within the same approved scope, a subsequent `/sdd` invocation can address the recorded defect. A material design change requires revisiting the plan first. After implementation, invoke `/sp-tests` again to verify it.

The final report maps scenario IDs to test files/results and distinguishes passed, failed, existing coverage and unverified scenarios. It lists commands executed, production defects and remaining coverage gaps. No commits occur automatically.

## 10. `/sp-docs`: domain documentation for future coding agents

After implementation and testing, invoke:

```text
/sp-docs ~/.config/opencode/superpowers/<project-id>/<task-id>
```

Or document an existing feature independently:

```text
/sp-docs Describe the domain rules for scheduled notifications and duplicate prevention.
```

The command accepts an explicit task directory or a feature/scope description. Resolve a supplied directory against the current repository. For a scope description, reuse a clearly identified matching task in the conversation; otherwise create a standalone task directory. If the intended scope or task is ambiguous, clarify that ambiguity rather than choosing an arbitrary previous task.

The high orchestrator delegates writing to `documenter` on low. The high `reviewer` independently checks the resulting document against the actual behavior found in the implementation. Findings return to the documenter for correction. After two unsuccessful attempts to resolve the same documentation issue, high handles that bounded issue. The orchestrator does not routinely rewrite the entire document itself.

Agents inspect current implementation and relevant existing task documents as evidence. A plan describes intent; it is not proof of implemented behavior. Review evidence may remain in the task's supporting reports, while the final document stays focused on domain meaning.

The command does not run builds, tests, lint or typechecking. It does not inspect test execution status, ask whether tests were run, require successful outcomes or add test-readiness warnings. Timing belongs to the user. All repository files remain unchanged; output is written to the selected external task directory.

### Audience and format

The primary reader is a future coding agent that needs to understand the domain before changing behavior. Use concise English Markdown, stable headings, consistent terminology and explicit rules. Small tables suit definitions, decision rules and state transitions. A domain-level Mermaid diagram is useful only when it clarifies a nontrivial process.

The document must remain useful after a structural refactor or class rename. Do not include source links, repository file paths, line numbers, class or method names, source navigation tables or descriptions that mirror the implementation structure. Name domain concepts according to their business meaning, even when a current implementation happens to use the same word.

Keep technical details only when they express an externally meaningful contract or constraint, such as a time zone, processing deadline or duplicate-prevention guarantee. Explain those details in domain terms. Do not enumerate internal configuration keys, libraries or infrastructure choices simply because they exist in the code.

### Document structure

Begin with a domain-specific title, a short scope statement and a last-updated date. Include the following sections when relevant; omit empty sections and boilerplate:

| Section | Content |
| --- | --- |
| Purpose and scope | The problem being solved, participants and boundaries |
| Domain concepts | Terms, precise meanings and relationships |
| Business rules and invariants | Conditions, required behavior and what must always remain true |
| Processes and state transitions | Triggers, preconditions, actions, outcomes and allowed transitions |
| Edge cases and failures | Expected behavior for relevant exceptional situations |
| Decisions and constraints | Known rationale, tradeoffs and limits affecting domain behavior |
| Example scenarios | Concrete situations demonstrating the rules and their consequences |
| Open questions | Material unresolved domain behavior or rationale, if any |

Use stable rule identifiers when helpful for cross-referencing scenarios; preserve existing identifiers during updates. Distinguish confirmed behavior, recorded rationale and unresolved questions. Never invent business intent from implementation details or silently turn an observed defect into an approved business rule. Resolve contradictions from available evidence or state the precise uncertainty.

Examples describe domain inputs and outcomes, without requiring executable code. For instance, a duplicate-prevention rule should say what counts as the same notification and when another delivery is permitted, rather than naming a service, repository or method. Avoid claims about exactly-once delivery unless the implementation supports that guarantee.

Documentation should describe current behavior, not narrate the development session or duplicate the implementation plan. Keep it proportional to the feature. Do not include secrets, tokens or personal data.

### Storage, review and later use

Write `documentation.md` beside the selected task's existing plan and scenarios. Add its location and a one-line domain scope summary to `progress.md`, then return the actual document path to the user. Do not automatically start another phase or commit anything.

High review checks domain accuracy, completeness of important rules, consistent terminology, useful brevity and absence of implementation-specific references. Correct unsupported claims and contradictions before completion. No test-status gate is part of this review.

In a later coding session, explicitly provide the document path as reference context. Reading it does not activate this workflow. The next agent uses it to understand the domain, then inspects the current implementation for the requested change. A structural refactor alone should not require a documentation rewrite; changes to domain behavior or constraints do.

## 11. Git, permissions and approval boundaries

Work always happens on the current branch and in the current working directory. There are no automatically created branches or worktrees, including when the current branch is a default branch. Existing changes are preserved; ask only when an edit cannot safely coexist with them or ownership of a change is unclear.

Commits, staging for a commit, pushes, merges and PR creation require explicit instruction. No phase command implicitly authorizes them.

| Operation | Intended policy |
| --- | --- |
| Read relevant project files and rules | No routine approval prompt |
| Edit production code during `/sdd` | Allowed within task scope |
| Edit tests during `/sp-tests` | Allowed within task scope |
| Write planning/progress/review/domain documents | Allowed within this task's external artifact directory |
| Read repository files during `/sp-docs` | Allowed; repository editing and build/test execution are outside this phase |
| Run agreed compilation/test commands in the appropriate phase | No repeated prompts once permitted |
| Install dependencies or tools | Ask |
| Access unrelated paths outside the repository | Ask |
| Destructive operations or shared external side effects | Ask; never inferred from a phase command |

The external task directory is an explicit exception to the general outside-project approval rule. Agents need access to that directory for normal operation, not unrestricted access to the home directory.

File permissions must reflect role boundaries: designer, documenter and reviewer write only external task artifacts, production workers edit production files, and test workers edit tests. Test file locations vary by project, so final enforcement needs repository-aware patterns. Shell commands can modify files too; `edit: deny` alone is not a complete read-only guarantee.

If repository rules conflict with these preferences, report the concrete conflict. Do not silently bypass a protected project policy or claim that a check was completed when it was excluded by this workflow.

## 12. Resuming and changing work

Resume by invoking the same phase command with the same task directory. The agent reads `progress.md` and checks actual files before deciding what is complete. It must not trust stale checkboxes alone or automatically redo completed work.

New sessions work because task documents contain repository identity, decisions and progress. A missing argument is acceptable only if the task is unambiguous in the visible conversation; otherwise the agent asks. Use the full task path for predictable behavior.

If the repository path differs from the recorded identity, resolve that mismatch first. If the branch or code changed manually, inspect the current state, report material drift and continue on the current branch once scope is clear. Never switch back automatically.

If you interrupt a running phase, no rollback is implied. Completed and partial edits remain. Canceling a phase does not authorize deleting its documents or reverting changes.

Avoid concurrent implementation/testing sessions on the same files. Sequential delegation within one orchestrator does not prevent a second independently started session from creating conflicts.

## 13. Example working day

In the repository's OpenCode session:

```text
/sp-plan Add duplicate prevention to scheduled notification processing.
Reuse the existing persistence and sender abstractions.
```

After discussing the design:

```text
I approve the design. Prepare the implementation plan and test scenarios.
```

Read the resulting documents. Copy the exact path provided by the agent:

```text
/sdd ~/.config/opencode/superpowers/notifications-a1b2c3/2026-09-08-deduplication
```

The directory above is illustrative; your project ID will differ. Implementation and review proceed, followed by compilation only. The final report might say:

```text
Implementation complete. Compilation passed.
Tests were not created, modified or run.
Deferred: the existing sender test still uses the previous method signature.
```

Later:

```text
/sp-tests ~/.config/opencode/superpowers/notifications-a1b2c3/2026-09-08-deduplication
```

The test phase adapts that test, adds missing scenario coverage, runs allowed local tests and reports results. If tests reveal a production defect, review that finding before requesting a fix. When satisfied, explicitly request a commit and specify whether existing unrelated changes should be excluded.

To document the domain behavior for a future coding session:

```text
/sp-docs ~/.config/opencode/superpowers/notifications-a1b2c3/2026-09-08-deduplication
```

Low writes `documentation.md` in that same directory and high reviews it. The document explains notification eligibility, duplicate identity, completion rules and relevant failure scenarios using domain terms. It contains no code references. This phase does not rerun tests or ask for evidence of their execution.

Later, provide that document as context:

```text
Read the domain documentation at <actual-task-directory>/documentation.md.
Use it as context when assessing the requested change to notification eligibility.
```

## 14. Troubleshooting and initial acceptance check

| Symptom | What to inspect |
| --- | --- |
| Commands are not listed | Correct configuration directory, command filenames/frontmatter, then restart OpenCode |
| Ordinary requests start brainstorming | Global activation rule, conflicting project instructions and plugin updates |
| `/sdd` writes or runs tests | Active phase instructions for orchestrator, workers and reviewer; inherited TDD instructions |
| Test stage launches Docker | Runner selection and existing fixture setup; container-backed suites must be excluded |
| All workers use high | Actual configured agent model IDs and which agent was dispatched |
| Reviewer cannot save a report | Permission for the external task directory, not just repository-local `.superpowers/` |
| Agent requests a clean Git tree | Personal current-branch policy must override stock worktree setup instructions |
| Review includes pre-existing changes | Starting baseline and task attribution; do not rely on `git diff HEAD` alone |
| Compilation unexpectedly starts tests/lint | Build lifecycle and package scripts; select an isolated compilation route |
| New session repeats completed tasks | Progress document and code reconciliation |
| `/sp-docs` is missing in an older installation | The earlier installer provided three commands; the documentation extension must also be implemented and installed |
| Domain documentation contains paths or class names | SP-DOCS domain-format rules and high review; replace implementation references with business concepts |
| `/sp-docs` demands a plan or successful tests | Standalone operation and the absence of phase/test-status prerequisites |

After installation or an update, verify one small representative task end to end: ordinary build leaves the workflow inactive; `/sp-plan` changes only task documents; `/sdd` preserves existing changes and does no test work; `/sp-tests` uses local fakes and reports genuine failures; `/sp-docs` writes domain documentation to the selected external task directory using low drafting and high review, also works independently, and performs no test-status check; no phase changes branches or commits; actual worker model IDs match high/low assignments.

These are installation acceptance checks, not a request to generate test infrastructure in every project.

## 15. Maintenance and sources

Keep general behavior in global `AGENTS.md`, phase-specific rules in commands/agent prompts, model IDs and permissions in OpenCode configuration, and project-specific commands/conventions in the repository's own instructions. Avoid copying the entire workflow into every task plan.

The updated installer encodes this guide's latest decisions, including `/sp-docs`, its activation rule, documenter permissions and low/high routing. Future revisions must not restore earlier proposals for automatic commits, worktrees, test generation during `/sdd`, or documents inside `docs/superpowers/` in the repository. The feature documentation format must stay domain-based, without code references.

This guide's operational choices come from the agreed personal requirements. Platform integration references:

- [OpenCode custom commands](https://opencode.ai/docs/commands/) — Markdown command files, arguments and agent selection.
- [Superpowers for OpenCode](https://github.com/obra/superpowers/blob/main/docs/README.opencode.md) — standard installation and plugin bootstrap.
- [Superpowers user instruction precedence](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md#user-instructions) — explicit user rules override skill workflows.

The setup remains an agent-driven workflow. Instructions and permission configuration reduce mistakes but do not guarantee deterministic behavior, perfect isolation or full correctness. Completion reports must describe the checks actually performed.
