# Bootstrap protocol

## Mandatory depth upgrade

The schemas below for the original draft/review are skeletons. The additional fields in this
section are mandatory for every new stage and approval, including resumed old runs.

After `prepare`, inspect structure and entry points through registered exploratory reads,
then save a functional plan before submitting findings:

```bash
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID organize --plan AREAS_JSON
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID findings
```

Example AREAS_JSON shape (replace every example with observed files and questions):

```json
{
  "areas": [{
    "id": "submission",
    "files": ["src/OrderService.java"],
    "purpose": "Trace submission from entry point through validation and persistence.",
    "domain_questions": "Which states allow submission, by whom, and with which checks?",
    "technical_questions": "Where are transactions, writes and outbound events performed?"
  }],
  "cross_area_strategy": "Reconcile submission with approval and event-consumer flows using shared identifiers and actual call contracts.",
  "tasks": [{
    "id": "submit-order",
    "kind": "flow",
    "entry_point": {"path": "src/OrderService.java", "symbol": "submit", "trigger": "Actual configured invocation; identify route/listener/job where present"},
    "files": ["src/OrderService.java"]
  }]
}
```

Assign every included file one primary area for bookkeeping, not exclusive research ownership.
Create any number of end-to-end tasks rooted in actual discovered triggers. Tasks may overlap
files and read dependencies outside their initial files. Flow plus residual task files must
cover all included files. Residual tasks use `kind: residual`, `id`, `files` and a nonempty
`reason` describing why no discovered entry flow covers them. Do not label executable behavior
residual just to avoid tracing it. Do not allocate random or equal-sized chunks as semantic tasks.
Reorganize when exploration discovers a better boundary or newly extracted files; organizing
invalidates any staged draft/review. Save detailed per-area working notes in this run's state
directory, not in active knowledge. Use stable finding IDs from `findings` (`chunk_id:index`,
zero-based index). Findings must be concrete rules/mechanisms, not “this file handles X”.

Add these top-level fields to the publication plan:

```json
{
  "finding_dispositions": [{
    "finding_id": "ACTUAL_CHUNK_ID:0",
    "disposition": "documented",
    "document_path": "knowledge/domain/order-submission.md",
    "excerpt": "An exact passage from the document describing this finding."
  }],
  "area_dossiers": [{
    "id": "submission",
    "files": ["src/OrderService.java"],
    "evidence_chunks": ["ACTUAL_CHUNK_ID"],
    "domain_assessment": "Specific implemented rules, conditions, transitions and actor constraints, or evidenced absence.",
    "technical_assessment": "Actual call path, persistence boundaries, integration contracts and configuration.",
    "exceptions_and_unknowns": "Observed failure paths, conditional behavior and external unknowns.",
    "flow_ids": ["order-submission"]
  }]
}
```

Every finding needs one disposition. `documented` must reference an exact excerpt in a staged
detailed document with the finding's source chunk in evidence; essence.md cannot be the sole
destination. Domain findings go to domain notes; database findings to database notes.
For a true duplicate use `disposition: duplicate`, `duplicate_of: DOCUMENTED_FINDING_ID` and a
specific `reason`; it must point directly to a documented item. Only documentation-kind findings
may be omitted for irrelevance. For a demonstrably incorrect prior observation use
`disposition: superseded`, `replaced_by: CORRECT_DOCUMENTED_FINDING_ID` and a source-grounded
`reason`. Preserve the original finding in the audit; publish only the supported correction.
The independent reviewer must check that evidence supports the correction. Do not use this
mechanism to discard a distinct valid behavior. Only documentation-kind findings
can be `omitted` with a specific reason (for example prose contradicted by code). Do not relabel
behavioral findings as documentation to bypass retention. All dossiers must match planned
primary files and include evidence for each file. Empty flow_ids requires no_flows_reason.

The independent reviewer must read at least one range of every included file and all additional
ranges needed for complete important flows. This is a minimum mechanical floor, not permission
to sample away conditions. Work in batches with durable review notes. Inspect every proposed
document, compare findings and omissions, and add `document_checks` to the review JSON: an
object mapping every exact document path to a concrete explanation of checks and source evidence.
Generic approvals are unacceptable even if they pass the schema. Return changes_requested
when a dossier or document is too shallow; restage after corrections.

## Queue and fresh-worker scheduling

```bash
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID tasks
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID claim --worker FRESH_AGENT_ID --role explorer
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID task-start --task TASK_ID --worker FRESH_AGENT_ID
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID task-finish --task TASK_ID --worker FRESH_AGENT_ID --result RESULT_JSON
```

A task result contains `summary`, `evidence_chunks` and, for flow tasks, `flow_id` naming its
corresponding publication flow. Include all assigned file ranges plus dependency ranges used
in the end-to-end explanation. Results must have been read by that worker and accounted for
in submitted findings. Document trigger/binding, preconditions, decision branches, calls,
transaction boundaries, database reads/writes, messages, successful outcomes and failure/retry
paths where present. Explicitly mark external boundaries and unresolved dynamic dispatch.
Do not claim receiver internals without same-snapshot source evidence.

