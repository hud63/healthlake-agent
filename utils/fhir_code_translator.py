"""FHIR code to human-readable text.

Clinical FHIR resources are full of coded values (SNOMED, LOINC, RxNorm, ICD-10). This pass walks a
resource or bundle and annotates each Coding with a readable display, so the model and the user see
meaning instead of codes.

The lookup here is a small illustrative map. Back it with a real terminology source (a LOINC or
SNOMED service, or a FHIR ValueSet $expand) for production breadth.
"""
from __future__ import annotations

from typing import Any

# Illustrative only, not a clinical reference.
_CODE_MAP: dict[str, dict[str, str]] = {
    "http://loinc.org": {
        "8867-4": "Heart rate",
        "8480-6": "Systolic blood pressure",
        "8462-4": "Diastolic blood pressure",
    },
    "http://snomed.info/sct": {
        "38341003": "Hypertension",
    },
}


def translate_code(system: str, code: str) -> str:
    """Return a readable label for (system, code), or the raw code when unknown."""
    return _CODE_MAP.get(system, {}).get(code, code)


def translate(node: Any) -> Any:
    """Recursively annotate Coding entries with a `_display` derived from the code map."""
    if isinstance(node, dict):
        if "system" in node and "code" in node and "display" not in node:
            node["_display"] = translate_code(node["system"], node["code"])
        return {k: translate(v) for k, v in node.items()}
    if isinstance(node, list):
        return [translate(item) for item in node]
    return node
