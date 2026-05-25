# Workflow Coach GPT Stage Runner - dicoimpro v0.2.3-auto

Status: Codex 037 docs/tests/scripts workflow tooling only. This document
defines the local GPT-5.5 Thinking stage runner boundary for the future coach
loop. It does not activate dicoimpro application runtime behavior.

## 1. Purpose

Codex 037 introduces an explicit local GPT coach API path for preparing and,
only when explicitly requested, executing one GPT-5.5 Thinking coach stage.

The runner prepares a model prompt from local workflow files, can save the
prompt, can optionally call the OpenAI Responses API, can save the model text as
a stage note, can validate the note shape, can extract transition_gate and
next_prompt, and can update local workflow state only through transition_gate.

## 2. Relation to Codex 035 and 036

Codex 035 defined coach guidance, stage schema, workflow state example, stage
notes, transition_gate, next_prompt, and context packet expectations.

Codex 036 added local state-machine and context-collector utilities under
`scripts/`.

Codex 037 adds `scripts/coach_step.py` as a local stage runner on top of those
scaffolds. It uses the Codex 035 documents and Codex 036 state utilities. The
state machine still follows transition_gate; it does not invent maturity
decisions.

## 3. What Codex 037 Implements

Codex 037 implements:

- local prompt preparation for a requested GPT-5.5 Thinking stage;
- writing `.dicoimpro/runs/<run_id>/<NN>_<stage>.model_prompt.md`;
- explicit optional OpenAI Responses API execution through `--execute-api`;
- writing model text to `.dicoimpro/runs/<run_id>/<NN>_<stage>.md`;
- local validation of returned stage notes;
- transition_gate extraction as JSON;
- optional local state update through transition_gate with `--update-state`;
- docs and tests proving the API path is explicit and not default.

## 4. What Codex 037 Does Not Implement

Codex 037 does not implement dicoimpro application runtime OpenAI activation.
This path is not dicoimpro application runtime. This path is not RoutingAgent
execution. This path is not prompt activation inside `src/`.

Codex 037 does not implement Codex SDK, Codex CLI integration, autonomous loop,
automatic Codex execution, RUN, real entry processing, candidate selection,
active journal read/write, JournalPatch application, XLSX/CSV export, old PDF
usage, publication, automatic PR creation, or automatic merge inside repository
scripts.

## 5. CLI Commands

Prepare only, no API call:

```text
python scripts/coach_step.py prepare --stage pre_cadrage --run-id codex_037_example
```

Explicit API execution:

```text
python scripts/coach_step.py run --stage pre_cadrage --run-id codex_037_example --execute-api
```

Validate a local stage note, no API call:

```text
python scripts/coach_step.py validate-note --note-path .dicoimpro/runs/codex_037_example/01_pre_cadrage.md
```

Extract a transition_gate, no API call:

```text
python scripts/coach_step.py extract-gate --note-path .dicoimpro/runs/codex_037_example/01_pre_cadrage.md
```

The `run` command without `--execute-api` fails clearly and tells the user to
use `prepare` for no-API prompt generation.

## 6. API Execution Boundary

The API is never called by default. Tests never call the API.

API execution requires both:

```text
--execute-api
OPENAI_API_KEY
```

The OpenAI SDK import is lazy/dynamic and happens only inside the explicit API
execution path. If the OpenAI package is missing, the script returns a clear
human-readable error only when `--execute-api` is requested.

No API key is committed, printed, logged, or stored in output files.

## 7. Model and Environment Variables

The default model is `gpt-5.5`. It can be changed with:

```text
--model <model-name>
```

`OPENAI_API_KEY` must be present in the environment for explicit API execution.
The key is consumed by the OpenAI SDK client and is not written to prompt files,
stage notes, logs, or stdout.

## 8. Stage Prompt Construction

The stage prompt is built from:

- `.dicoimpro/COACH_GUIDANCE.md`;
- `.dicoimpro/STAGE_OUTPUT_SCHEMA.md`;
- `.dicoimpro/WORKFLOW_STATE.local.json` if present, otherwise
  `.dicoimpro/WORKFLOW_STATE.example.json`;
- `.dicoimpro/runs/<run_id>/00_context.md` if present;
- optional previous stage note;
- requested stage name;
- optional user instruction or reflection instruction.

The prompt instructs GPT-5.5 Thinking to act as the dicoimpro coach, produce a
shareable reasoning summary rather than private chain-of-thought, produce one
valid stage note, include YAML front matter, required body sections,
transition_gate, next_prompt, and avoid inventing repository facts absent from
context.

## 9. Stage Note Validation

The validator checks:

- markdown YAML front matter exists;
- required front matter field names exist;
- required body sections exist;
- transition_gate block exists;
- transition_gate required fields exist;
- next_prompt block exists;
- next_prompt_type is one of `stage_prompt`, `reflection_prompt`,
  `codex_prompt`, or `none`.

Validation uses Python standard library parsing. It does not require PyYAML.

## 10. transition_gate Extraction

`extract-gate` parses the transition_gate block and prints it as JSON. The gate
must include the fields defined by STAGE_OUTPUT_SCHEMA and must pass the same
local validation used by the state machine.

Malformed gates are rejected with human-readable errors.

## 11. State Update Model

State update occurs only when `--update-state` is passed. The runner updates
`.dicoimpro/WORKFLOW_STATE.local.json` only through transition_gate.

The update refuses to advance if `transition_gate.can_advance` is false. It
also refuses to advance if `transition_gate.next_prompt_ready` is false. If
`next_prompt_type` is `reflection_prompt`, the local state reflection counter is
incremented by the existing state utility.

## 12. Safety Boundaries

The local coach GPT API path is workflow tooling only. It is outside dicoimpro
application runtime.

OpenAI runtime inside dicoimpro application code remains forbidden. Prompt
activation, rendering, or execution inside dicoimpro runtime remains forbidden.

The script does not call Codex SDK or Codex CLI. The script does not run an
autonomous loop. The script does not run RUN, journal, JournalPatch or real data
processing. The script also does not run publication, candidate selection,
XLSX/CSV export, or old PDF usage. Repository scripts do not automate PR
creation or merge.

## 13. Future Implementation Phases

Future phases may add stricter note parsing, richer stage indexing, manual
review helpers, or a transport layer after explicit authorization.

Any future phase must preserve explicit API boundaries, avoid application
runtime activation, and keep state advancement bound to transition_gate.

## 14. Verdict

GO for local docs/tests/scripts workflow tooling.

NO-GO for API calls by default, test-time API calls, dicoimpro runtime OpenAI
activation, RoutingAgent execution, prompt activation inside `src/`, Codex
SDK/CLI, autonomous loop, automatic Codex execution, RUN, journal,
JournalPatch, real data processing, XLSX/CSV export, old PDF usage,
publication, automatic PR/merge automation, production code, or behavior
change.
