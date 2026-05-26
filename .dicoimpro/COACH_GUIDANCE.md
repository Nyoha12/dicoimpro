# Coach Guidance - GPT-5.5 Thinking / Codex Loop

Status: scaffold documentation only. This file defines output guidance for a
future local coach loop. It does not activate prompts, models, Codex SDK calls,
or dicoimpro runtime behavior.

## Roles

### GPT-5.5 Thinking

GPT-5.5 Thinking is the local coach and strategist. It frames the next bounded
work item, evaluates maturity for the next stage, writes shareable stage notes,
and produces the next prompt or targeted reflection prompt. It is not the
executor and must not run repository commands, apply patches, create PRs, merge,
or process project data.

### Codex

Codex is the executor. Codex receives a bounded task prompt, edits only the
authorized files, runs the authorized commands, and returns a concise execution
summary with files changed, commands run, tests, and guardrail status. Codex does
not decide the whole workflow alone and does not override the coach-stage
transition gate.

### Python orchestration script

A future Python script is only an orchestrator and transport layer. It may later
move stage notes, context packets, and prompts between local files, GPT-5.5
Thinking, Codex, git, tests, and PR review after explicit authorization. It must
read the stage transition_gate and follow it. The script must not decide maturity
arbitrarily, must not invent a next prompt, and must not execute blocked stages.

### AGENTS.md / Codex instructions

If `AGENTS.md` or Codex-side instructions are present, they define Codex-side
execution rules: repository constraints, coding standards, command boundaries,
review expectations, and safety limits. They do not replace the coach-stage
transition gate and do not authorize dicoimpro runtime activation.

## Dicoimpro guardrails

These guardrails are false by default and remain false until a later explicit
authorization changes them:

- no prompt activation unless explicitly authorized later;
- no prompt rendering, execution, or consumption unless explicitly authorized
  later;
- no OpenAI runtime activation inside dicoimpro application code;
- no RUN without explicit later authorization;
- no journal read/write;
- no JournalPatch application;
- no real data processing unless explicitly authorized later;
- no publication;
- no old PDF as an active or decisive source.

This scaffold also authorizes no automatic PR creation, no automatic merge, no
candidate selection, no XLSX/CSV export, and no production behavior change.

## Required stage sequence

The required stage sequence is:

1. context
2. pre_cadrage
3. cadrage
4. decision
5. codex_prompt
6. codex_return
7. post_codex_review
8. pr_review
9. post_merge_review

## Optional reflection stages

Reflection is optional, targeted, and unlimited by user request until the
specific blocking question is resolved. Reflection stages are not systematic.
They are triggered only if the next stage is not ready or the user requests
deeper reasoning.

Optional reflection stages:

- reflection_before_cadrage
- reflection_before_decision
- reflection_before_codex_prompt
- reflection_before_post_codex_review
- reflection_before_pr_review
- reflection_before_post_merge_review

## Transition rules

- Each GPT stage output includes the current stage note, a transition_gate, and
  either a next_prompt or a reflection_prompt.
- The maturity assessment and next prompt generation happen inside the current
  GPT stage output.
- There is no separate mandatory GPT call only to decide maturity.
- There is no separate mandatory GPT call only to generate the next prompt.
- A stage must never advance if `transition_gate.can_advance` is false.
- A stage must never advance if `transition_gate.next_prompt_ready` is false.
- If `transition_gate.can_advance` is true and
  `transition_gate.next_prompt_ready` is true, the next_prompt must target the
  next stage.
- If `transition_gate.can_advance` is false, the next_prompt field must contain
  a targeted reflection prompt with the blocking question.
- Even reflection outputs include their own transition_gate and either a prompt
  for the target stage if resolved, or another reflection_prompt if not resolved.
- Archived reflection notes must be shareable reasoning summaries, not private
  chain-of-thought dumps.

## Local GPT coach API boundary

Local GPT API use may be authorized only by an explicit workflow command such
as `python scripts/coach_step.py run --execute-api`. This path is outside the
dicoimpro application runtime and is limited to local workflow-coach tooling
under `scripts/`.

Any local GPT coach API request must use the context packets, workflow state,
COACH_GUIDANCE, and STAGE_OUTPUT_SCHEMA as its controlling inputs. It must not
activate prompts in `src/`, must not render or execute prompts through the
dicoimpro runtime, and must not authorize OpenAI runtime inside dicoimpro
application code.

This boundary must not authorize RUN, journal read/write, JournalPatch
application, real data processing, candidate selection, publication, XLSX/CSV
export, old PDF usage, Codex SDK, Codex CLI, automatic PR creation, automatic
merge, or an autonomous loop.

Outputs from the local GPT coach API path are shareable stage notes and prompts
for future review. They must not be private chain-of-thought dumps.

## Manual Codex handoff boundary

GPT coach may produce a codex_prompt for Codex. Repository scripts may package
this prompt for manual handoff, archive a manually supplied Codex return, and
validate the archived return for review.

Repository scripts must not execute Codex SDK/CLI. Repository scripts must not
create/merge PRs, push branches, push to main, call GitHub API, merge PRs, or
run an autonomous loop.

External Codex execution may create PRs only when explicitly authorized by the
user workflow and only after checks pass. Merge remains human-controlled after
review.

This boundary authorizes no RUN/journal/JournalPatch/real data/src runtime
behavior change. It also authorizes no prompt activation, prompt rendering,
prompt execution, OpenAI runtime in `src/`, candidate selection, publication,
XLSX/CSV export, old PDF usage, or production behavior change.

