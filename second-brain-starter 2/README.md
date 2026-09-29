# Second Brain Starter for OpenCode 1

Build a code-grounded knowledge base one repository and one selected process at a time. This package contains three manually invoked skills, not an automation framework.

All skill instructions and generated documentation are in English. The default output directory is `/Projects/pkr-tool-docs` (capital `P`). Source repositories remain separate from the knowledge base.

## 1. What is included

| Skill | Your action | Result |
| --- | --- | --- |
| `second-brain-map` | Choose one repository and branch | Repository map, candidate flows and a map checkpoint |
| `second-brain-analyze` | Choose one specific process | Evidence-backed flow description and its completed checkpoint |
| `second-brain-organize` | Ask to organize existing analyses | Shared business knowledge, technical notes and an agent index |

You invoke each skill yourself. No skill automatically starts the next one. Repeat analyze for each process you choose. It does not analyze the entire repository automatically.

Incremental synchronization, scheduling, CI integration, automatic commits, pushes, and batch processing of all repositories are not included. Branch/commit metadata is retained so a future update workflow can be added later.

## 2. Prerequisites

Use OpenCode with filesystem and shell access, local Git repositories, Git, and permission to fetch their configured remotes. The agent must be able to read the source code and write to `/Projects/pkr-tool-docs`.

No database, vector store, Python runtime, or additional application service is required by these skills. JSON updates can use the tools already available to the agent. Git authentication must already work in the environment; never put credentials in these files.

If your filesystem does not have `/Projects`, explicitly choose another output path in your invocation. The skills must not silently write elsewhere. The package does not contain or analyze your application code until you invoke it in an environment with access to that code.

## 3. Install for OpenCode

OpenCode discovers the included `.opencode/skills/<name>/SKILL.md` layout. Supporting references stay beside each skill. The package does not require Codex metadata, a plugin, custom agents, or custom slash commands.

### A. Install once in the knowledge workspace

Extract this ZIP and open a terminal inside the extracted `second-brain-starter` folder. Copy its skill folders, including the hidden `.opencode` directory:

```bash
mkdir -p /Projects/pkr-tool-docs/.opencode/skills
cp -R .opencode/skills/second-brain-map /Projects/pkr-tool-docs/.opencode/skills/
cp -R .opencode/skills/second-brain-analyze /Projects/pkr-tool-docs/.opencode/skills/
cp -R .opencode/skills/second-brain-organize /Projects/pkr-tool-docs/.opencode/skills/
```

These commands install or update the three named skill folders. Do not replace your knowledge workspace with the extracted package: keep existing config.json, state.json and generated knowledge. Do not keep another outdated copy of the same skill in a different discovery location.

### B. Configure OpenCode 1

This package targets OpenCode 1, using `permission` and `bash`. For a knowledge workspace without an existing OpenCode configuration:

```bash
cp configuration/opencode.json /Projects/pkr-tool-docs/opencode.json
```

If opencode.json or opencode.jsonc already exists, merge the supplied permission entries into it. Preserve your providers, models, agent policies and other settings. The template does not select a provider or model.

The configuration allows these skills, ordinary reads/searches, and external access under `/Projects`. File edits are permitted in the knowledge workspace; source repositories are not granted file-edit permission. Shell commands request approval so Git inspection/fetch and the occasional atomic state write can be reviewed. File-edit restrictions are not a shell sandbox. More specific existing global or agent policies may still apply.

If your repository paths or knowledge root differ, adjust the absolute permission patterns accordingly. config.json supplies repository locations but does not itself grant OpenCode permissions. Permission templates must be copied or merged into opencode.json separately.

### C. Start OpenCode in the knowledge workspace

```bash
cd /Projects/pkr-tool-docs
opencode
```

Use a write-capable mode/agent for producing documents. A read-only planning mode cannot save the output. If OpenCode cannot find a skill, check the uppercase SKILL.md filename, folder name and skill permissions. The examples below explicitly ask the agent to load a skill by name; they do not rely on Codex `$skill` syntax.

### Optional: work from each source repository instead

The recommended setup above needs only one installation in the knowledge workspace. If you prefer starting OpenCode inside `/Projects/orders-api`, then later inside another application, install the three skill folders globally under `~/.config/opencode/skills/` instead. Merge the matching permissions into each active project's configuration or your global OpenCode configuration. Always state the shared output path `/Projects/pkr-tool-docs` in your prompts. Do not create a new knowledge base inside each source repository.

