# Bootstrap acceptance scenarios

These scenarios define acceptance, not a claim that every semantic case has been executed.
Run automated runtime tests in isolation; assess source interpretation with real repository
fixtures and actual independent agents. See [implementation plan](bootstrap-plan.md).

## Executed runtime checks

On 2026-09-19, `python3 -m unittest discover -s tests -v` passed all 34 tests
(18 ongoing-workflow tests and 16 bootstrap tests). Bootstrap fixtures cover pinned
resume, exclusions, full range accounting, read receipts, worker limits, independent
review gates, separate database outputs, one-time initialization, blocking/unblocking,
document extraction integrity, and rollback after errors or interruption. Recovery also
preserves CRLF notes and refuses to overwrite external edits after interruption.
All four skill manifests passed validation; shell scripts passed Bash syntax checks.
These results do not certify LLM comprehension or live workplace integration.

## Semantic and workflow scenarios

| Scenario | Expected outcome |
|---|---|
| Select one repository and remote branch | Only that project's pinned source is read; local edits remain untouched |
| Remote branch changes during exploration | Existing run and resume retain the original commit |
| Try another bootstrap after successful completion | Rejected for the same stable repository ID, even with a different branch |
| Interrupt exploration before completion | Saved receipts/results remain available; no active knowledge is published |
| Included long file or one very long line | All character ranges must be accounted for; no truncation counts as full coverage |
| Tests, generated code, dependencies and build output | Common rules exclude them with reasons; ambiguous files remain included |
| README contradicts implementation | Domain description follows code and identifies contradictory source prose |
| Explorer skips one chunk | Stage/publication cannot complete until the missing analysis is supplied |
| Explorer claims a result without reading it | Receipt gate rejects mechanically missing reads; review checks substantive evidence |
| File contains only boilerplate | Specific no-knowledge reason accounts for it without a pointless topic note |
| Code has a multi-file entry/validation/persistence/event flow | Synthesis connects stages and relevant failure paths with evidence |
| SQL repository | Separate database notes describe supported tables, keys, relations, indexes, migrations and query/write paths |
| NoSQL repository | Separate database notes describe supported document/container structure, partitioning, indexing and TTL |
| No database or outbound integration exists | Explicit evidenced assessment records absence; nothing is invented |
| Runtime value exists only outside the repository | Describe conditions and unknown active value; do not connect to live systems |
| Existing common domain topic has another project's variant | Preserve that variant; add or correct only the analyzed project's facts |
| Caller references another service | Link and supplement active notes with proven caller contracts, not guessed receiver internals |
| Code-derived architecture decision | Proposed ADR, identified evidence, unknown rationale/alternatives where absent |
| Existing accepted ADR conflicts with observed design | Preserve decision status/history; do not silently supersede it with proposed ADR |
| Same explorer attempts independent approval | Rejected; fresh actual reviewer required |
| Draft changes after approval | Prior approval invalid; new exact hash must be reviewed |
| Reviewer reports a missing flow | Correct analysis and draft before publication; no partial output |
| Fifth worker when configured maximum is four | Worker claim rejected until an active slot is released |
| Repository has 23 entry flows and a four-worker limit | Plan retains all 23 tasks; at most four workers run concurrently |
| One worker completes before the others | Its durable task result releases the slot; close it and spawn a fresh agent for the next task |
| HTTP, Kafka and cron entry points call the same service | Separate triggered flow tasks may share files and evidence; preserve distinct conditions and reconcile common behavior |
| Entry point is registered through configuration instead of an annotation | Discovery examines registration/wiring and includes the actual trigger |
| Included migration or library file has no discovered trigger | Justified residual task analyzes it; no coverage exclusion is inferred |
| Worker reads a dependency outside its initial file list | Allowed inside the pinned repository; include the dependency evidence in its result |
| Finished flow task is absent from staged publication flows | Staging fails until the result's flow ID is represented |
| A task is pending despite complete chunk receipts | Staging remains blocked; read coverage does not replace task completion |
| An ongoing inbox/daily/thought/link skill uses the shared depth contract | Its original source restrictions and single-agent workflow still apply |
| User requests repair of completed state | Explain that no repair mode exists; never delete user state or knowledge automatically |
| Transient command failure | Bounded retries; work retained |
| Persistent authentication/read failure | Block, explain in Polish, wait for human reaction, resume pinned run |
| Existing note changes after draft staging | Optimistic update fails; reread, merge and obtain fresh review |
| Invalid relative link or unsafe destination | Publication fails before successful completion marker |
| Successful complete run | Linked English knowledge and essence guide published; marker blocks reinitialization; no commit/push |
| Standard inbox update after bootstrap | Updates same domain/technical/database locations using inbox facts and existing human-conflict rules |

Review dimensions are coverage, domain, architecture, database, integrations, flows and links.
Schema success is necessary but insufficient: reviewer explanations must identify actual
evidence and meaningful checks. Test reports must distinguish runtime verification from
semantic acceptance and live GitLab/OpenCode integration that remains environment-dependent.
