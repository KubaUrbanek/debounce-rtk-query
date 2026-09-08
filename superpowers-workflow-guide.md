# Personal OpenCode + Superpowers Workflow

Version 2.0 · 8 September 2026

## Purpose and installation status

This technology-neutral setup uses two models and six explicit commands. It offers a full planned flow, a short follow-up flow, and an ephemeral flow for small actions. Documentation describes domain concepts and current behavior for future coding agents.

The updated `install-superpowers-flow.sh` implements this configuration. Download it, close OpenCode, run it without sudo, then reopen OpenCode in the relevant repository:

```bash
bash install-superpowers-flow.sh
```

The installer asks for exact high and low model IDs in `provider/model-id` format. It installs OpenCode when absent, configures the standard Superpowers plugin, assigns agents and permissions, and backs up managed files before updating them. Provider configuration and unrelated settings are preserved. Provider authentication remains separate if needed.

Requirements: macOS/Linux/WSL, Python 3.9+, curl and Git. No npm, pip or sudo is required by this installer. The upstream OpenCode installer may require its usual platform utilities. Use `--help` for model arguments, custom configuration directory, version selection and configuration-only mode.

Validation covers shell syntax and 17 isolated installer/helper tests, including updates, backups, command retirement, repository identity, shared documentation and legacy adoption. Remote installation was simulated; no model calls or live model-behavior tests were performed. Configuration and prompts define the intended behavior, not a guarantee that a model always follows it.

## Command selection

No manual agent selection is needed to start a command: its definition selects the primary agent. Use commands inside the repository you intend to work on.

| Command | Purpose | Agents/models | Persistent output |
| --- | --- | --- | --- |
| `/sp-plan <feature/change description>` | Clarify and design a larger change | designer high; focused explore low if useful | Task design, plan, scenarios and progress |
| `/sp-impl <task-directory>` | Implement an approved plan and update domain documentation | orchestrator high; coder low/high; reviewer high; documenter low | Implementation, task records and updated shared documentation |
| `/sp-tests <task-directory>` | Generate/adapt and execute local tests | orchestrator high; tester low/high; reviewer high | Tests and scenario/results records |
| `/sp-docs <feature/task-directory or process description>` | Document an existing process or refresh its description | orchestrator high; documenter low; reviewer high | Shared domain documentation and a short documentation task record |
| `/sp-followup <feature/task-directory or feature name> <change>` | Make a simple change with recovered feature context | followup low only | Change, short task record and updated shared documentation |
| `/sp-simplified <small action>` | Perform a small direct action such as a typo fix | simplified low only | Requested edit; result in chat, no workflow artifacts |

`/sdd` has been renamed to `/sp-impl`. The installer backs up and removes its recognized old managed command file. It stops if that file appears to be an unrelated custom command, allowing you to resolve the name conflict without losing it.

## Activation and common rules

Superpowers is inactive by default. These six commands activate only their requested scope and explicitly authorized delegates. Mentioning a skill, opening documentation or selecting an agent alone does not activate the process. Ordinary `build` uses low and does not create workflow documents or tests unless explicitly requested.

The full flow does not advance from planning to implementation or from implementation to testing automatically. There are two intentional built-in completion steps: `/sp-impl` always updates shared domain documentation, and `/sp-followup` always updates that same documentation. Neither step requires an additional `/sp-docs` invocation.

All agent communication, task artifacts and documentation are in English. Existing application language and code conventions are preserved.

Work happens in the current branch and working directory, even on main/master or with staged, unstaged or untracked changes. No automatic branches, worktrees, stashes, resets, staging, commits, pushes, merges or publication. Preserve existing user edits. Ask only about actual uncertainty or conflicts that prevent the requested change.

The standard Superpowers plugin still injects bootstrap context. Command-only activation is enforced through user instructions and agent permissions, not by unloading the plugin. Project or managed configuration can override global settings. After updates, inspect actual agent/model metadata on a small task.

## Feature and task structure

A **feature** is a long-lived domain capability or process, such as notifications. A **task** is one change to that feature, such as introducing retries or adding manual resumption.

The default artifact root is `~/.config/opencode/superpowers`. A custom OpenCode configuration directory changes that root accordingly.