## Program autonomy and verification policy

The future local coach-loop program uses four autonomy levels:

- `stop_human`: the program stops and requires a human decision.
- `auto_local`: the program may perform local non-destructive operations.
- `auto_external_with_budget`: the program may call explicitly authorized
  external services such as GPT within budget and only when the run was
  launched with that authorization.
- `auto_merge_after_verify`: the program may merge a PR only after a complete
  verification gate passes and only when `merge_mode` explicitly allows it.

Merge is manual by default. Auto-merge possible only with auto_after_verify,
meaning `merge_mode: auto_after_verify`, and auto-merge requires complete verify
gate evidence. Verification must stop for a human when objective, scope, risk,
tests, secrets, reviews, CI, PR state, budget, or contradictions are unresolved.
Risk unknown means `stop_human`.

Auto-reflection is allowed only when `reflection_required` is true,
`required_user_intervention` is false, the blocking question is not a
substantive human decision, and `max_reflections_per_stage` is not exceeded.
The recommended default limit is 3; after the limit, stop_human with a summary
of the unresolved blockage.

Repository scripts in Codex 039 only decide, they do not merge. They do not call
GitHub API, git, gh, OpenAI, GPT, Codex SDK, Codex CLI, or run a full autonomous
loop.

## Guarded PR verification and merge execution boundary

Merge is possible only through explicit verify runner tooling. Merge never
happens by default.

`--execute-merge` and `merge_mode auto_after_verify` are required before the
program may attempt a real merge. A fresh verify gate and stable head SHA are
required. The verify gate must confirm PR state, authorized changed files, no
forbidden paths, no detected secrets, valid archived Codex return, guardrail
guarantee, tests, diff-check, CI status, review state, and absence of
contradictions.
--execute-merge and merge_mode auto_after_verify are required. Fresh verify
gate and stable head SHA are required.

Post-merge tests are required after an executed merge. Post-merge failure stops
human and must not trigger destructive auto-repair, auto-revert, or automatic
follow-up merge behavior.
No destructive auto-repair.

This boundary does not authorize RUN/journal/JournalPatch/real data/src runtime
behavior change. It also does not authorize prompt activation, prompt rendering,
prompt execution, candidate selection, publication, XLSX/CSV export, old PDF
usage, OpenAI runtime in `src/`, Codex SDK/CLI, automatic Codex execution, or
autonomous full loop behavior.

## Semi-automatic coach loop runner boundary

The semi-automatic runner may orchestrate context collection, GPT stage
preparation or execution, stage note validation, transition_gate evaluation,
manual Codex handoff, Codex return archive, PR verification and guarded merge
delegation.

GPT is allowed only through explicit --execute-api and only through the
`scripts/coach_step.py` boundary. Codex remains manual handoff: repository
scripts must not execute Codex SDK, Codex CLI, or automatic Codex execution.

Merge is allowed only through the PR verify boundary with `--execute-merge`,
`merge_mode: auto_after_verify`, a successful verify gate and stable head SHA.
Merge is never default, and the runner must not implement a separate merge
pathway.

The runner must `stop_human` for unresolved risk, failed validation,
human-required transition gates, budget excess, invalid Codex returns, missing
PR URLs, red PR verification, manual merge mode, absent explicit merge
authorization, post-merge validation failure, or unknown risk.

This boundary authorizes no RUN/journal/JournalPatch/real data/src runtime
behavior change. It also authorizes no prompt activation, prompt rendering,
prompt execution inside `src/`, candidate selection, publication, XLSX/CSV
export, old PDF usage, Codex SDK/CLI, automatic Codex execution, or unbounded
autonomous loop behavior.

## Runner hardening and operational diagnostics

Runner diagnostics are local-only. `doctor`, `validate-run`, and `explain-next`
may inspect repository files, local run state, ignored artifact settings, and
local workflow module loadability, but they must not call external services.

These diagnostics do not call GPT, OpenAI, Codex, gh, git, pytest, network, or
merge. They must not bypass `stop_human`, must not weaken the API, Codex, PR
verification, or merge boundaries, and must not create a new autonomy level.
Diagnostics must not bypass stop_human.

Diagnostics do not authorize RUN/journal/JournalPatch/real data/src runtime
behavior change. They also do not authorize prompt activation, prompt rendering,
prompt execution inside `src/`, candidate selection, publication, XLSX/CSV
export, old PDF usage, Codex SDK/CLI, automatic Codex execution, or unbounded
autonomous loop behavior.

## Coach-loop freeze status

The coach-loop block is frozen after Codex 043 if tests pass. This freeze adds
no new autonomy and no new workflow capability.

Controlled usage is allowed through the runbook and final audit. API, Codex,
PR verification, and merge boundaries remain unchanged: API requires explicit
`--execute-api`, Codex remains manual handoff, PR verification remains guarded,
and merge remains non-default and explicit.

Any future production integration requires a separate explicit decision. This
freeze authorizes no RUN/journal/JournalPatch/real data/src runtime behavior
change, no prompt activation, no source discovery, no candidate selection, no
publication, no XLSX/CSV export, and no old PDF usage.

## Non-activation rule

The files under `.dicoimpro/` are workflow architecture documents and examples.
They are not prompts consumed by the dicoimpro application, not runtime
configuration, not a RUN plan, and not authorization to call OpenAI, Codex SDK,
or any external service.
