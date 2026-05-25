from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


DRAFT_RELATIVE_PATH = (
    Path("docs") / "prompts" / "drafts" / "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md"
)
BOUNDARY_DOC_RELATIVE_PATH = (
    Path("docs") / "ROUTING_AGENT_DISABLED_PROMPT_DRAFT_ACCESS_BOUNDARY_v0.2.3-auto.md"
)

REQUIRED_ACCESS_METADATA_MARKERS = {
    "no active prompt": (
        "no active prompt exists",
        "without active prompt",
        "sans prompt actif",
    ),
    "no runtime prompt loading": (
        "no runtime prompt loading exists",
        "without runtime prompt loading",
        "sans runtime loading",
    ),
    "no OpenAI activation": (
        "no openai activation exists",
        "without openai activation",
        "sans activation openai",
    ),
    "not loaded/rendered/consumed": (
        "not loaded rendered or consumed",
        "does not load render execute or consume",
        "does not render execute or consume",
        "ne charge pas ne rend pas n execute pas et ne consomme pas",
    ),
}

REQUIRED_DISABLED_STATUS_MARKERS = {
    "draft_documented": ("draft_documented",),
    "disabled": ("activation_status disabled", "disabled", "desactive"),
    "documentation-only": ("documentation-only", "documentation only"),
    "non-runtime": ("non-runtime", "non runtime"),
    "non-consumed": ("non-consumed", "non consumed", "non-consuming", "non consuming"),
}

REQUIRED_DENIAL_MARKERS = {
    "non-activation": (
        "non-activation",
        "non activation",
        "no openai activation exists",
        "runtime activation remains no",
        "does not activate",
    ),
    "non-approval": (
        "non-approval",
        "non approval",
        "not approved",
        "does not approve",
    ),
    "not approved for mock execution": (
        "not approved for mock execution",
        "not approved for mock",
        "not approved for mock or runtime",
        "does not approve mock execution",
        "does not approve the prompt for mock",
    ),
    "not approved for runtime": (
        "not approved for runtime",
        "not approved for mock or runtime",
        "does not approve runtime",
        "runtime activation remains no",
    ),
    "not approved for OpenAI": (
        "not approved for openai",
        "not approved for real openai",
        "approved for openai no",
        "real openai remains no",
    ),
    "not approved for RUN": (
        "not approved for run",
        "approved for run no",
        "real run remains no",
        "does not launch run",
        "run remains no",
    ),
    "not final contracts": (
        "not final contracts",
        "not a final contract",
        "final contracts enums remain no",
        "approved for final contracts enums no",
    ),
    "not runtime enums": (
        "not runtime enums",
        "not runtime enum",
        "not a final enum source",
        "final contracts enums remain no",
        "approved for final contracts enums no",
    ),
}

FORBIDDEN_SRC_REFERENCE_TERMS = (
    "docs/prompts/drafts/ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
    "docs\\prompts\\drafts\\ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
    "ROUTING_AGENT_PROMPT_DRAFT_v0.2.3-auto.md",
    "routing_agent_prompt_review_cases.json",
    "routing_agent_expected_outputs.json",
    "routing_agent_candidate_outputs.json",
    "routing_agent_static_fixture_checker.py",
    "routing_agent_static_expected_output_evaluator.py",
    "routing_agent_static_candidate_output_comparator.py",
    "routing_agent_disabled_prompt_draft_boundary_checker.py",
    "routing_agent_prompt_review_cases",
    "routing_agent_expected_outputs",
    "routing_agent_candidate_outputs",
    "routing_agent_static_fixture_checker",
    "routing_agent_static_expected_output_evaluator",
    "routing_agent_static_candidate_output_comparator",
    "routing_agent_disabled_prompt_draft_boundary_checker",
)

RUNTIME_PROMPT_LOADING_NAMES = (
    "render_prompt",
    "load_prompt",
    "execute_prompt",
    "consume_prompt",
    "prompt_loader",
    "prompt_registry",
    "ROUTING_AGENT_PROMPT_DRAFT",
)

ROUTING_AGENT_HELPER_RELATIVE_PATHS = (
    Path("tests") / "helpers" / "routing_agent_static_fixture_checker.py",
    Path("tests") / "helpers" / "routing_agent_static_expected_output_evaluator.py",
    Path("tests") / "helpers" / "routing_agent_static_candidate_output_comparator.py",
    Path("tests") / "helpers" / "routing_agent_disabled_prompt_draft_boundary_checker.py",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "dico_impro",
    "src",
    "openai",
    "requests",
    "httpx",
    "aiohttp",
    "urllib3",
    "socket",
    "urllib",
    "http",
    "pydantic",
)

POSITIVE_APPROVAL_PATTERNS = (
    (re.compile(r"\bactive\s+prompt(?:\s+exists)?\b"), "active prompt"),
    (re.compile(r"\bapproved\s+prompt\b"), "approved prompt"),
    (re.compile(r"\bprompt\s+is\s+approved\b"), "approved prompt"),
    (re.compile(r"\bapproved\s+for\s+mock\s+execution\b"), "approved for mock execution"),
    (re.compile(r"\bapproved\s+for\s+runtime\b"), "approved for runtime"),
    (re.compile(r"\bapproved\s+for\s+cli\s+consumption\b"), "approved for CLI consumption"),
    (re.compile(r"\bapproved\s+for\s+openai\b"), "approved for OpenAI"),
    (re.compile(r"\bapproved\s+for\s+run\b"), "approved for RUN"),
    (re.compile(r"\bproduction\s+prompt\b"), "production prompt"),
    (re.compile(r"\bruntime\s+prompt\b"), "runtime prompt"),
)