| Relative location under the artifact root | Purpose |
| --- | --- |
| `<project-id>/features/<feature-id>/feature.json` | Repository identity and feature name |
| `<project-id>/features/<feature-id>/documentation.md` | The ONE current domain description for the entire feature |
| `<project-id>/features/<feature-id>/tasks/<task-id>/identity.json` | Individual task identity and link to a selected prior task, when applicable |
| `<project-id>/features/<feature-id>/tasks/<task-id>/design.md` | Approved design, for planned work |
| `<project-id>/features/<feature-id>/tasks/<task-id>/plan.md` | Production implementation stages, for planned work |
| `<project-id>/features/<feature-id>/tasks/<task-id>/test-scenarios.md` | Separate behavioral test scenarios, for planned work |
| `<project-id>/features/<feature-id>/tasks/<task-id>/progress.md` | Request, actual progress, decisions, verification and deferred issues |
| `<project-id>/features/<feature-id>/tasks/<task-id>/support/` | Relevant baseline evidence and, where applicable, review reports |

The project ID combines the repository name and a hash of its canonical path. Task IDs are unique. These identifiers never create or select Git branches.

Every change to a feature uses the same `documentation.md`. Do not create task-local current documentation or a separate document containing only the latest delta. Preserve unaffected domain rules and useful user-authored content while updating changed behavior. Historical task records remain intact.

Follow-up tasks have a brief progress record and scoped baseline evidence, without formal plans, scenarios or reviews. Documentation tasks do not fabricate a design, implementation plan or test scenarios. `/sp-simplified` creates none of these directories or files.

The documents live outside Git. They are retained and not automatically committed, shared or deleted. Protect them with your own backup approach if needed.

## Recovering the correct context

An explicit feature or task directory identifies the target most reliably. A task directory also identifies its parent feature. The command reads the shared domain description, relevant previous task decisions and current source. It does not assume a saved plan was implemented or that the code still matches an older report.

For a feature name or process description, the agent lists features belonging to the current repository. It selects a unique match and asks when the target is ambiguous. It checks existing features before creating another folder. Repeated modifications of the same process should reuse its feature identity, not create near-duplicate features.

The installed `personal-flow/task-files.py` helper returns JSON with `repository`, `feature_directory`, `task_directory` and `documentation`. A feature-only resolution has a null task directory. Agents must use the explicit returned paths, especially the shared documentation path.

Helper operations, normally run by agents:

```text
list <repository> [feature-name]
init <repository> <feature-name> [SP-PLAN|SP-DOCS]
task <repository> <feature-or-task-path> <task-slug> <SP-PLAN|SP-DOCS|SP-FOLLOWUP>
resolve <repository> <feature-or-task-path>
adopt <repository> <legacy-task-path> <feature-name>
```

Pass each argument separately and quote paths or names containing spaces. `init` creates or finds the feature and creates a task. `task` creates a new task under the resolved feature and records a link when an earlier task was supplied. Commands resume an explicitly identified unfinished task instead of creating another one unnecessarily.

## Full flow: planning

Start with a task description:

```text
/sp-plan Add scheduled notifications with duplicate prevention.
```

The high designer reads project instructions, relevant implementation, available shared domain documentation and existing tests. It does not run tests. It asks about material uncertainty, presents the design and obtains approval. Already approved decisions do not need repeated approval without new evidence.

For an existing feature, create a new planned task under that feature. For a new feature, establish its folder first. The designer writes the design, implementation plan and separate test-scenario document in the task subfolder. Planning does not change the current domain document to describe behavior that has not been implemented.

The plan contains scope, exclusions, exact implementation files/interfaces, dependencies, behavioral requirements, coherent stages, acceptance criteria and a compilation-only approach. It gives low enough context to execute and flags work that merits high. It does not mix test implementation into production stages.

Each scenario contains a stable ID, linked requirement, preconditions/data, action, expected result, priority, suggested test level and existing fake/mock/harness to reuse. Cover relevant normal, boundary, failure, retry and regression behavior. These are scenarios, not test source code.

Planning ends with the actual task path and an exact `/sp-impl` invocation. The user starts implementation explicitly.

