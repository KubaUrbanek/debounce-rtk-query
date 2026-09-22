# Analysis depth upgrade

See [analysis contract](../runtime/analysis-depth.md) and [setup](../SETUP.md).

## Problem and outcome

The prior bootstrap could account for all source ranges yet produce a few generic sentences.
Read coverage, document completeness and semantic correctness are different properties.
This revision retains coverage and adds functional planning, finding-to-document accounting,
per-area synthesis and broader independent review. Other skills gain evidence-retention and
source-specific depth rules; personal daily remains concise and thought refinement stays faithful.

## Bootstrap implementation

- Discover entry points before submitting analysis: queue complete triggered flows and explicit
  residual work; account for every included file using area ownership.
- Researchers follow full use cases and read shared dependencies across task boundaries.
- Queue size is independent of the default four concurrent workers. Completed workers finish;
  fresh agent contexts take the next queued tasks. All tasks must complete before staging.
- Preserve detailed working evidence on disk; the coordinator integrates instead of compressing
  every specialist result into an executive summary. The knowledge guide alone remains short.
- Stage requires all finding IDs to be documented, truly duplicated or explicitly omitted under
  restricted rules, with exact document excerpts and source evidence.
- Domain and database findings have dedicated destinations; every planned area has a dossier.
- Approval requires reviewer source reads across all included files and checks of every document.
- Fresh bootstrap follows user-managed cleanup; no repair mode or automated deletion exists.
  Interrupted work resumes its pinned snapshot; completed retained state blocks reinitialization.

## Acceptance and limits

Automated tests reject unplanned submissions, lost findings, guide-only findings, nonexistent
excerpts, mismatched areas and single-file review approval. Task-queue acceptance also requires
more tasks than slots, shared dependency reads, fresh worker identities and complete flow mapping.
Existing workflow tests remain; see the release verification for actual test results.
The current suite passes 56 tests, including seven queued tasks with four worker slots,
failed-worker replacement, shared findings, explicit corrections and flow-evidence retention.
Domain audience checks additionally reject routing a technical finding into domain notes and
verify neutral labels for generated technical backlinks. Domain prose targets nontechnical
users; code-level tracing remains in internal evidence and technical documentation. These
mechanical checks cannot decide whether a sentence is understandable: substantive audience
review remains mandatory. Installing the package does not rewrite existing mixed documents.
Manual semantic acceptance requires tracing complete business and technical flows through a
representative repository; the user's private project is unavailable here. Schemas cannot
prove comprehension, adequate decomposition or honest evidence. No line-count or word-count
threshold can substitute for substantive review, and these changes do not claim such a guarantee.
