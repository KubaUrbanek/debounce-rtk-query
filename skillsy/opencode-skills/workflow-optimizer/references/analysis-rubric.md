# Session analysis rubric

Use this rubric to keep retrospective findings reproducible and proportional to the evidence.

## Evidence levels

| Level | Meaning | Allowed language |
| --- | --- | --- |
| Strong | Same friction appears in at least three sessions, or directly causes a failed result | `recurring`, `high confidence` |
| Moderate | Pattern appears in two sessions with a similar cause | `likely recurring`, `medium confidence` |
| Weak | One occurrence or an ambiguous proxy | `isolated observation`, `hypothesis` |

Counts must refer to the reviewed sample, not all OpenCode usage.

## Signals and likely destinations

| Signal | First place to consider changing |
| --- | --- |
| Same preference corrected across unrelated tasks | Global rule or global skill |
| Repository-specific convention corrected repeatedly | Project `AGENTS.md` |
| Repeatable specialist procedure | Skill |
| Stable role with distinct tools or permissions | Custom agent |
| Repeated deterministic shell/data transformation | Script or command |
| One unclear initial request | Prompt template or a clarifying question |
| Repeated permission interruption | Narrow OpenCode permission rule |
| Missing validation after implementation | Project workflow or relevant skill |

Do not recommend a global rule for a repository-local pattern. Do not recommend a new skill when one sentence in an existing rule is sufficient.

## Friction categories

### Rework

Look for user corrections, reverted edits, repeated explanations, abandoned approaches, and requests to undo complexity. Verify whether the agent had enough information at the time before blaming prompt quality.

### Exploration and context

Look for editing before reading central files, repeated reads caused by lost context, large irrelevant searches, and failure to reuse prior findings. Distinguish necessary investigation from churn.

### Implementation quality

Look for scope expansion, invented abstractions, missed repository conventions, fragile error handling, and failure to preserve unrelated changes.

### Verification

Look for omitted tests, tests added only after prompting, ignored failures, or expensive validation that could have been scoped better.

### Tooling and permissions

Look for repeated denials, overly broad permission requests, incorrect commands, or tasks better handled by a deterministic helper.

### Communication

Look for status gaps, buried outcomes, repeated clarification that available evidence could resolve, or answers whose certainty exceeds the evidence.

## Recommendation test

Before including a recommendation, answer:

1. Which session evidence supports it?
2. Would the proposed change have prevented or shortened the observed friction?
3. Is this the narrowest appropriate location and scope?
4. What downside or overfitting risk does the change introduce?
5. How can improvement be observed in the next 5-10 sessions?

Reject recommendations that cannot pass the first three questions.
