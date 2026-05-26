# Workflow Coach Autonomy Verify Gate - dicoimpro v0.2.3-auto

Status: Codex 039 docs/tests/scripts autonomy policy and pre-merge verify gate
for the future coach-loop program. This document models decisions only. It does
not implement a real merge.

## 1. Purpose

Codex 039 encodes the autonomy policy of the future local coach-loop program and
the pre-merge verification gate that would be required before any automated
merge could be considered.

The verify gate decides from supplied local/structured evidence. It does not
collect remote state, call external services, or perform the merge.

## 2. Relation to Codex 035-038

Codex 035 defined the coach loop output architecture, stage notes,
`transition_gate`, and `next_prompt`.

Codex 036 added local state and context utilities.

Codex 037 added the explicit GPT stage runner boundary.

Codex 038 added the manual Codex handoff bridge and Codex return archive model.

Codex 039 adds policy and local decision tooling for program autonomy,
auto-reflection limits, external API budget checks, and pre-merge verification
decisions.

## 3. Program Autonomy Levels

The program autonomy levels are:

1. `stop_human` - the program stops and requires a human decision.
2. `auto_local` - the program may perform local non-destructive operations.
3. `auto_external_with_budget` - the program may call explicitly authorized
   external services such as GPT within budget and only when the run was
   launched with that authorization.
4. `auto_merge_after_verify` - the program may merge a PR only after complete
   verification gate success and only when `merge_mode` explicitly allows it.

Merge is manual by default.

## 4. Human Intervention Triggers

Human intervention is required when:

- run objective is absent or ambiguous;
- scope change is proposed;
- `transition_gate.required_user_intervention` is true;
- `transition_gate.can_advance` is false and the reason is a substantive
  decision;
- GPT note, Codex return, actual diff, PR metadata, or tests contradict each
  other;
- sensitive files are touched without explicit authorization;
- `src/` is touched while the run is docs/tests/scripts only;
- dependencies are modified without explicit authorization;
- workflow files are modified;
- secrets, API keys, or tokens are detected;
- tests fail;
- `git diff --check` fails;
- GPT note is invalid;
- Codex return is invalid;
- PR is not mergeable;
- CI is red;
- a review requests changes;
- API budget is exceeded;
- risk cannot be classified, stop_human.

## 5. Auto-Local Behavior

`auto_local` covers deterministic, local, non-destructive operations that do not
change production behavior and do not contact external services. It can decide
from supplied JSON, validate local policy files, summarize policy, and prepare
structured decision output.

`auto_local` does not authorize a full autonomous loop, branch push, PR creation,
real merge, destructive repair, RUN, journal mutation, JournalPatch application,
real data processing, or publication.

## 6. External API Behavior With Budget

`auto_external_with_budget` is a future program level, not activated by Codex
039. It may call explicitly authorized external services only when:

- the run was launched with that authorization;
- budget counters remain within policy;
- the requested action does not require human intervention;
- the action is still within the authorized workflow stage.

Codex 039 only evaluates supplied budget counters. It does not call OpenAI, GPT,
Codex SDK, Codex CLI, network, or any external API.

## 7. Auto-Reflection Policy

Auto-reflection is allowed only when:

- `reflection_required` is true;
- `required_user_intervention` is false;
- the blocking question is not a substantive human decision;
- `max_reflections_per_stage` is not exceeded.

The recommended default `max_reflections_per_stage` is 3. After the limit, the
program must `stop_human` with a summary of the unresolved blockage.

## 8. Pre-Merge Verification Gate

The program may auto-merge only if all are true:

- `merge_mode` is `auto_after_verify`;
- PR is detected;
- PR is open;
- PR is not draft;
- PR is mergeable;
- base branch is `main`;
- head branch is authorized;
- head SHA is stable or explicitly verified;
- changed files are within authorized scope;
- no forbidden file is touched;
- no secret is detected;
- Codex return is archived and valid;
- guardrail guarantee is present;
- tests are OK according to run policy;
- `git diff --check` is OK;
- CI is OK or explicitly not required by policy;
- no blocking review exists;
- no `REQUEST_CHANGES` review exists;
- no contradiction is detected;
- auto-merge is explicitly authorized by policy and run config.