## Full flow: implementation and automatic documentation

```text
/sp-impl <task-directory>
```

This authorizes the selected production plan and its required domain documentation update. High orchestrates; low performs well-scoped implementation. Complex tasks may go directly to `coder-strong` on high. After two unsuccessful attempts at the same problem, address missing context or oversized scope, then escalate with the findings rather than repeating an identical attempt.

Workers do not spawn workers. Implementation is sequential in the shared directory. High reviews after coherent stages and at the end, checking specification compliance, correctness and regression risks. Confirmed in-scope defects are fixed automatically; optional style suggestions or unrelated refactors are reported. Material behavior/API/data-model changes or new dependencies require agreement.

Capture scoped baseline evidence before editing so pre-existing user changes remain distinguishable from the task's changes. A diff against HEAD alone is insufficient in a dirty repository. Avoid unrelated files or secrets.

Never create, modify or run tests, fixtures or test helpers in this phase, including during review. Record suspected existing-test breakage for `/sp-tests` and leave those files unchanged. Missing new tests does not block implementation review.

Compilation is allowed only through an isolated route that does not run tests or lint. No separate typecheck. Compilation's inherent type checking is acceptable. Inspect build lifecycles; a command called `build` may execute excluded checks. If isolation is unavailable, report compilation as not run instead of changing scripts to bypass checks.

After implementation and code review, the orchestrator automatically delegates the shared domain document to low `documenter`, then high `reviewer` checks domain accuracy. This is part of `/sp-impl`, not an optional next command. Do not ask the user to start `/sp-docs` or run tests first.

The document describes the full current feature, incorporating the latest change and preserving unaffected rules. If work is interrupted or blocked, record the actual state and do not present intended or partial behavior as completed. A failed documentation update means the full implementation flow is not complete.

The final report states what changed, review findings, compilation evidence, deferred test issues and the canonical documentation path. It explicitly says that tests were not created, changed or run. `/sp-tests` remains a separate user invocation.

## Full flow: tests

```text
/sp-tests <task-directory>
```

High coordinates low test workers and independent high review. Read the design, scenarios, current behavior and deferred test issues. Reuse equivalent existing coverage rather than generating duplicates. Use high for difficult test reasoning or after two unsuccessful attempts at the same problem.

Use established frameworks and local fake/mock/in-memory patterns. No Docker, containers, real external services or shared test environments. Default to unit and local integration/component tests. E2E requires an explicit request and still must meet those environment restrictions. New frameworks, tools or dependencies require agreement.

Run generated/adapted tests first, then related module tests only when their setup is compatible with these restrictions. Full application suites require explicit instruction. Inspect runner setup before execution; do not accidentally launch container-backed tests.

Fix genuine test bugs. A valid assertion exposing a production defect remains meaningful and failing: report it rather than editing production code, weakening expectations or manipulating fakes. A fake cannot prove real database or broker semantics; report relevant coverage limitations.

The final report maps scenario IDs to files/results and lists actual commands, failures and gaps. To fix production behavior, explicitly request `/sp-impl` for approved planned work or `/sp-followup` for a bounded correction. Each such implementation updates the shared domain document. Tests remain separately requested.

## Short flow: follow-up

```text
/sp-followup <feature-or-task-directory> Allow manual resumption after three failed attempts.
```

A feature name is also accepted if it identifies the process unambiguously:

```text
/sp-followup Notifications — allow manual resumption after three failed attempts.
```

This is a direct change flow, not another planning phase. The low `followup` agent recovers feature context, reads current implementation and creates a small linked task record. It makes the requested production change itself and then updates the one shared domain document itself.

There are no subagents, reviewers, formal design/plan documents, test scenarios or test work. The agent uses relevant Superpowers reasoning proportionally. A clear small request does not require repeating the full design approval process. Clarify actual ambiguity before changing behavior.

Compilation is permitted when useful and isolated; no tests, fixture changes, lint or separate typecheck. Preserve the dirty-worktree baseline. Record suspected existing-test breakage briefly for later testing. Documentation uses the same domain format as `/sp-docs`, but without its delegation or review steps.

