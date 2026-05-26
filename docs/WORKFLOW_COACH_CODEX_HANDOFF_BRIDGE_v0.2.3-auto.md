# Workflow Coach Codex Handoff Bridge - dicoimpro v0.2.3-auto

Status: Codex 038 docs/tests/scripts manual Codex handoff bridge workflow
tooling only. This document defines a local manual handoff bridge between GPT
coach stage notes and Codex execution. It does not activate dicoimpro
application runtime behavior.

## 1. Purpose

Codex 038 adds manual handoff tooling only. The bridge reads a local coach stage
note, extracts the `next_prompt` block, validates that the prompt can be used as
a Codex handoff, writes a standalone markdown packet under
`.dicoimpro/runs/<run_id>/`, archives a manually supplied Codex return, validates
that return, and extracts a GitHub PR URL when present.

It prepares a clean prompt packet to paste into Codex. It archives Codex returns
for review. It is not automatic Codex execution.

## 2. Relation to Codex 035, 036 and 037

Codex 035 defined the future GPT-5.5 Thinking / Codex coach loop output
architecture, stage notes, `transition_gate`, `next_prompt`, and run folders.

Codex 036 added local state and context utilities under `scripts/` for
deterministic workflow files.

Codex 037 added the local GPT stage runner for preparing, optionally executing
with explicit OpenAI authorization, validating, and extracting coach stage notes.

Codex 038 sits after those scaffolds. It consumes a coach stage note produced by
that workflow and packages the handoff for manual Codex use.

## 3. What Codex 038 Implements

Codex 038 implements:

- `scripts/coach_codex_handoff.py`;
- validation of handoff source notes;
- extraction of YAML front matter when present;
- extraction of `transition_gate` when present;
- extraction of `next_prompt` and `next_prompt_type`;
- standalone Codex handoff packet generation;
- deterministic writes under `.dicoimpro/runs/<run_id>/`;
- manual Codex return archiving;
- return validation for PR URL, commit hash, tests, diff-check, files changed,
  and guardrail guarantee;
- PR URL extraction from archived returns;
- tests and docs sync for the bridge boundary.

## 4. What Codex 038 Does Not Implement

Codex 038 does not call Codex SDK. It does not call Codex CLI. It does not
execute Codex. It does not call OpenAI. It does not call GPT. It does not call
network. It does not run an autonomous loop.

It does not create PRs or merge PRs from repository scripts. It does not push
branches, push to main, create tags, create releases, call GitHub API, run
pytest from the script, or run git from the script.

Repository scripts do not execute Codex.

It does not activate prompts, render prompts, execute prompts, or consume
prompts inside `src/`. It does not implement RUN, journal read/write,
JournalPatch application, real data processing, candidate selection, XLSX/CSV
export, old PDF usage, publication, production code changes, or behavior
changes.

## 5. Handoff Packet Model

The handoff packet is a markdown file written to:

```text
.dicoimpro/runs/<run_id>/<NN>_codex_handoff.md
```

The packet includes:

- Handoff metadata;
- Source coach note;
- Intended Codex mission;
- Prompt to paste into Codex;
- Required Codex finalization behavior;
- Forbidden scope;
- Expected files;
- Expected commands;
- Expected final summary;
- PR review boundary.

The packet is standalone enough for manual copy-paste into Codex, while still
recording that repository scripts did not execute Codex.

## 6. Source Note Eligibility

A source note is eligible only when:

- it has a non-empty `next_prompt` block;
- `next_prompt_type` is `codex_prompt` or `stage_prompt`;
- `reflection_prompt` is accepted only when `--allow-reflection` is passed;
- when `transition_gate` is present, `transition_gate.next_prompt_ready` is true;
- when `transition_gate.can_advance` is false, `--allow-blocked-gate` is required.

Malformed front matter, malformed transition gates, missing prompts, empty
prompts, and disallowed prompt types produce human-readable errors.

## 7. Codex Finalization Contract

