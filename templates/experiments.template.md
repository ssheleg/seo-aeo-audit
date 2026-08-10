# Experiment record — {{SITE}}

One row per test. Never delete a row: a reverted test is evidence too, and the
next audit needs to know it was tried.

| id | hypothesis | cohort (template, n) | control (n) | single variable | start | end | metric | control delta | test delta | significance | verdict | rolled out? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | {{...}} | {{...}} | {{...}} | {{...}} | {{YYYY-MM-DD}} | {{YYYY-MM-DD}} | {{...}} | {{...}} | {{...}} | {{...}} | {{win / no effect / loss / invalidated}} | {{yes / no + why}} |

**Verdict values:** `win → rolled out` · `win → not rolled out (why)` ·
`no effect` · `loss → reverted` ·
`invalidated (update / seasonality / instrumentation)`.

**Invalidation check before reading any row:** did the run overlap a core or spam
update? Date-align against `algorithm-updates.md` — a test through a rollout is
invalidated, not inconclusive.
