# Analysis depth upgrade

See [analysis contract](../runtime/analysis-depth.md) and [setup](../SETUP.md).

## Problem and outcome

The prior bootstrap could account for all source ranges yet produce a few generic sentences.
Read coverage, document completeness and semantic correctness are different properties.
This revision retains coverage and adds functional planning, finding-to-document accounting,
per-area synthesis and broader independent review. Other skills gain evidence-retention and
source-specific depth rules; personal daily remains concise and thought refinement stays faithful.

## Bootstrap implementation

- Organize before submitting analysis: all included files have one functional primary owner.
- Researchers follow full use cases and read dependencies across ownership boundaries.
- Preserve detailed working evidence on disk; the coordinator integrates instead of compressing
  every specialist result into an executive summary. The knowledge guide alone remains short.
- Stage requires all finding IDs to be documented, truly duplicated or explicitly omitted under
  restricted rules, with exact document excerpts and source evidence.
- Domain and database findings have dedicated destinations; every planned area has a dossier.
- Approval requires reviewer source reads across all included files and checks of every document.
- Repair preserves the completed snapshot, current knowledge and a backup of the prior state,
  then requires new exploration and review. It is intentionally more costly than summarizing
  the prior output; inadequate findings must not remain the only source of knowledge.

## Acceptance and limits

Automated tests reject unplanned submissions, lost findings, guide-only findings, nonexistent
excerpts, mismatched areas and single-file review approval. They verify repair preserves source
identity and published notes while invalidating old evidence. Existing workflow tests remain.
On 2026-09-21 all 50 runtime tests passed, and all six skill manifests passed validation.
Manual semantic acceptance requires tracing complete business and technical flows through a
representative repository; the user's private project is unavailable here. Schemas cannot
prove comprehension, adequate decomposition or honest evidence. No line-count or word-count
threshold can substitute for substantive review, and these changes do not claim such a guarantee.
