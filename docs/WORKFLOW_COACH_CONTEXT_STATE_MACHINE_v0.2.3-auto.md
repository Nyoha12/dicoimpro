# Workflow Coach Context State Machine - dicoimpro v0.2.3-auto

Status: Codex 036 docs/tests/scripts scaffold only. This document describes the
local context collector and deterministic workflow-state utilities for a future
GPT-5.5 Thinking / Codex coach loop. It does not authorize runtime activation.

## 1. Purpose

Codex 036 turns the Codex 035 output architecture into local files and
deterministic state/context utilities. The goal is to prepare a local scaffold
that can read workflow state, initialize a local state file, create run folders,
collect filtered repository context, and apply transition_gate decisions to
state in a reproducible way.

The state machine does not decide maturity arbitrarily. It only follows
transition_gate fields produced by a future stage note.

## 2. Relation to Codex 035

Codex 035 defined the output architecture: coach guidance, stage output schema,
workflow state example, transition_gate shape, next_prompt shape, targeted
reflection rules, and a run folder placeholder under `.dicoimpro/runs/`.

Codex 036 keeps that architecture non-runtime and adds local utilities around
it. The utilities do not call GPT-5.5, do not call OpenAI, do not call Codex
SDK, do not call Codex CLI, and do not start an autonomous loop.

## 3. What Codex 036 Implements

Codex 036 implements:

- `.dicoimpro/.gitignore` for generated local workflow artifacts;
- `scripts/coach_state.py` for local JSON state validation and deterministic
  transition_gate state updates;
- `scripts/coach_collect_context.py` for local repository context packets;
- `docs/WORKFLOW_COACH_CONTEXT_STATE_MACHINE_v0.2.3-auto.md`;
- tests covering the state-machine scaffold, context collector, docs sync, and
  runtime boundaries.

## 4. What Codex 036 Does Not Implement

Codex 036 does not implement API calls, OpenAI runtime, Codex SDK, Codex CLI,
GPT calls, autonomous loops, PR automation, merge automation, prompt
activation, prompt rendering, prompt execution, or prompt consumption.

It also does not authorize RUN, journal read/write, JournalPatch application,
real entry processing, candidate selection, real data processing, publication,
XLSX/CSV export, old PDF usage, or production behavior change.

## 5. Local State File Model

The tracked example remains `.dicoimpro/WORKFLOW_STATE.example.json`. A local
working copy can be initialized as `.dicoimpro/WORKFLOW_STATE.local.json`.

The state utility validates required keys, guardrail objects, workflow
permission objects, reflection counters, nullable fields, and boolean fields.
Sensitive guardrails and workflow permissions must remain false by default.

Generated local state is ignored by git through `.dicoimpro/.gitignore`.

## 6. Run Folder Model

Run folders live under `.dicoimpro/runs/<run_id>/`.

The tracked `.dicoimpro/runs/.gitkeep` preserves the directory scaffold.
Generated run packets and local run artifacts are ignored by git. The scaffold
creates folders only for local workflow organization; it does not execute a run.

## 7. Context Packet Model

The context collector refreshes repo context at each stage by writing a markdown
packet to `.dicoimpro/runs/<run_id>/00_context.md` by default.

Context packets are filtered to avoid token overload. They include only local
repository identity, current branch, current HEAD, last commit, recent commits,
git status, diff stat, changed files, optional state metadata, guardrails, and
notes for the next future GPT-5.5 Thinking stage.

The collector may run only local git commands with timeouts:

```text
git status --short
git branch --show-current
git rev-parse HEAD
git log -1 --oneline
git diff --stat
git diff --name-only
git log --oneline -5
```

It does not run pytest by default and does not call network, GitHub API, OpenAI,
Codex SDK, Codex CLI, RUN, journal, JournalPatch, or prompts.

## 8. Transition Gate State Update Model

The state utility reads a transition_gate dictionary and validates required
fields. A stage may advance only when both fields are true:

```text
transition_gate.can_advance == true
transition_gate.next_prompt_ready == true
```

If either value is false, the utility refuses to advance with a human-readable
error. The state machine does not infer maturity from any other source.

When `next_prompt_type` is `reflection_prompt`, the utility increments
`reflection_count_current_stage`. Otherwise it preserves the reflection count.
The utility records the stage note path and follows the evaluated next stage
from transition_gate.

## 9. CLI Commands

```text
python scripts/coach_state.py init --run-id codex_036_example
python scripts/coach_state.py validate
python scripts/coach_state.py ensure-run --run-id codex_036_example
python scripts/coach_collect_context.py --run-id codex_036_example
```

These commands are local scaffold utilities. They do not call any model, Codex,
network, GitHub API, pytest, RUN, journal, JournalPatch, or OpenAI.

## 10. Safety Boundaries

Codex 036 keeps authorized runtime paths unchanged. Scripts under `scripts/`
are local workflow scaffold utilities only.

This scaffold does not authorize OpenAI runtime, prompt execution, RUN, journal,
JournalPatch, real data, publication, production behavior, PR automation, merge
automation, Codex SDK, Codex CLI, or an autonomous loop.

## 11. Future Implementation Phases

Future phases may add explicit parsing of stage notes, stricter schema checks,
manual review tooling, or transport layers after separate authorization.

Those future phases must still preserve the transition_gate rule: the local
state machine follows the gate; it does not invent the gate, execute prompts, or
decide maturity independently.

## 12. Verdict

GO for docs/tests/scripts scaffold only.

NO-GO for API calls, Codex SDK, Codex CLI, GPT calls, autonomous loop, prompt
activation, prompt rendering, prompt execution, prompt consumption, PR or merge
automation, RUN, journal, JournalPatch, real data, XLSX/CSV export, old PDF
usage, publication, production code, or behavior change.
