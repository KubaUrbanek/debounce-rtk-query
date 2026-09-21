# Second Brain v2 — implementation plan

Status: Implemented locally; live integration and semantic acceptance pending.
Date: 2026-09-18.
Companion: [business scenarios](second-brain-tests.md).
Extension: [one-time bootstrap plan](bootstrap-plan.md) and [bootstrap scenarios](bootstrap-tests.md).

## Goal and agreed behavior

BR1. Three independent ongoing skills, one agent. A fourth independent initial-analysis skill
delegates exploration and independent review, with `max_parallel_agents` defaulting to 4.
Polish interaction, English Markdown artifacts.
Linux; Python standard library only; fixed-schema YAML; no automatic Git commit/push.
BR2. One system report per requested day, all merged MRs targeting develop* across stable
repository IDs. Europe/Warsaw, half-open local day, merged_at rather than commit timestamps.
Grouped cumulative outcomes, technical and business changes, sources, no author/SHA inventory.
BR3. Today-only personal daily: exact configured author emails and author dates, all reachable
local/remote commits, experiments and alternatives, plus include_in_daily=true inbox sources.
Whole conversations with explicit attribution; only explicit tasks/agreements. Late notes
included today with event dates. Existing report updated, including earlier archived-source facts.
BR4. Knowledge only from explicit inbox facts; relevant existing active knowledge may be read.
Shared domain; technical shared/per repository at agent discretion. Stable topical Markdown,
meaningful links; essence is a guide. No personal-report feedback loop.
SQL and NoSQL documentation is separate in `knowledge/technical/REPO_ID/database/`, linked to
domain and application concepts. The fourth skill initializes knowledge from a pinned remote
source snapshot; its code-wins rule is specific to that workflow and does not change BR5.
BR5. Before writing, ask about unknown scope and every contradiction/change of existing rule.
Deferred issues become unknown scope/conflict notes. New ADRs proposed; accepted predecessor
remains valid until successor acceptance; then superseded with links.
BR6. Separate content hashes for knowledge/daily. Archive only after required stages and valid
date. No-durable-value material may be completed without topic generation. Bad dates stay.
Archive content is never read; known system report may be renamed back to inbox before update.
BR7. Errors are separate from no activity. Partial reports may supply sourced knowledge.
Empty activity produces only a message. No protected user section; existing facts must survive reruns.

## Implementation steps and acceptance

| Step | Implementation | Acceptance |
|---|---|---|
| P1 | Fixed parser and source metadata in runtime/brain.py | AC1: invalid/unknown YAML rejected without external dependencies |
| P2 | Paginated glab collection, local-time filter and diff limits | AC2: merged day and target prefix determine inclusion, errors retained |
| P3 | Local/remote Git author-date collection and daily inbox selection | AC3: local experiments included once per SHA; late/invalid dates handled |
| P4 | Semantic instructions in three SKILL.md files | AC4: independent scope, source provenance and human decisions preserved |
| P5 | Optimistic publication, graph links, hash marking and archive moves | AC5: source changes invalidate markers; both required stages gate archive |
| P6 | Template, setup and package replication | AC6: installable package with one authoritative runtime and identical deployed copies |

## Risks and boundaries

No live company GitLab available during implementation. API authentication, permissions and
server diff limits require deployment verification. A day's MR diffs establish changes,
not every historical detail of the complete system. Current MR descriptions may have changed.
Local deleted/unreachable commits cannot be recovered automatically. Markdown links use the
documented inline syntax; arbitrary embedded HTML/reference-link formats are outside the graph
helper's supported subset. Semantic correctness needs human acceptance with real materials.

## Handoff

Start at SETUP.md, config.example.yaml and runtime/protocol.md. Runtime source is authoritative;
run build.sh after edits to refresh installed skill copies. Do not reintroduce archive scanning,
automatic commits, commit-date system reports, all-to-all links or dependencies. Update both
this plan and scenarios if business behavior changes.
The bootstrap extension adds its own runtime, coverage/review gates and one-time state.
Follow its companion plan for initial source analysis; do not use the inbox publication
command to bypass its gated publisher.