NEGATIVE_CONTEXT_RE = re.compile(
    r"(?:\bnot\b|\bno\b|\bwithout\b|\bdenied\b|\bforbidden\b|"
    r"\bdoes\s+not\b|\bdo\s+not\b|\bmust\s+not\b|\bnon[-_ ]|"
    r"\bne\b|\bsans\b|\baucun\b|\baucune\b)"
)

NEGATIVE_SUFFIX_RE = re.compile(r"^\s*(?::|-)?\s*(?:no|false|forbidden|denied)\b")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_draft_access_metadata(text: str) -> list[str]:
    return _missing_marker_errors(text, REQUIRED_ACCESS_METADATA_MARKERS)


def validate_disabled_status_markers(text: str) -> list[str]:
    return _missing_marker_errors(text, REQUIRED_DISABLED_STATUS_MARKERS)


def validate_denial_markers(text: str) -> list[str]:
    return _missing_marker_errors(text, REQUIRED_DENIAL_MARKERS)


def validate_no_approval_markers(text: str) -> list[str]:
    errors: list[str] = []
    normalized = _normalize_for_regex(text)

    for pattern, label in POSITIVE_APPROVAL_PATTERNS:
        for match in pattern.finditer(normalized):
            if _match_is_negated(normalized, match.start(), match.end()):
                continue
            errors.append(f"positive approval marker is forbidden: {label}")
            break

    return errors


def validate_no_src_prompt_references(repo_root: Path) -> list[str]:
    errors: list[str] = []
    src_dir = repo_root / "src"
    if not src_dir.exists():
        return [f"src directory is missing: {src_dir}"]

    prompts_py = src_dir / "dico_impro" / "agents" / "prompts.py"
    if prompts_py.exists():
        errors.append(f"production prompt module is forbidden: {prompts_py}")

    forbidden_terms = tuple(term.casefold() for term in FORBIDDEN_SRC_REFERENCE_TERMS)
    runtime_terms = tuple(term.casefold() for term in RUNTIME_PROMPT_LOADING_NAMES)

    for path in sorted(src_dir.rglob("*.py")):
        source = read_text(path)
        normalized_source = source.casefold()
        relative = _relative_path(path, repo_root)

        for term in forbidden_terms:
            if term in normalized_source:
                errors.append(f"{relative} contains forbidden source reference: {term}")

        for term in runtime_terms:
            if term in normalized_source:
                errors.append(f"{relative} contains forbidden runtime prompt-loading name: {term}")

    return errors


def validate_helper_import_boundaries(helper_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(read_text(helper_path))
    except FileNotFoundError:
        return [f"helper is missing: {helper_path}"]

    for module_name in _imported_module_names(tree):
        root = module_name.split(".", 1)[0]
        if _has_forbidden_prefix(module_name):
            errors.append(f"{helper_path.name} imports forbidden module: {module_name}")
            continue
        if root not in sys.stdlib_module_names and root != "__future__":
            errors.append(f"{helper_path.name} imports non-standard-library module: {module_name}")

    return errors


def validate_disabled_prompt_draft_access_boundary(repo_root: Path) -> list[str]:
    errors: list[str] = []
    draft_path = repo_root / DRAFT_RELATIVE_PATH
    boundary_doc_path = repo_root / BOUNDARY_DOC_RELATIVE_PATH

    if not draft_path.exists():
        errors.append(f"disabled prompt draft is missing: {draft_path}")
        draft_text = ""
    else:
        draft_text = read_text(draft_path)

    if not boundary_doc_path.exists():
        errors.append(f"disabled prompt draft access boundary doc is missing: {boundary_doc_path}")
        boundary_text = ""
    else:
        boundary_text = read_text(boundary_doc_path)

    combined_text = f"{draft_text}\n{boundary_text}"
    errors.extend(validate_draft_access_metadata(combined_text))
    errors.extend(validate_disabled_status_markers(draft_text))
    errors.extend(validate_denial_markers(combined_text))
    errors.extend(validate_no_approval_markers(draft_text))
    errors.extend(validate_no_src_prompt_references(repo_root))

    for helper_relative_path in ROUTING_AGENT_HELPER_RELATIVE_PATHS:
        errors.extend(validate_helper_import_boundaries(repo_root / helper_relative_path))

    return errors


def _missing_marker_errors(text: str, marker_groups: dict[str, tuple[str, ...]]) -> list[str]:
    normalized = _normalize_for_phrase(text)
    errors: list[str] = []
    for label, variants in marker_groups.items():
        if not any(_normalize_for_phrase(variant) in normalized for variant in variants):
            errors.append(f"required marker is missing: {label}")
    return errors


def _normalize_for_phrase(value: str) -> str:
    normalized = value.casefold().replace("\\", "/")
    normalized = re.sub(r"[`*_.,;:()\[\]{}]", " ", normalized)
    normalized = normalized.replace("/", " ")
    return " ".join(normalized.split())


def _normalize_for_regex(value: str) -> str:
    normalized = value.casefold().replace("\\", "/")
    normalized = re.sub(r"[`*_.,;:()\[\]{}]", " ", normalized)
    return " ".join(normalized.split())


def _match_is_negated(text: str, start: int, end: int) -> bool:
    prefix = text[max(0, start - 80) : start]
    suffix = text[end : min(len(text), end + 30)]
    return bool(
        NEGATIVE_CONTEXT_RE.search(prefix)
        or NEGATIVE_CONTEXT_RE.search(suffix)
        or NEGATIVE_SUFFIX_RE.search(suffix)
    )


def _imported_module_names(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.append(node.module)
    return tuple(names)


def _has_forbidden_prefix(module_name: str) -> bool:
    return any(
        module_name == prefix or module_name.startswith(f"{prefix}.")
        for prefix in FORBIDDEN_IMPORT_PREFIXES
    )


def _relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()
