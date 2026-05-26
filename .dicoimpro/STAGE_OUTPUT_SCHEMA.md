# Stage Output Schema - GPT-5.5 Thinking / Codex Loop

Status: markdown schema for future local workflow notes. This is a
documentation/test scaffold only. It defines output shape and does not implement
API calls, prompt execution, Codex SDK calls, or an autonomous loop.

## Note format

Each stage note is a markdown file with YAML front matter followed by required
body sections. The front matter is metadata for orchestration; the body is a
shareable reasoning summary, not private chain-of-thought.

Required YAML front matter fields:

```yaml
---
run_id: codex_035_example
stage: pre_cadrage
created_at: 2026-05-25T00:00:00Z
input_refs: []
repo_context_refs: []
previous_stage_ref: null
can_advance: null
reflection_required: false
next_stage: cadrage
next_prompt_type: stage_prompt
next_prompt_path_suggested: .dicoimpro/runs/codex_035_example/02_cadrage_prompt.md
blocking_question: null
guardrail_risk_level: low
---
```

The required front matter field names are:

- `run_id`
- `stage`
- `created_at`
- `input_refs`
- `repo_context_refs`
- `previous_stage_ref`
- `can_advance`
- `reflection_required`
- `next_stage`
- `next_prompt_type`
- `next_prompt_path_suggested`
- `blocking_question`
- `guardrail_risk_level`

The front matter must remain parseable by local standard-library scripts. Use
simple `key: value` lines for these required fields. This scaffold does not
require PyYAML and does not authorize adding PyYAML to parse stage notes.

## Required body sections

Every stage note must include these sections in this order:

1. Stage objective
2. Inputs used
3. Repository context summary
4. Current-stage analysis summary
5. Resolved points
6. Unresolved points
7. Guardrail and scope check
8. Transition gate
9. Next prompt

## Transition gate block

The `transition_gate` block is required in the "Transition gate" section.

Required fields:

```yaml
transition_gate:
  evaluated_next_stage: cadrage
  can_advance: true
  reflection_required: false
  next_prompt_ready: true
  next_prompt_type: stage_prompt
  blocking_question: null
  reason: "The next stage has enough context."
  required_user_intervention: false
  allowed_to_execute_automatically: false
```

Field rules:

- `evaluated_next_stage` names the next intended stage.
- `can_advance` is the maturity decision for the next stage.
- `reflection_required` is true only when the next stage cannot be produced
  properly before answering a blocking question.
- `next_prompt_ready` must be true before the workflow advances.
- `next_prompt_type` is one of `stage_prompt`, `reflection_prompt`,
  `codex_prompt`, or `none`.
- `blocking_question` is null when no reflection is required, otherwise it is
  the specific question the reflection must resolve.
- `reason` explains the gate decision as a shareable summary.
- `required_user_intervention` identifies whether the user must answer before
  the next stage can proceed.
- `allowed_to_execute_automatically` remains false in this scaffold.

Autonomy rules:

- `transition_gate.required_user_intervention` controls autonomy. When it is
  true, local workflow tooling must stop for a human before advancing.
- `blocking_question` may trigger `stop_human` when it asks for a substantive
  human decision such as scope approval, risk acceptance, budget approval,
  secret handling, publication, merge, or production behavior change.
- `next_prompt_ready` is not sufficient for auto-advance when
  `required_user_intervention` is true.

The transition_gate block must remain parseable enough for
`scripts/coach_step.py`: keep the `transition_gate:` line followed by indented
simple `key: value` fields. The local state machine follows this block and does
not invent maturity decisions from prose.

## Next prompt block

The `next_prompt` block is mandatory in every stage note.

If `can_advance` is true and `next_prompt_ready` is true, `next_prompt` contains
the next stage prompt. If `can_advance` is false, `next_prompt` contains a
targeted reflection prompt using `next_prompt_type: reflection_prompt` and the
blocking question. If the workflow is complete, `next_prompt_type` is `none` and
`next_prompt` explains why no further prompt is required.

The next_prompt block must include a literal `next_prompt:` marker so local
workflow scripts can extract it without prompt rendering or prompt execution.

Example:

```markdown
## 9. Next prompt

next_prompt_type: stage_prompt

next_prompt:
Ask GPT-5.5 Thinking to produce the cadrage note using the attached context
packet and the pre_cadrage conclusions.
```

## Expected stages

Required workflow stages:

- `context`
- `pre_cadrage`
- `cadrage`
- `decision`
- `codex_prompt`
- `codex_return`
- `post_codex_review`
- `pr_review`
- `post_merge_review`

Optional reflection stages:

- `reflection_before_cadrage`
- `reflection_before_decision`
- `reflection_before_codex_prompt`
- `reflection_before_post_codex_review`
- `reflection_before_pr_review`
- `reflection_before_post_merge_review`

## Stage-specific outputs

### pre_cadrage

Required output fields:

- `problem_statement`
- `technical_threshold`
- `open_options`
- `risks`
- `candidate_next_stage`

### cadrage

Required output fields:

- `authorized_scope`
- `forbidden_scope`
- `likely_files`
- `tests_expected`
- `guardrails`
- `ready_for_decision`

### decision

Required output fields:

- `single_decision`
- `rejected_alternatives`
- `success_criteria`
- `ready_for_codex_prompt`

### codex_prompt

Required output fields:

- `codex_task_prompt`
- `branch_name`
- `expected_files`
- `forbidden_changes`
- `required_commands`
- `expected_summary_format`

### codex_return

Required output fields:

- `files_changed`
- `commands_run`
- `test_results`
- `apparent_guardrail_status`
- `pr_readiness`

### post_codex_review

Required output fields:

- `diff_summary`
- `test_evidence`
- `blocking_issues`
- `pr_recommendation`

### pr_review

Required output fields:

- `pr_url`
- `mergeability`
- `findings`
- `merge_verdict`

### post_merge_review

Required output fields:

- `main_test_result`
- `validated_state`
- `next_possible_threshold`

### reflection

Required output fields:

- `target_stage`
- `reflection_index`
- `trigger`
- `blocking_question`
- `analysis_summary`
- `conclusion`
- `updated_transition_gate`

Reflection output must include a transition_gate and next_prompt. If the
blocking question is resolved, the next_prompt targets the original target
stage. If it is not resolved, the next_prompt is another targeted
reflection_prompt.
