from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from dico_impro.contracts import AgentResult, ValidationStatus


class QualityGateClassification(StrEnum):
    RECOVERABLE = "recoverable"
    BLOCKING = "blocking"
    PRUDENCE = "prudence"
    OK = "ok"


@dataclass(frozen=True)
class QualityGateResult:
    classification: QualityGateClassification
    reasons: tuple[str, ...] = ()

    @property
    def is_ok(self) -> bool:
        return self.classification == QualityGateClassification.OK


RECOVERABLE_ERROR_TYPES = frozenset({"schema_invalid", "non_parseable_output"})
BLOCKING_ERROR_TYPES = frozenset(
    {"protocol_violation", "source_confusion", "publication_blocking"}
)
PRUDENCE_ERROR_TYPES = frozenset({"run_002_required", "warning"})


def evaluate_agent_result(result: AgentResult) -> QualityGateResult:
    payload = result.payload
    reasons: list[str] = []

    if payload.get("object_type") is None:
        reasons.append("payload missing object_type")
    if payload.get("schema_version") is None:
        reasons.append("payload missing schema_version")
    if reasons:
        return QualityGateResult(QualityGateClassification.BLOCKING, tuple(reasons))

    error_type = payload.get("error_type")
    if error_type in BLOCKING_ERROR_TYPES:
        return QualityGateResult(QualityGateClassification.BLOCKING, (str(error_type),))
    if error_type in RECOVERABLE_ERROR_TYPES:
        return QualityGateResult(QualityGateClassification.RECOVERABLE, (str(error_type),))
    if error_type in PRUDENCE_ERROR_TYPES:
        return QualityGateResult(QualityGateClassification.PRUDENCE, (str(error_type),))

    if result.validation_status == ValidationStatus.SCHEMA_INVALID:
        return QualityGateResult(QualityGateClassification.RECOVERABLE, ("schema_invalid",))
    if result.validation_status == ValidationStatus.NON_PUBLIABLE_EN_L_ETAT:
        return QualityGateResult(QualityGateClassification.BLOCKING, ("publication_blocked",))
    if result.validation_status == ValidationStatus.RUN_002_AUTO_REQUIS:
        return QualityGateResult(QualityGateClassification.PRUDENCE, ("run_002_required",))
    if result.validation_status == ValidationStatus.AUDIT_HUMAIN_REQUIS:
        return QualityGateResult(QualityGateClassification.PRUDENCE, ("audit_required",))
    if result.warnings or result.audit_notes:
        return QualityGateResult(QualityGateClassification.PRUDENCE, ("warnings_or_audit_notes",))

    return QualityGateResult(QualityGateClassification.OK)


def classify_agent_result(result: AgentResult) -> QualityGateClassification:
    return evaluate_agent_result(result).classification


__all__ = [
    "QualityGateClassification",
    "QualityGateResult",
    "classify_agent_result",
    "evaluate_agent_result",
]