The handoff packet instructs external Codex execution to:

- run tests;
- run `git diff --check`;
- verify only authorized files changed;
- stage only authorized files;
- commit only after checks pass;
- push branch only after checks pass;
- create PR only after checks pass;
- include PR URL, commit hash, files changed, commands run, pytest result,
  diff-check result, and guardrail guarantee.

Codex must never merge, never push to main, and never create tags/releases. If
checks fail, Codex must not commit, push, or create a PR.

## 8. Codex Return Archive Model

A manually supplied Codex return is archived to:

```text
.dicoimpro/runs/<run_id>/<NN>_codex_return.md
```

Generated run artifacts remain local and ignored by git. The archive step stores
text supplied by a human or external Codex session. The repository script does
not fetch Codex output, call Codex, call GitHub API, or inspect remote PR state.

## 9. Return Validation

Return validation checks that a Codex return:

- includes a PR URL or explicitly says no PR was created because checks failed;
- includes a commit hash when a PR URL is present;
- includes pytest result or explicit test failure;
- includes `git diff --check` result or an explicit reason it was not run;
- includes files changed;
- includes guardrail guarantee;
- does not claim merge completed.

Validation is textual and local. It does not call GitHub API or any network.

## 10. PR Review Boundary

Repository scripts do not create PRs or merge. Repository scripts do not push
branches, push to main, or call GitHub API.

External Codex may create the PR during a user-authorized mission only after all
checks pass. Merge remains human-controlled after GPT review. The bridge records
the return and extracts PR URLs for review; it does not review or merge PRs.

## 11. CLI Commands

Build a handoff packet:

```text
python scripts/coach_codex_handoff.py build --run-id codex_038_example --note-path .dicoimpro/runs/codex_038_example/01_pre_cadrage.md
```

Validate source note eligibility:

```text
python scripts/coach_codex_handoff.py validate-source --note-path .dicoimpro/runs/codex_038_example/01_pre_cadrage.md
```

Archive a manually supplied Codex return:

```text
python scripts/coach_codex_handoff.py archive-return --run-id codex_038_example --return-path codex_return.txt
```

Validate a Codex return:

```text
python scripts/coach_codex_handoff.py validate-return --return-path .dicoimpro/runs/codex_038_example/05_codex_return.md
```

Extract a PR URL:

```text
python scripts/coach_codex_handoff.py extract-pr --return-path .dicoimpro/runs/codex_038_example/05_codex_return.md
```

`build` and `archive-return` refuse to overwrite existing target files unless
`--overwrite` is passed.

## 12. Safety Boundaries

Codex 038 is docs/tests/scripts only. No `src/` production code changes are
authorized.

The bridge does not call Codex SDK, does not call Codex CLI, does not execute
Codex, does not call OpenAI, does not call GPT, does not call network, does not
call GitHub API, does not run git from the script, and does not run pytest from
the script.

It does not run an autonomous loop, does not create or merge PRs from repository
scripts, does not activate or execute prompts inside `src/`, does not run RUN,
does not touch journal or JournalPatch, does not process real data, does not
export XLSX/CSV, does not use the old PDF, and does not change runtime behavior.

## 13. Future Implementation Phases

Possible future phases, each requiring explicit authorization:

1. Richer static parsing of expected files and expected commands.
2. Human review helper for archived Codex returns.
3. PR review packet builder that still avoids GitHub API by default.
4. Explicit transport prototypes with hard approval gates.
5. Fully audited coach loop runner with no automatic merge and strict stop
   conditions.

None of these phases are implemented by Codex 038.

## 14. Verdict

GO for manual handoff tooling only.

NO-GO for Codex SDK, Codex CLI, automatic Codex execution, OpenAI calls, GPT
calls, network calls, autonomous loop, repository-script PR creation or merge,
prompt activation/rendering/execution in `src/`, RUN, journal, JournalPatch,
real data, XLSX/CSV export, old PDF usage, publication, production code, or
behavior change.
