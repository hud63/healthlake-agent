"""FHIR code -> human-readable text.

Clinical FHIR resources are full of coded values (SNOMED, LOINC, RxNorm, ICD-10). This helper turns
them into readable text so the LLM and the end user see meaning, not codes.

Skeleton: a tiny illustrative map + passthrough. TODO: back this with a real terminology source
(e.g. a LOINC/SNOMED lookup or a FHIR ValueSet/$expand) rather than a hardcoded dict.
"""
from __future__ import annotations

from typing import Any

# Illustrative only — NOT a clinical reference.
_DEMO_CODE_MAP: dict[str, dict[str, str]] = {
    "http://loinc.org": {
        "8867-4": "Heart rate",
        "8480-6": "Systolic blood pressure",
    },
}


def translate_code(system: str, code: str) -> str:
    """Return a readable label for (system, code), or the raw code if unknown."""
    return _DEMO_CODE_MAP.get(system, {}).get(code, code)


def translate(resource: dict[str, Any]) -> dict[str, Any]:
    """Walk a FHIR resource and annotate codings with readable text.

    TODO: recurse into CodeableConcept/Coding nodes and attach `_display`. This stub returns the
    resource unchanged.
    """
    return resource
