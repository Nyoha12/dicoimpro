# Coach Loop Final Audit Freeze - v0.2.3-auto

Status: Codex 043 docs/tests final audit and freeze of the coach-loop
development block.

## 1. Purpose

Codex 043 closes the Codex 035-042 coach-loop development block with a final
audit and freeze. Codex 043 adds no runtime feature, no script change, no new
autonomy, no API behavior, no Codex execution behavior, no merge pathway, no
prompt activation, and no production runtime behavior.
This document confirms Codex 035-042 coherence.
Codex 043 adds no new autonomy.
Codex 043 makes no OpenAI/GPT call.
Codex 043 adds no Codex SDK/CLI.

## 2. Final Status

Current main before Codex 043 is 609 tests passing. The coach-loop block is
ready for controlled local usage after merge if tests pass.

This freeze does not authorize production integration. It confirms that the
existing local workflow tooling can be used under the documented boundaries.

## 3. Codex 035-042 Recap

- Codex 035: output architecture for the local GPT-5.5 Thinking / Codex coach
  loop.
- Codex 036: context collector and transition_gate state machine.
- Codex 037: GPT stage runner with explicit API boundary.
- Codex 038: manual Codex handoff bridge.
- Codex 039: autonomy policy and pre-merge verify gate.
- Codex 040: PR verification and optional guarded merge runner.
- Codex 041: semi-automatic coach loop runner.
- Codex 042: hardening, runbook, and local diagnostics.

## 4. Current Verified Baseline Before Codex 043

The baseline before Codex 043 is:

```text
Codex 001-042 merged into main.
Current main before Codex 043 is 609 tests passing.
Coach-loop workflow tooling exists from Codex 035 to Codex 042.
Generated .dicoimpro/runs artifacts are local/ignored.
```

## 5. Existing Workflow Bricks

The frozen block includes local workflow bricks for context collection, prompt
preparation, optional GPT stage execution, note validation, transition gate
evaluation, autonomy decisions, manual Codex handoff, Codex return archiving,
PR verification, optional guarded merge delegation, diagnostics, and runbook
usage.

These bricks live in existing `.dicoimpro/`, `docs/`, `scripts/`, and `tests/`
workflow surfaces. Codex 043 does not modify scripts.

## 6. Controlled Usage Path

Controlled local usage starts with diagnostics, then a prepare-only run, then
human review. API calls, Codex execution, PR verification, and guarded merge
remain separate and explicit stages.

The coach-loop block is ready for controlled local usage after merge if tests
pass, but that usage is local workflow tooling only.

## 7. Default Non-Destructive Behavior

The default behavior is local and non-destructive. Preparing a run writes local
ignored artifacts under `.dicoimpro/runs/<run_id>/` and does not call GPT,
Codex, gh, git, pytest, network, or merge by default.

## 8. Explicit API Boundary

API requires --execute-api. GPT calls are allowed only through the existing
`scripts/coach_step.py` boundary and only when explicitly authorized for the
run.

No OpenAI runtime inside the dicoimpro application is authorized.

## 9. Manual Codex Handoff Boundary

Codex execution remains manual handoff. Repository scripts may prepare a handoff
packet and archive a manually supplied Codex return, but they do not execute
Codex SDK, Codex CLI, or automatic Codex execution.

## 10. PR Verification Boundary

PR verification remains under the existing `scripts/coach_pr_verify.py`
boundary. Verification builds a local `pre_merge_report`, evaluates the
autonomy policy, and records local evidence.

## 11. Optional Guarded Merge Boundary

Merge is never default. Auto-merge requires --execute-merge plus merge_mode
auto_after_verify plus verify gate success.

The optional guarded merge command is dangerous unless the verify gate is green.
It must not be used casually. It must be used only when the user explicitly
wants guarded auto-merge.

## 12. Stop-Human Doctrine

Unknown risk means stop_human. Human stop remains required for unresolved
objective, unresolved scope, invalid notes, invalid Codex returns, missing PR
evidence, failed tests, failed diff-check, failed CI, blocking reviews,
contradictions, secrets, forbidden files, budget excess, or any unclassified
risk.

## 13. Diagnostics And Runbook Status

Codex 042 added local-only diagnostics and the operational runbook:

```text
python scripts/coach_loop.py doctor
python scripts/coach_loop.py validate-run --run-id <run_id>
python scripts/coach_loop.py explain-next --run-id <run_id>
```

Diagnostics do not call GPT, OpenAI, Codex, gh, git, pytest, network, or merge.
They do not weaken stop_human.

## 14. Guardrail Audit

The coach-loop block authorizes no RUN/journal/JournalPatch/real data/src
runtime behavior. It authorizes no old PDF usage and no publication.
It authorizes no src runtime behavior change.

It also authorizes no source discovery, candidate selection, or dictionary entry
processing.

## 15. Forbidden Scopes

The frozen block does not authorize:

- `src/` runtime behavior change;
- scripts changes from Codex 043;
- package behavior change;
- OpenAI/GPT calls without explicit API authorization;
- Codex SDK or Codex CLI execution;
- automatic Codex execution;
- unbounded autonomous loop;
- gh/git/pytest execution from repository diagnostics;
- real merge outside the existing guarded merge boundary;
- RUN artifacts;
- real entry processing;
- source discovery;
- candidate selection;
- active journal read/write;
- JournalPatch application;
- XLSX/CSV export;
- old PDF usage;
- publication.

## 16. Final Usage Checklist

Use this checklist in order:

```text
python scripts/coach_loop.py doctor
python scripts/coach_loop.py start --run-id <run_id> --stage pre_cadrage
python scripts/coach_loop.py validate-run --run-id <run_id>
python scripts/coach_loop.py explain-next --run-id <run_id>
python scripts/coach_loop.py start --run-id <run_id> --stage pre_cadrage --execute-api --user-instruction "..."
python scripts/coach_loop.py resume-codex --run-id <run_id> --return-path <path>
python scripts/coach_loop.py verify-pr --run-id <run_id> --merge-mode manual
python scripts/coach_loop.py verify-pr --run-id <run_id> --merge-mode auto_after_verify --execute-merge
```

The last command is optional and dangerous unless the verify gate is green. It
must not be used casually. It must be used only when the user explicitly wants
guarded auto-merge.

## 17. Remaining Optional Work

The remaining work is optional, not blocker:

- real controlled end-to-end test on a harmless docs PR;
- ergonomics improvements if usage shows friction;
- richer cost accounting;
- CI integration if desired;
- later production integration only after separate decision.

These items are not blockers for the coach-loop block freeze.

## 18. Freeze Verdict

Codex 043 freezes the coach-loop development block after final docs/tests audit.
The block is coherent from Codex 035 through Codex 042 and ready for controlled
local usage after merge if tests pass.

The freeze adds no runtime feature and no script change. API, Codex handoff, PR
verification, optional guarded merge, diagnostics, and stop_human boundaries
remain unchanged.
