---
name: workflow-optimizer
description: Analyze multiple OpenCode sessions to find recurring workflow friction, correction loops, wasted context, weak verification, and missed automation opportunities, then recommend evidence-backed changes to prompts, AGENTS.md, skills, agents, or OpenCode configuration. Use for retrospectives or requests to work better with OpenCode; not for locating one fact in an old session or summarizing a single session.
metadata:
  version: "1.0.0"
  data-policy: "local-sanitized-exports"
---

# Workflow Optimizer

Find repeatable improvements in how the user and OpenCode work together. Base conclusions on session evidence, not generic agent advice.

## Scope

- Default to the 30 most recent sessions. Use 10 for a quick review and up to 100 only when the user asks for a deep review.
- Prefer sessions from the current project. Include other projects only when the user asks for a global workflow review.
- Treat a behavior as a recurring pattern only when it appears in at least two sessions. A useful issue from one session may be reported as an isolated observation.
- Analyze the interaction and workflow. Do not grade the user's writing style or infer personal traits.

## Collect evidence

When live OpenCode history is available, create a temporary directory and run:

```bash
python3 <skill-directory>/scripts/collect_sessions.py \
  --max-count 30 \
  --project "$PWD" \
  --output <temporary-directory>/sessions.json
```

The collector uses `opencode session list --format json` and sanitized `opencode export` output. If the command is unavailable or a sanitized export fails, report the exact limitation. Never silently retry without `--sanitize`.

If the user provides exported session JSON instead, analyze that input directly. Do not inspect `auth.json`, environment variables, credentials, or unrelated application data. Keep collected transcripts in a temporary location unless the user explicitly asks to save them.

Read [references/analysis-rubric.md](references/analysis-rubric.md) before analyzing the corpus.

## Analyze

Build a compact evidence ledger before recommending changes. Look for:

- repeated user corrections, reversals, or requests to simplify;
- implementation beginning before enough repository exploration;
- unnecessary abstraction, large diffs, or scope expansion;
- missing, late, or repeatedly requested tests and verification;
- repeated permission prompts or tool failures;
- rereading the same context, long detours, and avoidable token use;
- tasks that should become a rule, skill, custom agent, command, or script;
- poor model or agent selection only when the session data supports it.

Separate observation, inference, and recommendation. Quote only short evidence fragments and include session IDs or titles so the user can verify each pattern. Redact any secret-like value that remains in supplied data.

Prioritize with this order: user-visible rework, correctness risk, repeated time cost, then convenience. Prefer a small change that prevents a demonstrated problem over a broad new rule.

## Report

Return:

1. A one-paragraph assessment of the dominant pattern.
2. Up to five prioritized improvements, each with evidence, expected benefit, confidence, and the smallest concrete change.
3. A short `Keep doing` section for practices that consistently worked.
4. Exact candidate diffs for `AGENTS.md`, agent configuration, commands, or skills only when the evidence justifies them.
5. One measurable experiment for the next 5-10 sessions.

Do not modify configuration, rules, skills, or agents during an analysis-only request. When the user explicitly asks to apply recommendations, inspect the target files, preserve unrelated content, make only the approved edits, and show the resulting diff.

Avoid false precision. Use counts when reliable; otherwise say `several sessions` and explain the sampling limitation.
