# Prompt activation protocol v0.2.3-auto

Status: protocol-only gate created by Codex 022.

This document defines how future real prompt documents may later be introduced,
reviewed, versioned and approved. It does not create any real prompt body, does
not render or load prompts, does not activate OpenAI, and does not change any
runtime path.

## 1. Current state

```text
- no real prompt exists yet ;
- PromptPackage fixtures remain metadata-only and disabled ;
- OpenAIAdapter remains disconnected from prompt content ;
- CLI dry-run remains fake-only ;
- authorized runtime paths remain unchanged after Codex 022.
```

## 2. Prompt lifecycle statuses

Every future prompt document must use exactly one lifecycle status:

```text
not_created
draft_documented
human_review_required
approved_for_mock_only
approved_for_real_openai_later
retired
```

Status meanings:

```text
not_created - no prompt body has been written.
draft_documented - a draft prompt document exists but has no runtime approval.
human_review_required - a draft exists and must be reviewed before any mock use.
approved_for_mock_only - human approval allows mock-only review or tests, not real OpenAI.
approved_for_real_openai_later - human approval records intent for a later real
OpenAI mission, but does not activate runtime use by itself.
retired - the prompt must not be used for new work.
```

## 3. Activation rules

These rules are mandatory for every future prompt until a later explicit mission
changes them:

```text
- no prompt is active by default ;
- no prompt may be consumed by OpenAIAdapter yet ;
- no prompt may be consumed by CLI dry-run ;
- no prompt may trigger real OpenAI ;
- no prompt may access data/local_files ;
- no prompt may access the active journal ;
- no prompt may use the old PDF ;
- no prompt may process real project entries ;
- no prompt may launch RUN ;
- no prompt may perform candidate selection ;
- no prompt may write JournalPatch ;
- no prompt may create XLSX/CSV exports.
```

The status `approved_for_real_openai_later` is not runtime activation. It is only
a documented approval state for a future separately approved integration mission.

## 4. Human review requirements

Every future real prompt document must include a human-readable review note and
must state all of the following before it can leave `draft_documented`:

```text
- agent target ;
- input contract ;
- expected output contract ;
- forbidden context ;
- known risks ;
- disabled-by-default state ;
- reviewer identity or review record reference ;
- review date ;
- lifecycle status.
```

Every future prompt remains disabled until explicitly approved. Human review may
approve only the documented status transition being requested.

## 5. First future prompt candidate

The preferred first future prompt candidate is `RoutingAgent`.

Reason: `RoutingAgent` is the narrowest initial target because it should operate
against a small structured routing decision contract before broader
classification or source-audit behavior. `ClassificationAgent` remains higher
risk because it is closer to final classification semantics and should wait
until routing review proves the protocol.

No `RoutingAgent` prompt body is written by Codex 022. The first prompt must be
mock-only and review-only before any future real OpenAI call is considered.

## 6. Storage policy

Future prompt drafts should live under:

```text
docs/prompts/drafts/
```

This directory is for future human-readable prompt draft documents only. Codex
022 does not create any prompt draft in that directory.

Storage restrictions:

```text
- src/dico_impro/agents/prompts.py is forbidden ;
- inline prompt fields inside PromptPackage JSON fixtures are forbidden ;
- PromptPackage JSON fixtures must remain metadata-only and disabled ;
- prompt_body_ref is a reference only, not prompt content ;
- prompt_body_ref must not cause runtime loading, rendering or consumption.
```

Prompt draft documents must be versioned as documents. A future prompt draft file
name must include the agent target and a stable version marker, for example a
future document path shaped like:

```text
docs/prompts/drafts/RoutingAgent_v0.review.md
```

That example path is a naming convention only. It is not created by Codex 022.

## 7. Runtime policy

Real prompts may exist as documents later, but they must not be imported, loaded,
rendered or consumed by runtime until a future explicit mission approves the
runtime connection and adds tests for that connection.

Current authorized runtime paths remain unchanged after Codex 022:

```text
1. fake CLI dry-run ;
2. mock OpenAI planning via injected client only ;
3. metadata-only PromptPackage validation.
```

The runtime must remain free of:

```text
- real OpenAI calls ;
- network calls ;
- prompt loading or rendering ;
- CLI prompt consumption ;
- old PDF usage ;
- real project data or real entry processing ;
- data/local_files access ;
- active journal access ;
- RUN ;
- candidate selection ;
- JournalPatch application ;
- XLSX/CSV export creation ;
- SourceDiscoveryAgent activation.
```

## 8. Required future activation mission

Any later mission that wants to move beyond this protocol must be explicit and
must include all of the following:

```text
- the exact prompt document path ;
- the lifecycle status transition requested ;
- the agent target ;
- the input and output contracts ;
- human review evidence ;
- tests proving disabled-by-default behavior ;
- tests proving CLI dry-run cannot consume the prompt ;
- tests proving OpenAIAdapter cannot consume the prompt unless explicitly wired ;
- tests proving no real OpenAI or network call occurs by default ;
- tests proving no data/local_files, active journal, RUN, candidate selection,
  JournalPatch, SourceDiscoveryAgent or XLSX/CSV path is introduced.
```
