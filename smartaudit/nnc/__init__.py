"""Narrative-Number Consistency — đối chiếu ngôn từ với số liệu."""

from smartaudit.nnc.checker import (
    Evidence,
    NNCResult,
    Verdict,
    build_facts,
    check_claim,
    check_report,
)

__all__ = [
    "Evidence",
    "NNCResult",
    "Verdict",
    "build_facts",
    "check_claim",
    "check_report",
]
