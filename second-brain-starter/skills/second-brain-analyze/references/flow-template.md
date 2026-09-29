# Flow document template

Use the headings below, omitting genuinely irrelevant sections and explaining why when absence matters. Replace placeholders with observed facts. Keep the document useful for deciding where and how to change code.

# <Business operation>

- Repository: <configured ID>
- Branch: <configured branch>
- Analyzed commit: <full pinned SHA>
- Status: Completed / Draft
- Scope: <entry point, variants and explicit external boundaries>

## Purpose and entry points
Describe the observable outcome. List routes, consumers, jobs or callable entry symbols. Do not infer business intent beyond evidence.

## Preconditions and authorization
Identify inputs, actor restrictions, starting states, validations and rejection outcomes. Say when authorization is delegated or cannot be established.

## Execution and variants
Trace entry -> decisions -> persistence -> events/integrations -> result. Include important alternate and failure branches, configuration switches and asynchronous continuations visible in this repository. Link sources alongside claims.

## Business rules and state transitions
Use concrete conditions and resulting behavior. Identify invariants, exceptions and side effects. Separate implemented rules from inferred intent.

## Persistence and external effects
Record reads/writes, observed transaction scope, events and external contracts. Do not assume atomicity across a database and a broker. Explain what remains unverified across repository boundaries.

## Failures, retries and repeated execution
Describe error propagation, rollback where established, retry configuration, duplicate handling and partial success. State unknowns explicitly.

## Tests and confidence
Link relevant tests and the behaviors they assert. Separate implementation facts from test expectations. Record gaps and contradictions. State whether tests were only read or actually run, with actual results if run.

## Change guidance
Identify the main extension points, related processes and tests to inspect. Describe evidenced coupling; avoid speculative recommendations.

## Sources
List repository-relative files, symbols and roles, including relevant configuration, migrations and tests. Associate them with the pinned commit.

## Open questions
List unresolved facts and boundaries. Distinguish an external unknown from an unfinished reachable local code path. Unfinished local analysis keeps this document a draft.