The supplied relative edit rules assume the knowledge workspace is the working directory. For source-repository sessions, remove the relative edit exceptions (config.json, state.json, index.md, open-questions.md, repositories/*, domain/*) and keep only `*` deny plus the absolute `/Projects/pkr-tool-docs/*` allow rule. That avoids authorizing similarly named files in the source repository. Project-local skill installation is enough if you always use the recommended central workspace.

## 4. Configure your first repository

This is the knowledge-base configuration, distinct from OpenCode permissions in opencode.json. You can let map create it from your first prompt, or use configuration/config.example.json as a reference to create `/Projects/pkr-tool-docs/config.json` yourself:

```json
{
  "repositories": [
    {
      "id": "orders-api",
      "path": "/Projects/orders-api",
      "remote": "origin",
      "branch": "develop"
    }
  ]
}
```

- `id`: stable name used in document paths and state keys.
- `path`: absolute path to your local application checkout.
- `remote`: the existing Git remote to fetch.
- `branch`: branch name on that remote, without an `origin/` prefix.

Use the real branch; `develop` is only an example. Map and analyze fetch the configured remote, pin its branch to a full SHA, and inspect that committed version. They must not switch your working branch or include uncommitted edits. A feature branch currently checked out in your editor does not change the configured analysis branch.

## 5. Step one: map the repository

```text
Load and use the second-brain-map skill for /Projects/orders-api.
Repository ID: orders-api. Remote: origin. Branch: develop.
Write the knowledge base to /Projects/pkr-tool-docs.
```

Expected outputs:

- `repositories/orders-api/map.md`: module responsibilities, technology, storage, integrations, source snapshot and limitations.
- `repositories/orders-api/coverage.md`: entry points, source symbols, candidate flows and analysis status.
- Configuration and a map checkpoint in the shared state, preserving all existing flow checkpoints.

The agent scans the repository's structure and entry-point mechanisms. It does not deeply document every process and does not mark discovered processes analyzed. After a successful scan, it records the configured branch and full SHA under `repositories[repo-id].map`. Both map.md and coverage.md identify that same discovery snapshot. An interrupted scan does not advance the previous map checkpoint.

Read the map and candidate list. Choose a useful process with clear behavior, such as approving an order or handling a payment notification. Do not start by requesting a generic description of every class.

## 6. Step two: analyze a process you choose

```text
Load and use the second-brain-analyze skill for repository orders-api.
Analyze the order approval process, starting at
POST /orders/{id}/approve.
Use /Projects/pkr-tool-docs as the knowledge base.
```

Other acceptable selectors are a business name, a message consumer, a scheduled job, or a class and entry method. If the name is ambiguous, the skill asks you to choose; it does not silently pick a process.

The agent follows that process through authorization, validation, decisions, persistence, configuration, events, integrations and error paths. It reads relevant tests and records what they assert. It does not run them by default.

Expected outputs:

- `repositories/orders-api/flows/approve-order.md` (the precise flow ID follows the selected process).
- Updated coverage linking the selected entry points to the document.
- A completed entry in the shared `state.json`.

The flow description explains conditions, alternate paths, rules, state transitions, effects, repeated execution, failure behavior, sources, test evidence and unknowns. External implementations that have not been inspected remain explicitly unverified.

Repeat the skill yourself for another process:

```text
Load and use the second-brain-analyze skill for repository orders-api.
Analyze the payment notification consumer PaymentReceivedListener.
Use /Projects/pkr-tool-docs as the knowledge base.
```

Related helper calls belong to the selected process analysis. Unrelated processes do not. A flow can have multiple entry points; the inventory links them to one flow where justified.

## 7. Understand the shared state

There is exactly one `/Projects/pkr-tool-docs/state.json`. Each repository has its own key, with a map checkpoint and individual flow entries:

```json
{
  "repositories": {
    "orders-api": {
      "map": {
        "document": "repositories/orders-api/map.md",
        "branch": "develop",
        "last_mapped_commit": "0123456789abcdef0123456789abcdef01234567"
      },
      "flows": {
        "approve-order": {
          "document": "repositories/orders-api/flows/approve-order.md",
          "branch": "develop",
          "last_analyzed_commit": "0123456789abcdef0123456789abcdef01234567"
        }
      }
    }
  }
}
```

The example SHAs are illustrative. Each skill writes the actual full SHA. `map.last_mapped_commit` identifies the source version used to discover the repository entry points and candidate flow list. `flows[flow-id].last_analyzed_commit` identifies the version used to verify that detailed flow description. Neither means the last commit touching a particular file.

For example, map can remain at commit A while approval is analyzed at a later commit B. This tells you that the list of processes was discovered at A but approval was inspected at B. Analyze may adjust its coverage status or flag newly observed entries with their own provenance; it must not claim the whole inventory was rescanned at B.

Two flow documents may have different checkpoints because you analyzed them on different days. This is intentional and visible. Shared knowledge must preserve that provenance rather than pretending the whole knowledge base was verified at one time.

Only a successfully completed map invocation updates the map checkpoint. Only a successfully completed analyze invocation updates a flow checkpoint. Map preserves existing flow checkpoints, analyze preserves the map checkpoint, and organize preserves both. Existing entries and unrelated metadata must survive every update.

If analysis is interrupted, the skill leaves a draft and preserves the previous completed checkpoint. Ask it to resume the same process. It must check the draft's source version and revalidate changed evidence before publishing. This is a simple draft workflow, not a persistent task scheduler.

The same interruption rule applies to map: its draft inventory is not a completed map snapshot.

A save is not an atomic transaction across Markdown files and JSON. State is written last. If a crash leaves newer prose with an older checkpoint, rerun analysis to reconcile it. Organize must flag mismatched prose instead of treating it as newly verified.

If you already have state with only flows, keep it. The next successful map invocation adds the map object without changing those flow entries. Missing map provenance is explicitly unrecorded, never guessed from the latest flow or HEAD.

Run skills sequentially, not in parallel against the same knowledge base. If another writer changes state during analysis, the skill stops publication rather than overwriting it.

## 8. Step three: organize what you have learned

After one or several completed analyses:

```text
Load and use the second-brain-organize skill for /Projects/pkr-tool-docs.
Organize the completed flow descriptions into shared business knowledge,
per-repository technical notes and an index for a coding agent.
```

Possible outputs, created only when useful:

- `index.md`.
- `domain/glossary.md` and `domain/rules.md`.
- `domain/cross-repository-flows.md` when enough evidence exists.
- `repositories/orders-api/technical.md`.
- `open-questions.md`.

Organize extracts and connects established knowledge. It does not discover undocumented behavior or certify source code again. Drafts and mismatched checkpoints cannot become established facts. Similar names across repositories are not automatically the same business concept.

## 9. Bootstrap projects individually into one knowledge base

Yes: every project's generated knowledge goes into `/Projects/pkr-tool-docs`. Application source code stays in its original checkout. Install the skills once, then select repositories one by one.

| Content | Location under /Projects/pkr-tool-docs |
| --- | --- |
| OpenCode skill definitions | `.opencode/skills/` |
| OpenCode runtime permissions | `opencode.json` |
| Registered source projects | `config.json` |
| All map and flow checkpoints | `state.json` |
| Project A map and coverage | `repositories/orders-api/` |
| Project B map and coverage | `repositories/payments-api/` |
| Project A detailed processes | `repositories/orders-api/flows/` |
| Project A unfinished work | `repositories/orders-api/drafts/` |
| Project B detailed processes | `repositories/payments-api/flows/` |
| Business concepts and rules | `domain/` |
| Navigation across the knowledge base | `index.md` |

All project-specific documents share one parent: `repositories/<repo-id>/`. map.md, coverage.md and technical.md sit directly there; process descriptions live in flows/ and unfinished notes in drafts/. Shared concepts stay in domain/ and state.json remains a single file.

### First project

Run map for orders-api, invoke analyze for each process you choose, then organize when useful. Mapping itself is not a full detailed analysis of the project.

### Second project

In the same workspace, ask:

```text
Load and use the second-brain-map skill.
Add repository payments-api from /Projects/payments-api,
remote origin, branch develop.
Use the existing knowledge base at /Projects/pkr-tool-docs.
Preserve all orders-api documents, configuration and state.
```

This adds a separate config entry and a `repositories.payments-api` state key. It must not reset orders-api, reanalyze it, or mark any payment flow analyzed. Use a unique stable repository ID for each project so paths cannot collide.

Then choose one process:

```text
Load and use the second-brain-analyze skill for repository payments-api.
Analyze the payment confirmation process, starting at PaymentConfirmedListener.
Use /Projects/pkr-tool-docs as the knowledge base.
```

Finally, invoke organize manually to integrate the newly completed evidence with existing shared knowledge. Business concepts are merged only when supported by evidence. Technical details remain per repository. Cross-project summaries preserve each flow's own branch and commit. You do not need to finish every process in one project before adding another.

## 10. Use the knowledge while coding

A useful prompt for your coding agent:

```text
Read /Projects/pkr-tool-docs/index.md.
Find the notes relevant to the change below, inspect their source checkpoints,
and verify the relevant behavior in current code before editing.
Use the knowledge base to locate rules, affected processes and tests.
Treat documented unknowns as unknowns.

Change: <describe your task>
```

The knowledge base speeds up navigation and reasoning; it is not a replacement for current code. It can be stale after other developers merge changes. Automatic detection and incremental updating are deliberately deferred.

To check usefulness after several analyses, ask where to add a validation, what a state change affects, how duplicate messages behave, and which tests document a failure case. Verify answers against the cited code. If the agent still has to rediscover the whole process, improve that process note.

## 11. Troubleshooting

| Situation | Expected behavior / next action |
| --- | --- |
| Repository or branch is unspecified | Provide it once; do not let the agent guess |
| Fetch fails | Fix access or connectivity; no silent use of stale refs |
| Saved commit is missing or not an ancestor of the configured branch | Skill explains and stops replacement; investigate history before choosing a new baseline |
| Branch setting differs from a flow checkpoint | Clarify the intended source before replacement |
| Coverage map is older than current code | Compare map.last_mapped_commit to the flow snapshot; analyze verifies only its selected entry, while a successful rerun of map refreshes the inventory checkpoint |
| Existing state has no map object | Rerun map to record it; preserve flow entries and never infer a map checkpoint |
| Process name is ambiguous | Specify the endpoint, consumer or method |
| Source code is unavailable | Provide access; do not generate code claims from memory |
| Tests disagree with implementation | Record the contradiction and evidence; do not invent intended behavior |
| A local implementation path remains unread | Keep the analysis a draft |
| External system implementation is unavailable | Describe the observed contract and mark the boundary unverified |
| `state.json` is malformed | Repair or restore it; do not reset all checkpoints |
| Documents and state disagree after a crash | Revalidate the selected flow before publishing it as completed |
| You want incremental updates | Not included; a later skill can use the recorded checkpoints |

## 12. Relationship to the original step-by-step approach

| Original steps | This package |
| --- | --- |
| 1–3: scope, repository map, entry-point inventory | map |
| 4–7: select a flow, trace it, inspect tests, write evidence | analyze |
| 8: repeat for more flows | You invoke analyze for each chosen process |
| 9–10: common knowledge and navigation | organize |
| 11: assess usefulness on realistic questions | Manual check described above |
| 12: incremental updates | Deferred |

The `docs/` folder contains a concise implementation record and planned acceptance scenarios. These are reference material, not additional skills or required runtime steps.

## 13. OpenCode documentation and verification

The integration follows the official documentation checked on 2026-09-29:

- [V1 skills](https://opencode.ai/docs/skills/)
- [V1 permissions](https://opencode.ai/docs/permissions/)

The archive structure, skill metadata, links and JSON examples were checked locally. The skill behavior was exercised with synthetic Git repositories in the authoring environment. The package has not been run in your OpenCode installation; version, provider and existing policy settings remain environment-specific.

## 14. If you already generated notes using the older layout

No migration is needed for a new knowledge base. If you already have `flows/<repo-id>/` or `drafts/<repo-id>/`, move those existing documents into `repositories/<repo-id>/flows/` and `repositories/<repo-id>/drafts/`. Update relative Markdown links in the moved documents and all incoming links (coverage, index and shared notes). Update each affected state.document path; preserve the repository ID, flow ID, branch and commit exactly. Relocation alone is not a new source analysis. If both old and new destinations exist, compare them before moving and never overwrite one blindly. Keep a backup until links and state paths are verified. The archive does not move files on your computer automatically.
