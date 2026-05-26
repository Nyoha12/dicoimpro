# Workflow Coach PR Verify Merge Runner - v0.2.3-auto

Status: Codex 040 docs/tests/scripts workflow tooling.

## 1. Purpose

Codex 040 adds the first guarded PR verification and optional auto-merge runner
for the future coach-loop program. The runner builds a local
`pre_merge_report` from PR evidence, validates that report through the autonomy
policy, records the report under `.dicoimpro/runs/<run_id>/`, and can execute a
real merge only when every explicit merge condition is satisfied.

Merge is never default. The default path is verification only.

## 2. Relation to Codex 035-039

Codex 035 defined the local GPT-5.5 Thinking / Codex coach-loop architecture.
Codex 036 added local context and transition-gate state tooling. Codex 037 added
the explicit GPT stage runner. Codex 038 added the manual Codex handoff bridge
and Codex return archive. Codex 039 encoded the autonomy policy and pre-merge
verify gate as a decision model only.

Codex 040 connects those pieces to real PR evidence through a local runner.
Unlike Codex 039, it may perform a real merge, but only inside
`scripts/coach_pr_verify.py`, only with `--execute-merge`, and only after a
fresh successful verify gate.

## 3. What Codex 040 Implements

- PR URL parsing for GitHub pull request URLs.
- Local `gh` CLI collection of PR metadata, changed files, status checks,
  review state, and diff text.
- Secret-like diff scanning without storing secret values.
- A `pre_merge_report` JSON shape aligned with `scripts/coach_autonomy.py`.
- Validation of archived Codex returns through `scripts/coach_codex_handoff.py`.
- Autonomy decision integration through `scripts/coach_autonomy.py`.
- Local report recording under `.dicoimpro/runs/<run_id>/`.
- An explicit merge execution path guarded by `--execute-merge`,
  `merge_mode: auto_after_verify`, a green autonomy decision, and
  `--match-head-commit`.
- Post-merge validation that syncs main and runs tests only after an executed
  merge.

## 4. What Codex 040 Does Not Implement

Codex 040 does not call OpenAI/GPT/Codex SDK/Codex CLI. It does not execute
Codex, does not implement autonomous full loop behavior, does not activate,
render, execute, or consume prompts inside `src/`, and does not process RUN,
journal, JournalPatch, real data, XLSX/CSV export, old PDF input, or
publication flows.

The external Codex implementing this mission must not merge PR #40.

## 5. PR Evidence Model

The runner collects PR evidence through local `gh` CLI commands:

- PR URL, number, open state, draft state, mergeability, base branch, head
  branch, and head SHA;
- review decision and blocking review signals where available;
- status check rollup where available;
- changed files;
- PR diff text for secret-like pattern scanning.

There is no direct GitHub API library, no `requests`/`httpx` use, and no
network path except the local `gh` CLI inside this runner.

## 6. Pre-Merge Report Model

The saved report contains:

- `merge_mode`;
- `pr`;
- `scope`;
- `checks`;
- `codex_return`;
- `reviews`;
- `contradictions_detected`;
- local evidence metadata.

The report is written to
`.dicoimpro/runs/<run_id>/08_pre_merge_report.json` unless an existing file
requires explicit `--overwrite`.

## 7. Autonomy Decision Integration

The runner imports the local autonomy module and calls its pre-merge decision
logic. A merge can proceed only when the decision is allowed and the autonomy
level is `auto_merge_after_verify`.

Manual merge mode blocks auto-merge. A blocked verify gate blocks auto-merge.
Unknown or contradictory evidence blocks auto-merge and requires a human stop.

## 8. Explicit Auto-Merge Execution

Merge requires all of the following:

- --execute-merge required;
- `--execute-merge` required;
- `merge_mode auto_after_verify` required;
- fresh successful verify gate required;
- PR is open, not draft, mergeable, based on `main`, and has an authorized head
  branch;
- head SHA is present and stable;
- match-head-commit required through `--match-head-commit <head_sha>`;
- changed files are within authorized scope;
- no forbidden path or secret-like diff content is detected;
- archived Codex return is present and valid;
- guardrail guarantee is present;
- tests, diff-check, and CI are green or CI is explicitly not required;
- no blocking review, REQUEST_CHANGES review, contradiction, or unknown risk.

The merge command is `gh pr merge ... --merge --delete-branch
--match-head-commit <head_sha>`. The runner never pushes to main and never
creates tags or releases.

## 9. Post-Merge Validation

Post-merge tests must run after an executed merge. The runner then performs:

- `git checkout main`;
- `git pull origin main`;
- `python -m pytest`.

It records `.dicoimpro/runs/<run_id>/09_post_merge_report.json`. Post-merge
failure stops human and does not auto-repair. There is no destructive
auto-repair, no auto-revert, and no follow-up merge action.

## 10. Human Stop Conditions

The runner stops for human intervention when the verify gate is incomplete or
red, including draft PR, non-mergeable PR, wrong base, unstable head SHA,
forbidden paths, secrets, failed tests, failed diff-check, failed CI,
missing/invalid Codex return, missing guardrail guarantee, blocking reviews,
REQUEST_CHANGES, contradictions, or unknown risk.

## 11. CLI Commands

```text
python scripts/coach_pr_verify.py verify --run-id codex_040_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_040_example/05_codex_return.md --merge-mode manual
python scripts/coach_pr_verify.py verify --run-id codex_040_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_040_example/05_codex_return.md --merge-mode auto_after_verify
python scripts/coach_pr_verify.py verify --run-id codex_040_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_040_example/05_codex_return.md --merge-mode auto_after_verify --execute-merge
python scripts/coach_pr_verify.py decide-report --report-json .dicoimpro/runs/codex_040_example/08_pre_merge_report.json
python scripts/coach_pr_verify.py summarize-report --report-json .dicoimpro/runs/codex_040_example/08_pre_merge_report.json
python scripts/coach_pr_verify.py validate-boundary
```

`decide-report`, `summarize-report`, and `validate-boundary` do not call `gh`,
`git`, or merge anything.

## 12. Safety Boundaries

This script may use local `gh`, `git`, and `pytest` only inside explicit
boundaries. `gh` evidence collection is limited to PR verification. `git` and
`pytest` are limited to post-merge validation after an executed merge. Real
merge is limited to `--execute-merge` plus `merge_mode auto_after_verify` plus
a complete green verify gate.

This does not authorize OpenAI/GPT calls, Codex SDK/CLI, automatic Codex
execution, autonomous full loop, RUN, journal read/write, JournalPatch, real
data processing, prompt activation/rendering/execution inside `src/`, XLSX/CSV
export, old PDF usage, publication, production code changes, or runtime
behavior changes.
No src runtime behavior change.

## 13. Future Implementation Phases

Future phases may add richer CI normalization, explicit review timeline
analysis, signed report snapshots, and a human-reviewed scheduler around the
runner. Those phases must preserve the verify gate and explicit merge boundary.

## 14. Verdict

Codex 040 is the first guarded real merge-capable script for the coach-loop
program. It is safe only as an explicit verify runner: merge is never default,
`--execute-merge` is mandatory, `merge_mode auto_after_verify` is mandatory, the
fresh verify gate must pass, match-head-commit is required, and post-merge tests
must run. The external Codex implementing this mission must not merge PR #40.
