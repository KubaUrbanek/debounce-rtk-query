# Second Brain v2 — business scenarios

Date: 2026-09-18. Status: planned semantic acceptance; automated checks listed separately.
Companion: [implementation plan](second-brain-plan.md).
Fourth-skill coverage: [bootstrap scenarios](bootstrap-tests.md) and [bootstrap plan](bootstrap-plan.md).

| ID | Priority | Given | When | Then | Coverage |
|---|---|---|---|---|---|
| SC1 | High | Monday commit merged Wednesday into develop-api | Wednesday system report | Included in Wednesday outcomes, not selected by commit date | BR2, AC2, P2 |
| SC2 | High | MRs on develop and main around Warsaw midnight | Daily collection | Only develop* merges within local day included | BR2, AC2, P2 |
| SC3 | High | One inaccessible repository | Collection | Partial coverage explicitly stated; available facts still useful | BR7, AC2, P2 |
| SC4 | High | Own unpushed experiment on two local branches | Personal daily | Included once, alternative approach retained | BR3, AC3, P3 |
| SC5 | High | Rebase changed committer date but not author date | Personal daily | Author day determines selection | BR3, AC3, P3 |
| SC6 | High | Late meeting marked include_in_daily=true | Today daily | Entire conversation summarized as dated earlier-event update | BR3, AC3, P3 |
| SC7 | High | Knowledge processed a source before daily | Publication | Source stays until daily consumes identical hash | BR6, AC5, P5 |
| SC8 | High | Source edited after daily consumption | Knowledge publication | Old daily marker insufficient; source remains pending | BR6, AC5, P5 |
| SC9 | High | Invalid/missing date, useful content | Knowledge extraction | Knowledge allowed; no daily or archival | BR6, AC5, P5 |
| SC10 | High | Source contradicts existing rule | Distillation | Ask before writing; defer into sourced conflict if requested | BR4–5, AC4, P4 |
| SC11 | High | Explicit architecture choice without repo scope | Distillation | Ask scope; proposed ADR only, unknown if deferred | BR5, AC4, P4 |
| SC12 | Medium | Administrative note without durable facts | Distillation | No empty topic; knowledge processed | BR6, AC5, P5 |
| SC13 | High | Archived source already reflected in today's daily | Rerun daily | Preserve previous facts without opening archive | BR3, BR6, AC4–5, P4–5 |
| SC14 | High | System report archived | Requested rerun | Rename known report to inbox, update same identity and links | BR2, BR6, AC5, P5 |
| SC15 | Medium | No activity and successful collection | Run reporting skill | Message only, no empty file | BR7, AC4, P4 |
| SC16 | High | New proposed ADR supersedes accepted design | Publication | Old ADR remains accepted until user accepts successor | BR5, AC4, P4 |
| SC17 | High | Source changed between read and publish | Publish | Reject stale hash, no completion marker | BR6, AC5, P5 |
| SC18 | Medium | Bad YAML indentation/duplicate keys/aliases | Check config | Clear rejection, no file changes | BR1, AC1, P1 |
| SC19 | Medium | Overlapping MRs including a revert | System synthesis | Cumulative result and significant reversal, not per-commit narrative | BR2, AC4, P4 |
| SC20 | High | Publication has broken source links | Publish | Reject before marking inputs processed | BR6, AC5, P5 |
| SC21 | High | Inbox explicitly describes SQL or NoSQL changes | Distillation | Update separate project database notes and link domain/application concepts | BR4, AC4, P4 |
| SC22 | High | Source contradicts a fact initialized from code | Later inbox distillation | Ask about the conflict; do not reuse bootstrap's automatic code-wins exception | BR4–5, AC4, P4 |

Automated tests cover collection filters/pagination, DST, actual local Git, stage ordering,
changed hashes, invalid/late dates, archive non-reading, graph links and config validation.
Human-in-the-loop behavior, attribution, meaningful grouping and factual synthesis remain
planned acceptance checks; they are not asserted as passed by unit tests.