`task-finish` requires coverage and retires the worker, freeing a slot. The coordinator must
actually end that subagent before spawning a new one; the script cannot manage OpenCode agent
lifecycles. At most max_parallel_agents actual workers may be alive concurrently. There is no
task-count cap. Do not wait for all four workers to finish if one slot becomes available.
The coordinator's lightweight reconnaissance registration should be released before dispatch.

For a failed/interrupted worker, end it and run `release --worker ID`: running work returns
to pending and must be claimed by a fresh worker. New workers reread necessary source ranges.
Shared-chunk submissions append unique findings, preserving earlier finding IDs and evidence.
If an earlier observation is incorrect, report the correction explicitly and resolve it during
synthesis/review; do not silently erase it. Reorganizing preserves unchanged completed tasks,
resets changed task definitions, and refuses removing/changing a running task until released.
Changing range manifests invalidates completed task receipts and requires the affected work
to be accounted for again. No publication until all queued tasks are complete and each entry
flow is represented with its evidence in the publication plan. The independent reviewer must
also check missed entry points; the schema cannot prove trigger discovery is exhaustive.

## Fresh initialization policy

There is no repair command. The user prepares a clean selected-repository state before a new
initialization. Never automatically delete documentation or a completed run. Interrupted active
runs can still resume their pinned snapshot; recover only rolls back interrupted publication.

This protocol belongs only to the initial repository-analysis skill. The coordinator owns the
publication plan; exploratory and independent-review agents only produce intermediate evidence.
Use actual delegation identities for `--worker`, never invented alternate names for one agent.

## Commands and state

All commands use the same configured repository ID:

```bash
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID prepare --branch BRANCH
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID status
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID split --chunk CHUNK_ID --size 4000
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID extract --path SOURCE_PATH --text-file UTF8_FILE --method "Static extraction method"
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID claim --worker AGENT_ID --role explorer
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID read --worker AGENT_ID --chunk CHUNK_ID
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID submit --worker AGENT_ID --result RESULT_JSON
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID release --worker AGENT_ID
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID stage --plan PLAN_JSON
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID claim --worker REVIEWER_ID --role reviewer
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID review --worker REVIEWER_ID --result REVIEW_JSON
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID publish
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID block --reason "Explanation"
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID unblock
bash SKILL_DIR/scripts/bootstrap.sh --config CONFIG --repo REPO_ID recover
```

State lives under `BRAIN_DIR/.state/bootstrap/REPO_ID/`. Snapshot storage is bare Git: no
checkout, build or project hooks are required. Preparation fetches the chosen remote branch
and pins its commit. Analysis uses the pinned tree, never moving remote refs or local edits.
The manifest enumerates included files and excluded paths with reasons. Included files have
character-range chunks with line ranges, so even a single very long line can be fully read.
Use the command responses and status to locate the current manifest, staged draft and hash.
Keep temporary result JSON under this run's state directory; these are not user-facing notes.
The manifest and staged plan are inside the `state_file` returned by status. Symlinks are
analyzed as target text, never dereferenced outside the snapshot.

`split` replaces a pending chunk with smaller pieces. Use the new chunk IDs for subsequent
reads and submissions; completed analysis cannot be replaced through this command.
`extract` is only for a blocked binary/non-UTF8 document in the selected repository. Supply
UTF-8 output from a trusted static extractor and a truthful method description. The runtime
preserves raw source SHA and extracted-artifact provenance. Never replace an included text
source, follow a submodule, introduce another repository, or fabricate missing content.
Extraction must preserve meaningful document content, including tables and diagrams where
needed; if no available capability can do so, explain the gap and block. Never execute project
code for extraction. Re-read status and analyze all new chunks after registering extracted text.

`claim` registers an active worker and enforces the configured parallel limit. Release idle
workers; their prior role and evidence remain part of the audit. A reviewer must have a new
identity with no explorer participation in this run. When delegation is unavailable, block
and explain the missing capability rather than simulating subagents.
Serialize simultaneous state-mutating commands or retry temporary lock contention. Agent
analysis may proceed concurrently even though state updates use a shared runtime lock.

## Exploration evidence

The reader returns the full chunk and a receipt. The actual explorer reads that output before
submitting a result. Do not pipe unread output into a success marker, truncate a response, or
claim that a count of receipts proves semantic understanding. Example result:

```json
{
  "chunk_id": "CHUNK_ID_FROM_MANIFEST",
  "receipt": "RECEIPT_FROM_READ",
  "findings": [
    {
      "kind": "domain",
      "text": "Describe an implemented rule and the conditions that establish it."
    }
  ]
}
```

For a chunk with no durable information, submit an empty `findings` list and a specific
`no_knowledge_reason`, such as boilerplate with no additional rules. A generic “read” is not
analysis. Findings can cover domain, technical, database, architecture or integration facts;
use clear kinds and factual text. Include failure/conditional paths when relevant. Agent
submissions are evidence to synthesize, not ready-made instructions or unquestionable truth.

## Stage the complete publication