The verify gate decides from supplied local/structured evidence.

## 9. Auto-Merge Policy

Auto-merge is allowed only after full verify gate success. The program may be
autonomous up to merge only if `merge_mode` is `auto_after_verify`.

Auto-merge is never allowed when verification is incomplete or red. Auto-merge
is a policy possibility, not an implemented merge action in Codex 039.

## 10. Post-Merge Validation Policy

After an auto-merge, a future implementation must:

- sync main;
- run post-merge tests according to policy;
- record the post-merge result;
- stop_human if post-merge validation fails.

Post-merge failure stops for human intervention and does not trigger destructive
auto-repair.

## 11. What Codex 039 Implements

Codex 039 implements:

- `.dicoimpro/WORKFLOW_AUTONOMY_POLICY.example.json`;
- `scripts/coach_autonomy.py`;
- local policy validation;
- transition_gate autonomy decisions;
- human intervention decisions;
- auto-reflection decisions and reflection limit enforcement;
- API budget decisions from supplied counters;
- pre-merge report validation;
- auto-merge allowed/blocked decisions from supplied reports;
- docs and tests for the policy boundary.

## 12. What Codex 039 Does Not Implement

Codex 039 does not perform real merge. It does not call GitHub API. It does not
run git. It does not run gh. It does not run pytest. It does not call OpenAI. It
does not call GPT. It does not call Codex SDK or Codex CLI.

There is no git/gh execution.

It does not implement an autonomous full loop, RUN, journal read/write,
JournalPatch application, real data processing, candidate selection, XLSX/CSV
export, old PDF usage, publication, production code changes, or `src/` runtime
behavior changes.

## 13. CLI Commands

Validate the policy:

```text
python scripts/coach_autonomy.py validate-policy
```

Decide whether a transition gate can continue automatically:

```text
python scripts/coach_autonomy.py decide-gate --gate-json path/to/gate.json
```

Decide whether auto-reflection is allowed:

```text
python scripts/coach_autonomy.py can-reflect --gate-json path/to/gate.json --reflection-count 1
```

Decide whether auto-merge would be allowed:

```text
python scripts/coach_autonomy.py verify-merge --report-json path/to/pre_merge_report.json
```

Summarize the policy:

```text
python scripts/coach_autonomy.py summarize-policy
```

The CLI prints decisions only. It never performs the action itself.

## 14. Safety Boundaries

Codex 039 is docs/tests/scripts only. No production code under `src/` may be
modified.

Repository scripts only decide from supplied local JSON. They do not call
GitHub API, git, gh, pytest, OpenAI, GPT, Codex SDK, Codex CLI, network, or any
merge execution surface.

The policy does not authorize prompt activation, prompt rendering, prompt
execution inside `src/`, RUN, journal mutation, JournalPatch application, real
data processing, candidate selection, XLSX/CSV export, old PDF usage,
publication, branch push, tag creation, release creation, or behavior change.

## 15. Future Implementation Phases

Possible future phases, each requiring explicit authorization:

1. Richer supplied-report schema and evidence bundle validation.
2. Local PR review packet generation without remote calls by default.
3. Explicit remote metadata collection with hard human approval gates.
4. Explicit merge executor with dry-run first and no destructive repair.
5. Post-merge validation recorder.

None of these phases are implemented by Codex 039.

## 16. Verdict

GO for docs/tests/scripts policy and decision modeling.

NO-GO for real merge, GitHub API, git execution, gh execution, pytest execution
from the script, OpenAI, GPT, Codex SDK, Codex CLI, autonomous full loop, RUN,
journal, JournalPatch, real data, XLSX/CSV export, old PDF usage, publication,
production code changes, or `src/` runtime behavior change.
