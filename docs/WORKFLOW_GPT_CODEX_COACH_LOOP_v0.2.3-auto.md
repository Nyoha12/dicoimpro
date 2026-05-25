# Workflow GPT-5.5 Thinking / Codex Coach Loop - dicoimpro v0.2.3-auto

Status: Codex 035 documentation/tests/scaffold only. This document defines the
output architecture for a future local coach loop. It implements no API call, no
Codex SDK call, no Codex CLI integration, no prompt activation, and no
autonomous execution loop.

## 1. Purpose

The purpose is to define the first architecture scaffold for a local GPT-5.5
Thinking <-> Codex coach loop. The scaffold describes stage outputs,
transition gates, next prompts, context packets, and safety boundaries before
any runtime transport exists.

## 2. Why this architecture exists

The coach loop is designed to replace manual relaunching and copy-pasting
between GPT-5.5 Thinking, Codex, git, tests, and PR review. It does not remove
human authorization. It gives future orchestration a structured way to carry the
current note, the maturity decision, and the next prompt without inventing
workflow state outside the GPT stage output.

## 3. The target loop

Target loop:

```text
repo context + last merged PR
-> GPT-5.5 Thinking pre_cadrage
-> GPT-5.5 Thinking cadrage
-> GPT-5.5 Thinking decision
-> GPT-5.5 Thinking Codex prompt
-> Codex execution
-> Codex return to GPT-5.5 Thinking
-> GPT-5.5 Thinking post-Codex review
-> PR review
-> post-merge review
-> loop continues
```

GPT-5.5 Thinking is the coach/strategist. Codex is the executor. Python
orchestration is only a future transport layer that reads files, moves prompts,
and follows the transition_gate after explicit authorization.

## 4. What this Codex implements

Codex 035 implements only:

- `.dicoimpro/COACH_GUIDANCE.md`
- `.dicoimpro/STAGE_OUTPUT_SCHEMA.md`
- `.dicoimpro/WORKFLOW_STATE.example.json`
- `.dicoimpro/runs/.gitkeep`
- this workflow documentation
- documentation sync updates
- static tests for the scaffold and guardrails

This is a documentation/tests/scaffold-only change and creates no production
behavior change.

## 5. What this Codex does not implement

Codex 035 does not implement:

- no API call implementation;
- no OpenAI API implementation;
- no Codex SDK implementation;
- no Codex CLI implementation;
- no autonomous loop;
- no automatic PR creation;
- no automatic merge;
- no prompt activation, rendering, execution, or consumption inside dicoimpro;
- no OpenAI runtime activation inside dicoimpro application code;
- no RUN;
- no real entry processing;
- no candidate selection;
- no journal read/write;
- no JournalPatch application;
- no XLSX/CSV export;
- no old PDF usage;
- no production code or runtime behavior change.

## 6. Stage model

The required stage sequence is:

```text
context
pre_cadrage
cadrage
decision
codex_prompt
codex_return
post_codex_review
pr_review
post_merge_review
```

Each GPT stage produces the current note, transition_gate, and next prompt or
reflection prompt. A stage note is a shareable reasoning summary with structured
metadata and the current stage-specific outputs.

## 7. Reflection model

Reflection is optional, targeted, and unlimited. It is triggered only when the
next stage is not ready or when the user requests deeper analysis.

Reflection is not a separate mandatory maturity pass. It answers a specific
blocking question. Even reflection outputs include their own transition_gate and
either a prompt for the target stage if resolved, or another reflection_prompt if
the blocking question remains unresolved.

Archived reflection notes must be shareable summaries, not private
chain-of-thought dumps.

## 8. Transition gate model

The transition_gate is the source of truth for stage movement. It includes:

- evaluated_next_stage
- can_advance
- reflection_required
- next_prompt_ready
- next_prompt_type
- blocking_question
- reason
- required_user_intervention
- allowed_to_execute_automatically

The script must not decide maturity arbitrarily. The script reads
transition_gate and follows it. A stage must never advance when
`can_advance` is false or `next_prompt_ready` is false.

## 9. Next prompt generation model

There is no separate mandatory GPT call only to generate the next prompt. The
maturity assessment and next prompt generation happen inside the current GPT
stage output.

If the next stage is ready, the current stage output contains a next_prompt for
that stage. If the next stage is not ready, the same field contains a targeted
reflection_prompt with the blocking question. If the workflow is complete,
`next_prompt_type` is `none` and the note explains why.

## 10. Repository context packet model

Repo context is refreshed at each stage through context packets. Context packets
must be filtered to avoid token overload and must include only the evidence
needed for the current stage.

Stage-specific context packets:

### pre_cadrage

- project state summary;
- last merged Codex;
- main test count;
- recent PR summary;
- roadmap/current threshold.

### cadrage

- pre_cadrage note;
- repo status;
- relevant docs paths;
- guardrail status.

### decision

- cadrage note;
- options;
- risks;
- tests/docs impact.

### codex_prompt

- decision note;
- allowed files;
- forbidden files;
- expected tests;
- guardrails.

### codex_return / post_codex_review

- Codex summary;
- git diff stat;
- git status;
- commands run;
- test result;
- changed files.

### pr_review

- PR URL;
- PR diff;
- CI status if available;
- Codex return;
- guardrail checklist.

### post_merge_review

- main branch test result;
- merge commit/PR;
- validated state;
- next threshold candidates.

## 11. File layout

```text
.dicoimpro/
  COACH_GUIDANCE.md
  STAGE_OUTPUT_SCHEMA.md
  WORKFLOW_STATE.example.json
  runs/
    .gitkeep
docs/
  WORKFLOW_GPT_CODEX_COACH_LOOP_v0.2.3-auto.md
tests/
  test_coach_loop_output_architecture.py
```

Future run artifacts may use `.dicoimpro/runs/<run_id>/` after explicit
authorization. This Codex only creates the directory placeholder.

## 12. Safety boundaries

The scaffold does not authorize OpenAI runtime, prompt execution, Codex SDK,
RUN, journal access, JournalPatch application, real data processing, candidate
selection, publication, XLSX/CSV export, or old PDF use.

Authorized runtime paths are unchanged. The existing fake-only and mock-only
boundaries remain the only active behavior. `.dicoimpro` files are architecture
documents and examples; dicoimpro runtime must not read, render, execute, or
consume them.

## 13. Future implementation phases

Possible future phases, each requiring explicit authorization:

1. Static local script that only validates note/schema files.
2. Local context-packet builder with no prompt execution.
3. Manual transport helper that prepares files for a human to paste.
4. OpenAI transport prototype with injected clients and disabled defaults.
5. Codex transport prototype with explicit human approval gates.
6. Fully audited loop runner with no automatic merge and strict stop conditions.

None of these phases are implemented by Codex 035.

## 14. Verdict

GO for documentation/tests/scaffold only.

NO-GO for API calls, Codex SDK calls, autonomous execution, prompt activation,
prompt rendering, prompt execution, prompt consumption, OpenAI runtime
activation inside dicoimpro, RUN, journal read/write, JournalPatch application,
real data processing, candidate selection, XLSX/CSV export, old PDF usage,
automatic PR creation, automatic merge, and production behavior change.
