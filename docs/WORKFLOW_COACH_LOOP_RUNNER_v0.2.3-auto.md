# Workflow Coach Loop Runner - v0.2.3-auto

Status: Codex 041 docs/tests/scripts semi-automatic coach-loop runner workflow tooling.

## 1. Purpose

Codex 041 adds the first semi-automatic local coach-loop runner. It orchestrates
the existing local workflow bricks for context collection, GPT stage
preparation/execution, transition_gate validation, autonomy decisions, bounded
auto-reflection, manual Codex handoff, Codex return resume, PR verification and
guarded merge delegation.

The runner writes local state and summaries under `.dicoimpro/runs/<run_id>/`.
It stops with `stop_human` whenever validation, policy, budget, gate, PR or
risk evidence is unresolved.

## 2. Relation to Codex 035-040

Codex 035 defined the coach-loop output architecture. Codex 036 added local
context and workflow state tooling. Codex 037 added the GPT stage runner.
Codex 038 added manual Codex handoff and return archiving. Codex 039 encoded
the autonomy policy and pre-merge verify gate. Codex 040 added the guarded PR
verification and optional merge runner.

Codex 041 orchestrates those scripts rather than duplicating their logic.

## 3. What Codex 041 Implements

- `scripts/coach_loop.py`.
- Local run initialization/resume under `.dicoimpro/runs/<run_id>/`.
- `loop_state.json`.
- `loop_summary.md`.
- `start`, `resume-codex`, `verify-pr`, `status`, and `summarize` commands.
- Prepare-only start flow by default.
- Explicit GPT flow only through `scripts/coach_step.py` with `--execute-api`.
- Transition gate extraction and autonomy policy evaluation.
- Bounded auto-reflection when policy allows it.
- Manual Codex handoff creation through `scripts/coach_codex_handoff.py`.
- Codex return archive/resume through `scripts/coach_codex_handoff.py`.
- PR verification and guarded merge delegation through `scripts/coach_pr_verify.py`.

## 4. What Codex 041 Does Not Implement

Codex 041 does not execute Codex. It does not call Codex SDK or Codex CLI. It
does not call OpenAI directly. It does not implement a separate merge pathway,
does not build its own merge command, and does not implement an unbounded
autonomous loop.

It does not authorize RUN, journal read/write, JournalPatch application, real
data processing, XLSX/CSV export, old PDF usage, publication, prompt
activation/rendering/execution inside `src/`, production code changes, or src
runtime behavior change.

## 5. Runner Commands

```text
python scripts/coach_loop.py start --run-id codex_041_example --stage pre_cadrage
python scripts/coach_loop.py start --run-id codex_041_example --stage pre_cadrage --execute-api
python scripts/coach_loop.py start --run-id codex_041_example --stage pre_cadrage --execute-api --user-instruction "..."
python scripts/coach_loop.py resume-codex --run-id codex_041_example --return-path codex_return.md
python scripts/coach_loop.py resume-codex --run-id codex_041_example --return-path codex_return.md --verify-pr --merge-mode manual
python scripts/coach_loop.py verify-pr --run-id codex_041_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_041_example/05_codex_return.md --merge-mode manual
python scripts/coach_loop.py verify-pr --run-id codex_041_example --pr-url https://github.com/Nyoha12/dicoimpro/pull/99 --codex-return-path .dicoimpro/runs/codex_041_example/05_codex_return.md --merge-mode auto_after_verify --execute-merge
python scripts/coach_loop.py status --run-id codex_041_example
python scripts/coach_loop.py summarize --run-id codex_041_example
```

## 6. Loop State Model

The state file is `.dicoimpro/runs/<run_id>/loop_state.json` and uses
`schema_version: coach_loop_state.v1`.

It records run id, stage, status, paths to context/prompt/stage note/handoff,
transition_gate, autonomy decision, reflection count, GPT/external call counts,
Codex return path, PR URL, pre-merge report path, merge decision, post-merge
report path, blockers, warnings and next required action.

The summary file is `.dicoimpro/runs/<run_id>/loop_summary.md`.

## 7. Start Flow

`start` collects local context and prepares a GPT coach prompt. Without
`--execute-api`, it stops at `prompt_prepared` and no API call occurs.

With `--execute-api`, GPT calls require --execute-api and use coach_step.py
boundary. The runner validates the returned stage note, extracts
`transition_gate`, evaluates policy through `scripts/coach_autonomy.py`, and
then either stops human, performs bounded reflection, or builds a Codex handoff
when the note is Codex-ready.

## 8. Auto-Reflection Policy

Auto-reflection is bounded by `max_reflections_per_stage` from
`.dicoimpro/WORKFLOW_AUTONOMY_POLICY.example.json`, defaulting to 3.

Auto-reflection is allowed only when the policy allows it, no human decision is
required, the blocking question is not substantive, budget remains available,
and `--execute-api` authorized GPT execution. Unknown risk stops human.

## 9. Manual Codex Handoff Boundary

Codex remains manual handoff. The runner may build a handoff packet through
`scripts/coach_codex_handoff.py`, but it does not execute Codex, does not call
Codex SDK, and does not call Codex CLI.

## 10. Codex Return Resume Flow

`resume-codex` archives a manually supplied Codex return, validates it, extracts
a PR URL, updates `loop_state.json`, and stops for PR verification or review.
If `--verify-pr` is supplied, it continues into the PR verification flow.

Invalid Codex returns and missing PR URLs stop human.

## 11. PR Verification and Merge Delegation

`verify-pr` builds a pre-merge report through `scripts/coach_pr_verify.py` and
decides through the autonomy policy. Merge is never default.

Merge requires --execute-merge and auto_after_verify, and merge is only
delegated to the coach_pr_verify.py boundary. The runner does not implement a
separate merge pathway.

Post-merge validation runs only after an executed merge. Post-merge failure
stops human and does not trigger destructive repair.

## 12. Stop-Human Conditions

The runner stops human when the objective is absent or ambiguous, a gate
requires human intervention, `can_advance` is false and reflection is not
allowed, policy blocks continuation, note validation fails, handoff validation
fails, Codex return validation fails, PR URL is missing, pre-merge verification
is incomplete or red, merge mode is manual, `--execute-merge` is absent for a
merge attempt, post-merge validation fails, budget is exceeded, or risk is
unknown.

## 13. Budget Handling

The runner tracks `gpt_call_count` and `external_call_count` in
`loop_state.json`. It evaluates budget with `scripts/coach_autonomy.py` before
GPT calls. It never calls GPT when `--execute-api` is absent.

## 14. Safety Boundaries

Codex 041 is workflow tooling only. It does not call OpenAI directly, does not
execute Codex, does not call Codex SDK/CLI, does not implement automatic Codex
execution, does not implement an unbounded autonomous loop, and does not
authorize RUN, journal, JournalPatch, real data, publication, XLSX/CSV export,
old PDF usage or src runtime behavior change.
No automatic Codex execution.

## 15. Future Implementation Phases

Future phases may add richer state transitions, stronger contradiction
detection, signed run summaries, and human-reviewed scheduling. Those phases
must keep GPT calls behind `--execute-api`, Codex execution as manual handoff,
and merge execution behind `coach_pr_verify.py`.

## 16. Verdict

Codex 041 is the first semi-automatic local coach-loop runner. It orchestrates
existing scripts, stops on unknown risk, keeps Codex manual, keeps GPT calls
explicit, keeps merge delegated to the PR verify boundary, and changes no
production runtime behavior.
