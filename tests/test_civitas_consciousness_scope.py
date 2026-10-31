"""Evidence-scope guards for the AI consciousness research programme.

These are *documentation/provenance* consistency checks, not experiments
that establish consciousness or that validate the proposed scientific
indicators.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "civitas_zero"
PAPER = BASE / "paper"


def test_indicator_registry_is_theory_derived_and_unrun():
    data = json.loads((PAPER / "INDICATOR_MATRIX.json").read_text())
    assert data["research_field"].startswith("AI consciousness")
    assert data["phenomenal_consciousness_demonstrated"] is False
    assert [x["id"] for x in data["indicators"]] == ["C1", "C2", "C3"]
    assert all(x["status"] == "UNTESTED" for x in data["indicators"])
    for indicator in data["indicators"]:
        assert indicator["theoretical_relevance"]
        assert indicator["primary_test"]
        assert indicator["controls"]
        assert "phenomenal consciousness" in indicator["not_sufficient_for"]


def test_legacy_ecology_results_are_not_relabelled_consciousness():
    data = json.loads((PAPER / "INDICATOR_MATRIX.json").read_text())
    legacy = {x["id"]: x for x in data["historic_results"]}
    assert legacy["v5.4"]["status"] == "FAILED_CONFIRMATION"
    assert legacy["v5.5"]["status"] == "EXPLORATORY"
    assert all("NOT consciousness data" in x["role"] for x in legacy.values())


def test_primary_documents_are_linked_and_do_not_claim_discovery():
    readme = (BASE / "README.md").read_text()
    target = (PAPER / "CONSCIOUSNESS_RESEARCH_PROGRAM.md").read_text()
    draft = (PAPER / "CONSCIOUSNESS_PAPER_DRAFT.md").read_text()
    for f in ("CONSCIOUSNESS_RESEARCH_PROGRAM.md", "CONSCIOUSNESS_PAPER_DRAFT.md",
              "INDICATOR_MATRIX.json"):
        assert f in readme and (PAPER / f).is_file()
    assert "C1" in target and "C2" in target and "C3" in target
    assert "UNTESTED" in target
    assert "no consciousness evidence yet" in target.lower()
    assert "not submission-ready" in draft.lower()
    assert "results do not exist" in readme.lower()
