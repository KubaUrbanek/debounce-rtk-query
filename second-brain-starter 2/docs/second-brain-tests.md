# Second Brain Starter — acceptance scenarios

Date: 2026-09-29. Status: Planned manual acceptance scenarios, not a claim of executed production tests.

See [implementation record](second-brain-plan.md). Use disposable repositories and temporary knowledge directories.

| ID | Priority | Given | When | Then | Coverage |
| --- | --- | --- | --- | --- | --- |
| SC1 | High | A repository with HTTP, message and scheduled entry points and no knowledge | User invokes map | Map and coverage identify observed entry types, cite symbols and exclude generated artifacts; a map checkpoint matches provenance in both documents; no flow checkpoint is created | BR1, AC1–2, P1–2 |
| SC2 | High | Map lists approval and refund; state contains another repository | User selects approval | Only approval is deeply documented; original state entries remain and approval gets the real pinned SHA | BR2–3, AC3, P3 |
| SC3 | High | Completed approval at commit A | Analysis at B stops before verification | Prior completed checkpoint remains A; new work is clearly a draft | BR4, AC3, P3 |
| SC4 | High | Completed approval plus an unverified refund draft | User invokes organize | Shared claims cite completed approval; refund assertions remain unverified; state is byte-for-byte unchanged | BR5, BR7, AC4, P4 |
| SC5 | High | User checkout has uncommitted changes and a different branch | User invokes analyze for configured remote develop | Source reads use a pinned develop SHA; checkout branch and local modifications are untouched | BR6, AC1, AC3, P1, P3 |
| SC6 | High | Prior flow SHA is not in the fetched configured branch history | User reanalyzes that flow | Skill reports the problem and preserves the previous completed flow and checkpoint | BR6, AC3, P3 |
| SC7 | High | Invalid JSON state | User invokes a writing skill | Skill reports the error instead of replacing state with an empty object | BR3–4, AC1, P1 |
| SC8 | Medium | Two repositories use the same word for different concepts | User organizes completed notes | Concepts remain distinct unless evidence supports equivalence; provenance retains both snapshots | BR5, BR7, AC4, P4 |
| SC9 | Medium | README and three extracted skill folders | User configures a first repository and follows examples | All three can be invoked independently, including by explicit SKILL.md path; no next skill starts itself | AC5, P5 |
| SC10 | High | Document has SHA B but completed state has A after a failed save | User invokes organize | Mismatch is flagged and new prose is not promoted as newly verified knowledge | BR4–5, AC3–4, P3–4 |
| SC11 | Medium | Fetch fails | User invokes map or analyze | No silent stale-ref fallback or false current-snapshot claim occurs | BR6, AC1, P1 |
| SC12 | Medium | Tests and implementation disagree | User analyzes the process | Both evidence sources and the contradiction are documented; business intent is not invented | BR7, AC3, P3 |

| SC13 | High | State contains completed flow approval at A but no map object | User successfully invokes map at B | Map checkpoint is added at B; approval remains at A and all other metadata survives | BR1, BR3, AC1–2, P1–2 |
| SC14 | High | A completed map checkpoint at A | Mapping at B is interrupted | Map checkpoint stays A and incomplete output remains a draft | BR1, BR4, AC2, P2 |
| SC15 | High | Map is at A and approval is at A | Approval analysis completes at B | Approval moves to B; map remains A and coverage discovery metadata is not rewritten to B | BR3, AC3, P3 |
| SC16 | Medium | Legacy state contains flows with no map checkpoint | User organizes knowledge | Missing map provenance is flagged, no checkpoint is invented, and valid flow evidence can still be organized | BR3, BR5, AC4, P4 |

## Focused package checks

Skill frontmatter and naming are validated separately during package creation. Small synthetic forward checks exercise selected behaviors and do not establish that every scenario above passed or that production code has been analyzed.

## OpenCode-specific planned checks

- SC17: Given OpenCode V1 and the V1 template, start in the knowledge workspace; all three named skills can load and write documentation there.
- SC18: Given two mapped projects, analyze one process in each; all project-specific documents remain under their respective repositories/<repo-id>/ directories and state.document uses matching paths.
- SC19: Given existing orders-api state, map payments-api; add only its map/state and preserve orders-api content.
- SC20: Given a source-repository session with global skills and absolute-only edit permission, write knowledge to the shared root without creating local documentation.

These environment-level checks are planned, not executed in the user's OpenCode installation. They cover AC1, AC2 and AC5.
