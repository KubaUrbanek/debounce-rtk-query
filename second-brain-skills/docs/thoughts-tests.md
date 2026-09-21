# Thoughts and links acceptance

See [setup](../SETUP.md) and [publication protocol](../runtime/thoughts-protocol.md).

## Agreed behavior

- A rough draft may mix ideas, learning and reflections, with no manually entered connections.
- Ideas accumulate in one document; learning/reflections split by subject with agent-selected titles.
- Existing matching notes are extended; repeats are omitted and new evidence retains provenance.
- Alternative views remain side by side. Ambiguous intent requires a user question before generation.
- Useful agent suggestions remain separate from the user's words.
- Knowledge/ADRs provide context and links, never automatic factual updates from personal thoughts.
- Processed draft originals are archived; archive content is never read. No thought input enters daily.
- Connection review scans finished knowledge, ADRs, personal and thought notes only.
- Links and explanations are automatic, meaningful and reciprocal; substantive prose stays unchanged.

## Executed verification

Run `python3 -m unittest discover -s tests -v`. The added tests use temporary files to check
archive provenance, clarification and destination gates, source/output version checks,
complete draft accounting, reciprocal idempotent links, excluded folders, original prose
preservation, crash recovery, external-edit protection, archive collisions and incoming links.
Existing workflow and bootstrap regression tests run in the same suite.

## Semantic checks in your environment

Try a mixed draft with a duplicate existing idea, a new learning, an alternative reflection
and an ambiguous sentence. The agent must ask about the sentence, extend the right notes,
preserve both views, and avoid turning observations into system facts. Then run connection
review twice: the second run should add nothing unless new relationships are justified.
Tests of hashes and schemas do not establish that an LLM interpreted personal intent correctly.
