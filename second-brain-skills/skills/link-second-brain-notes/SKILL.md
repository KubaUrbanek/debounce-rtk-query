---
name: link-second-brain-notes
description: Find meaningful connections between finished Second Brain knowledge, ADR, personal and thought notes and automatically add reciprocal links with explanations, preserving substantive text. Use for an on-demand relationship review, excluding inbox, drafts and archive.
---
# Connect finished notes

Speak Polish; write English link explanations. Use one agent and the bundled standard-library
scripts. Read [thoughts protocol](references/thoughts-protocol.md).
Read [analysis depth](references/analysis-depth.md); complete note coverage and meaningful
relationships matter, not a target number of links.

1. Run scripts/thoughts.sh inventory --scope notes. This is the exact eligible scope:
   knowledge/, architecture/, personal/, thoughts/notes/. Never inspect inbox, drafts, archive,
   source repositories or private snapshots. Do not use the broader brain graph inventory.
2. Read all eligible notes in manageable batches with the guarded `read` command. Track
   completion; if the collection exceeds context, retain topic summaries and reread actual
   candidates before linking. Do not claim a full review after sampling a subset.
   Persist a path/hash/topic coverage ledger and specific candidate relationships under .state/
   when the collection is large. Account for every note, including notes with no justified new
   links; revisit cross-batch candidates rather than only linking adjacent notes. A filename
   inventory or generated index is not a substitute for reading substantive note content.
3. Find substantive relationships: the same domain concept, supporting or contrasting
   reasoning, implementation constraints, a reflection on a documented design, related
   experience or a proposal affecting a known component. Mere keywords are insufficient.
   Ideas and personal learning remain proposals/observations, not facts or accepted ADRs.
4. Add justified links automatically, without asking for each connection. Use a short English
   explanation that makes sense in both directions. Read both original notes; never infer a
   relationship from filenames alone. If the connection is uncertain, omit it rather than
   invent it or ask the user to approve a speculative link.
   For each candidate retain the supporting passage from both endpoints in the analysis.
   Explain the concrete dependency, shared rule, causal connection or contrasting assumption.
   Do not imply that a personal idea is implemented merely because it links to factual
   documentation. Generic "related" explanations fail this check.
5. Prepare only the relation JSON from the protocol, including exact hashes of both endpoints.
   Run `link`. It appends reciprocal Connections entries, skips existing semantic connections,
   and cannot replace the substantive note text. Do not manually rewrite notes, remove links,
   regenerate personal reports or change source/decision status. Repeated runs are idempotent.
6. Report reviewed scope and added connections in Polish. Recover interrupted publication
   before continuing. Do not commit or push.
