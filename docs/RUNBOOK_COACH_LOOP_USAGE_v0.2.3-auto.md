# Coach Loop Usage Runbook - v0.2.3-auto

Status: Codex 042 hardening and operational runbook for controlled local use.

## 1. Purpose

This runbook gives the practical command sequence for the semi-automatic local
coach-loop runner. The default is local and non-destructive.
Generated .dicoimpro/runs/* artifacts are local and ignored.
No new autonomy is introduced.
No src runtime behavior change is authorized.

## 2. Before Starting

- Confirm the branch and working tree manually.
- Run `python scripts/coach_loop.py doctor`.
- Generated `.dicoimpro/runs/*` artifacts are local and ignored.
- Keep the run objective explicit before using API or merge flags.

## 3. Safe Smoke Without API

```text
python scripts/coach_loop.py start --run-id codex_042_example --stage pre_cadrage
python scripts/coach_loop.py validate-run --run-id codex_042_example
python scripts/coach_loop.py explain-next --run-id codex_042_example
```

This prepares context and a model prompt only. No API call occurs.

## 4. Controlled API Run

API requires --execute-api. API requires `--execute-api` and uses the
`scripts/coach_step.py` boundary.

```text
python scripts/coach_loop.py start --run-id codex_042_example --stage pre_cadrage --execute-api
```

Do not use this unless external GPT use is explicitly authorized for the run.

## 5. Reading Status

```text
python scripts/coach_loop.py status --run-id codex_042_example
```

This reads local state only.

## 6. Explaining Next Action

```text
python scripts/coach_loop.py explain-next --run-id codex_042_example
```

This prints the next local action. It does not call GPT, Codex, gh, git,
pytest, network, or merge.

## 7. Manual Codex Handoff

When status is `handoff_ready`, Codex remains manual handoff. Open the handoff
packet under `.dicoimpro/runs/<run_id>/`, paste it into Codex manually, and keep
the Codex return for archive.

## 8. Resuming From Codex Return

```text
python scripts/coach_loop.py resume-codex --run-id codex_042_example --return-path codex_return.md
```

The runner archives and validates the return, extracts the PR URL, and stops
for PR verification or review.

## 9. PR Verification Without Merge

```text
python scripts/coach_loop.py verify-pr --run-id codex_042_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_042_example/05_codex_return.md --merge-mode manual
```

Manual merge mode never merges.

## 10. Optional Guarded Merge

Merge is never default. Merge requires --execute-merge and
`merge_mode auto_after_verify` after a successful verification gate.

```text
python scripts/coach_loop.py verify-pr --run-id codex_042_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_042_example/05_codex_return.md --merge-mode auto_after_verify --execute-merge
```

The runner delegates merge to `scripts/coach_pr_verify.py`; it does not build a
separate merge pathway.

## 11. Stop-Human Policy

Unknown risk means stop_human. Unknown risk means `stop_human`. Stop for human review when validation fails,
budget is exceeded, a transition gate requires intervention, Codex return data
is invalid, PR verification is red or incomplete, or post-merge validation
fails.

## 12. Diagnostics

```text
python scripts/coach_loop.py doctor
python scripts/coach_loop.py validate-run --run-id codex_042_example
python scripts/coach_loop.py explain-next --run-id codex_042_example
```

These diagnostics are local-only and non-destructive. They do not call GPT,
OpenAI, Codex, gh, git, pytest, network, or merge.

## 13. What Not To Do

- Do not use diagnostics to override `stop_human`.
- Do not execute Codex SDK or Codex CLI.
- Do not add automatic Codex execution or an unbounded autonomous loop.
- Do not merge without `--execute-merge` and `auto_after_verify`.
- Do not process RUN, journal, JournalPatch, real data, XLSX/CSV, old PDF, or
  publication flows.
- Do not change `src/` runtime behavior.

## 14. End-Of-Run Checklist

- `loop_state.json` is valid.
- `loop_summary.md` is current.
- Blockers and warnings are reviewed.
- Codex return and PR evidence are archived when applicable.
- Merge, if any, was explicitly authorized and verified.
- No RUN/journal/JournalPatch/real data or src runtime behavior change occurred.