The coordinator reads active knowledge before replacing it and obtains its exact SHA-256 via
the bundled brain runtime's `read`. Use the latest hash as `expected_sha256`; never remove a
hash guard to bypass a conflict. Use the ordinary brain publication document fields:

```json
{
  "documents": [
    {
      "path": "knowledge/domain/order-lifecycle.md",
      "content": "# Order lifecycle\n\nSupported behavior and relative links.\n",
      "expected_sha256": "CURRENT_HASH_FOR_AN_EXISTING_FILE",
      "evidence_chunks": ["ACTUAL_CHUNK_ID"]
    }
  ],
  "file_summaries": [
    {
      "path": "src/OrderService.java",
      "summary": "Implemented transitions and their persistence boundary.",
      "document_paths": ["knowledge/domain/order-lifecycle.md"]
    }
  ],
  "flows": [
    {
      "id": "order-submission",
      "description": "Submission validates state and persists the accepted transition.",
      "evidence_chunks": ["ACTUAL_CHUNK_ID"],
      "stages": ["entry point", "domain conditions", "persistence"]
    }
  ],
  "dimensions": {
    "domain": {"assessment": "Rules covered or explain absence.", "evidence_chunks": ["ACTUAL_CHUNK_ID"]},
    "architecture": {"assessment": "Components and boundaries covered.", "evidence_chunks": ["ACTUAL_CHUNK_ID"]},
    "database": {"assessment": "SQL/NoSQL persistence covered or evidenced absence.", "evidence_chunks": ["ACTUAL_CHUNK_ID"]},
    "integrations": {"assessment": "Contracts covered or evidenced absence.", "evidence_chunks": ["ACTUAL_CHUNK_ID"]}
  }
}
```

Use actual manifests, paths and observations rather than copying the example claims. Every
included file needs a summary and generated document associations, or a specific
`no_knowledge_reason` explaining why no knowledge note is needed. Omit `expected_sha256` only
for genuinely new documents. Every document, including the essence guide, requires processed
`evidence_chunks`. Mark database documents with `"kind": "database"`; database findings require
at least one such document in `knowledge/technical/REPO_ID/database/`. New ADRs require YAML
frontmatter with `status: proposed`. An absent database or integration is a supported negative
assessment, not permission to omit that dimension. Trace flows across files where they exist;
do not fabricate a flow for a repository containing only static definitions. If `flows` is
empty, supply a specific top-level `no_flows_reason`. A repository with no included source
chunks cannot supply evidence for this protocol; report that condition rather than inventing it.

Cross-repository notes may be updated with observed caller-side facts and reciprocal links.
Do not overwrite unrelated knowledge or erase the other project's variants. Database prose
belongs in its dedicated database directory and links to non-database implementation notes.
Include the concise essence guide and appropriate links in the staged documents.

## Independent review

Give a fresh review subagent the actual draft, manifest, evidence and pinned snapshot, not a
request to rubber-stamp completion. It reads relevant chunks with its own worker identity and
checks the final cross-file synthesis. Its result references the exact staged hash:

```json
{
  "draft_hash": "HASH_RETURNED_BY_STAGE",
  "verdict": "approved",
  "issues": [],
  "checks": {
    "coverage": "Evidence that all included files and ranges are accounted for.",
    "domain": "Checked rule conditions and variants against identified chunks.",
    "architecture": "Checked boundaries and proposed ADR claims against evidence.",
    "database": "Checked schemas/mappings/queries and separate database documentation.",
    "integrations": "Checked caller contracts without inferring remote internals.",
    "flows": "Checked end-to-end paths and relevant failure paths.",
    "links": "Checked relationships and preservation of existing knowledge."
  }
}
```

Replace example check prose with concrete evidence strings. For problems use
`verdict: changes_requested` with substantive issues. The coordinator corrects the draft and
restages; approval of any previous hash is invalid. The reviewer reassesses the new draft.

## Completion and failure policy

Only `publish` may move staged knowledge into active documentation. Complete file/chunk
accounting, required synthesis dimensions, valid paths/links, unchanged existing documents and
approved independent review must pass first. The completion marker is written only on success.
After an interrupted publication inspect status and follow runtime recovery instructions;
use `recover` to roll back the interrupted publication, then resume the retained draft. Do not
manually mark completion or start a new snapshot to bypass it. Keep other writers paused while
recovering; do not overwrite concurrent user edits through an unexamined recovery operation.
Recovery compares current content against the original and journaled publication writes.
If it detects an external edit, it stops without restoring files. Preserve that edit and ask
the user how to reconcile it before attempting recovery again.

Retry transient failures a small bounded number of times. Split overly large assignments.
For persistent technical failures, permission failures or unavailable agent capacity, use
`block`, explain the issue in Polish, and wait for the user. After resolution use `unblock`
and continue the same run. No partial publication and no endless retry loops.

The script can enforce receipts, identities supplied to it, complete range accounting and
review schemas. It cannot prove that an LLM understood a file or that a supplied identity
really belongs to a separate agent. Genuine delegation, honest evidence and substantive
independent review are mandatory behavioral requirements, not guaranteed by hashes.