The response contains the change, compilation evidence if any, deferred issues and shared documentation path. If the scope becomes too broad to handle reliably, the agent asks about narrowing it or using `/sp-plan`; it does not automatically change model, start reviewers or switch flows.

## Small actions: simplified

```text
/sp-simplified Fix the typo in the notification button label.
```

The low `simplified` agent handles the request alone. It uses applicable Superpowers reasoning without forcing the full process: brief brainstorming for unclear behavior, systematic debugging for a defect, and direct action for an obvious typo.

No subagents, reviewers, automatic escalation, tests or fixture changes. No generated documentation, plans, designs, scenarios, task folders, progress files or persistent reports. Reasoning and the result remain in chat. The requested edit is the only intended persisted output. Compilation is optional when useful and safely isolated; no lint or separate typecheck.

The current-branch and existing-change rules still apply. If the request needs an update to domain documentation, the agent recommends `/sp-followup` or `/sp-impl` and asks before switching. `/sp-simplified` deliberately does not update the shared document.

## Documentation on demand

```text
/sp-docs <feature-or-task-directory>
```

Or describe a pre-existing process, even if no agent ever implemented it:

```text
/sp-docs Document the existing invoice approval process and its business rules.
```

Resolve an existing feature or establish a new one, create a documentation task record and inspect actual implementation. No prior plan or implementation task is required. Low writes the shared document, high independently checks it and corrections are made as needed. After two unsuccessful revisions of the same issue, high resolves that bounded issue.

This command does not change repository files or run builds, tests, lint or typechecking. It does not check test execution status, ask whether tests were run, require successful test outcomes or add test-readiness warnings. The user chooses when to invoke it.

It is useful for first documenting an existing process or refreshing documentation after changes made outside these flows. Normal `/sp-impl` and `/sp-followup` already maintain the document automatically.

## Domain document format

The primary reader is a future coding agent learning the domain before modifying behavior. Use concise English Markdown, stable headings, consistent terminology, explicit rules and small tables where helpful.

The document must remain useful after a structural refactor or class rename. Do not include code references, source links, repository paths, line numbers, class/method names or source-navigation tables. Define concepts by their business meaning. Keep technical details only when they express meaningful domain constraints, such as time zones, deadlines or duplicate-prevention guarantees.

Start with a domain-specific title, scope and last-updated date. Include relevant sections and omit empty boilerplate:

| Section | Content |
| --- | --- |
| Purpose and scope | Problem, participants and boundaries |
| Domain concepts | Terms, definitions and relationships |
| Business rules and invariants | Conditions and required behavior |
| Processes and state transitions | Triggers, preconditions, actions and outcomes |
| Edge cases and failures | Expected exceptional behavior |
| Decisions and constraints | Known rationale, tradeoffs and domain limits |
| Example scenarios | Concrete situations demonstrating the rules |
| Open questions | Material unresolved domain behavior or rationale |

Use stable rule IDs when helpful and preserve them during updates. Distinguish confirmed behavior, recorded rationale and uncertainty. A plan is not evidence of implementation. Never invent business intent or silently turn a suspected defect into an approved rule. Keep precise unresolved questions when evidence conflicts.

Examples describe domain inputs and outcomes, not executable code. A compact domain-level diagram is appropriate when it clarifies a nontrivial process. Avoid transcripts, large code blocks, secrets or personal data.

Review evidence and technical locators may remain in task support records; the shared document stays domain-focused. A pure structural refactor should not require rewriting it. Changes to domain behavior or constraints do.

For a later coding session, explicitly provide the shared document path as reference context. Reading it does not activate the workflow. The next agent uses it to understand the domain and inspects current code for the specific requested change.

## Agents and permissions

| Agent | Model | Role |
| --- | --- | --- |
| build | low | Ordinary work |
| designer | high | Full planning |
| orchestrator | high | Full implementation, testing and documentation coordination |
| coder / coder-strong | low / high | Production implementation, no tests |
| tester / tester-strong | low / high | Local test work, no production edits |
| reviewer | high | Independent review in full flows only |
| documenter | low | Shared domain document, repository read-only and shell denied |
| followup | low | One-agent change plus shared documentation |
| simplified | low | One-agent small action, no workflow artifacts |
| explore | low | Focused read-only investigation in delegated full flows |

