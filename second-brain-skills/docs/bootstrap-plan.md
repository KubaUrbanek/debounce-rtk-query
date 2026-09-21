# Repository bootstrap implementation plan

Companion: [acceptance scenarios](bootstrap-tests.md).
Runtime contract: [bootstrap protocol](../skills/bootstrap-second-brain/references/bootstrap-protocol.md).

## Agreed behavior

Initialize exactly one configured repository once, from a selected remote branch pinned to a
commit. Resume incomplete analysis against the same snapshot. Existing active knowledge can
be augmented; archive is not read. No commit history or live database queries are needed.
Documentation in the repository is included, but implemented code wins contradictory prose.

Use common automatic exclusions for tests, generated content, dependencies and build artifacts.
Every included file is chunked with complete character/line coverage. Actual subagents analyze
assigned chunks, recording findings or concrete no-knowledge explanations. A coordinator
resolves cross-file flows and publishes only meaningful concepts. The configurable parallel
limit defaults to four; only bootstrap uses this delegation workflow.

Domain knowledge is shared with explicitly scoped project variants. Technical knowledge is
per project unless a shared principle is supported. SQL and NoSQL have a dedicated per-project
database directory. Other projects' active notes may gain supported caller-side integration
facts and links, without analyzing their code or inventing receiver behavior. New ADRs are
proposed; missing rationale is unknown. Existing accepted ADRs are not silently superseded.

Stages are preparation, exploration, synthesis, independent review and publication. An actual
review subagent that never explored this run checks the staged draft against source evidence.
All corrections require restaging and review of the new hash. No incomplete documentation is
published. Persistent failures block, preserving work until human response; retries are bounded.
Unknown externally controlled runtime values are documented limitations, not analysis failures.

## Implementation responsibilities

| Component | Responsibility |
|---|---|
| `runtime/bootstrap.py` | Snapshot, manifest, chunk receipts, worker roles, coverage, staging, review gates and one-time completion |
| `scripts/bootstrap.sh` | Portable Bash entrypoint invoking Python standard-library runtime |
| Coordinator skill | Real delegation, source interpretation, cross-file synthesis, document selection and final handoff |
| Explorer subagents | Full assigned reads, evidence-based findings, no direct active-document writes |
| Independent reviewer | Check exact draft and source relationships; report concrete gaps before publication |
| Shared brain runtime | Existing document hashes, path/link validation and generated graph maintenance |

Technical state stays in `.state/bootstrap/REPO_ID/` as JSON and pinned Git objects. User-facing
notes are linked English Markdown. Interaction is Polish. No third-party Python dependencies,
project execution, automatic Git commit or push. Existing three skills retain their own
collection scope, inbox workflow and human conflict decisions, but use the same dedicated
database documentation structure.

## Limits that must remain explicit

Receipt and range validation establishes mechanical coverage, not semantic comprehension.
Actual agent identities and substantive review must be honored by the orchestrator; IDs alone
cannot authenticate an LLM as an independent worker. Static analysis cannot establish unknown
external settings. Full coverage is a gate on the selected included material, not a claim of
perfect knowledge or proof that the code has no defects. Completion is not recorded until
publication succeeds. See runtime status on recovery; never bypass a gate by editing state.