`followup` and `simplified` deny delegation. Simplified also denies edits to the workflow artifact root. Production agents deny common test paths. Document-only agents allow edits only under the artifact root. Shell permissions begin with selected read-only Git commands allowed and other commands requiring scoped permission. Once a specific safe compilation/test command is allowed, do not request repeated permission unnecessarily.

Patterns cannot identify every project's test layout and shell operations can also modify files. Explicit phase instructions remain necessary; permissions are not a complete sandbox. Honor actual tool denials and project policies. Ask for new dependencies, unrelated outside access, destructive operations or shared external effects. No command implicitly authorizes Git publication or commits.

## Upgrading and legacy tasks

Rerun the installer with the intended high/low model IDs. It updates managed agents, commands, helper and rules while retaining unrelated configuration and task artifacts. Originals are saved under `.personal-flow-backups/<snapshot>/` in the configuration directory. A manifest records original paths, existence and modes. Restore exact files from a chosen backup if needed; do not copy the manifest over configuration.

The recognized old `commands/sdd.md` is removed within the backup/rollback transaction, and `commands/sp-impl.md` is installed. An unrelated custom `sdd.md` is left intact and reported as a conflict. Old historical references to `/sdd` are historical; use `/sp-impl` for new work.

Old flat directories `<project-id>/<task-id>/` remain untouched. On first use, assign a legacy task to the correct feature through the helper's `adopt` operation. The command should ask only if the feature grouping is ambiguous.

Adoption copies the selected task into the feature's task history and records its origin. The original remains recoverable. A previous task document seeds the shared documentation only if none exists; otherwise the existing shared document is preserved, and the old text becomes historical supporting material. Reconcile relevant domain facts against current implementation. Never automatically group unrelated tasks or overwrite a newer shared description with an older one.

Repeated adoption of the same legacy task into the same feature reuses the imported task. Historical original/snapshot documents are not additional current domain documents; only the feature-level `documentation.md` is maintained.

## Resuming and troubleshooting

Resume an explicitly identified task with the corresponding command. Reconcile progress with actual code and shared documentation; do not trust stale checkboxes or rerun completed work blindly. A repository mismatch must be resolved before editing. Never switch branches automatically to match an old record.

Canceling work does not roll back completed edits or authorize deleting documents. Avoid concurrent sessions modifying the same feature, code or shared documentation.

| Symptom | Check |
| --- | --- |
| New commands are missing | Updated installer, actual configuration directory and a restarted OpenCode session |
| Every worker uses high | Configured agent IDs and actual dispatch metadata |
| Ordinary requests activate the flow | Global activation rule, project overrides and plugin instructions |
| Implementation runs tests | Phase instructions and build lifecycle; tests are excluded |
| Follow-up creates reviewers | It must select primary `followup`, whose delegation is denied |
| Simplified creates task artifacts | It must select primary `simplified`; no helper calls or artifact writes |
| Multiple current docs appear | Use the helper's canonical feature documentation path, never task-local copies |
| Docs demand a plan or test results | Standalone SP-DOCS contract has no such prerequisites |
| A legacy task cannot resolve | Adopt it into an explicitly selected feature first |

After installing, try a small representative task to confirm the configured model assignments and actual behavior. This is a setup check, not an instruction to generate project test infrastructure.

## Configuration ownership and references

`AGENTS.md` contains general working agreements and activation. `personal-flow/WORKFLOW.md` contains the phase contracts and domain format. Command files select primary agents; configuration assigns models and permissions. `personal-flow/task-files.py` maintains repository/feature/task identity and explicit paths. Project-specific implementation and build conventions remain in project instructions.

Keep future changes consistent across these locations. Do not restore automatic worktrees/commits, test work during implementation, or task-local current domain documents.

Platform references retained for installation context:

- [OpenCode commands](https://opencode.ai/docs/commands/)
- [Superpowers for OpenCode](https://github.com/obra/superpowers/blob/main/docs/README.opencode.md)
- [Superpowers user instruction precedence](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md#user-instructions)

The workflow choices in this guide come from the agreed personal requirements. Reports must distinguish configured intent, inspected evidence and checks actually executed.
