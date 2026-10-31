"""Scientific-reporting regression checks for consciousness theory review.

These are *formal provenance checks*, NOT validation of a consciousness
indicator, biological transfer or any experiment on subjective experience.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "experiments/civitas_zero/literature"
SCRIPT = LIT / "audit.py"
spec = importlib.util.spec_from_file_location("civitas_literature_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def load():
    ind = json.loads((LIT / "BUTLIN_INDICATORS.json").read_text())
    refs = json.loads((LIT / "SOURCES.json").read_text())
    suites = json.loads(
        (LIT.parent / "paper/INDICATOR_MATRIX.json").read_text())
    return ind, refs, suites


def test_canonical_theory_labels_are_complete_and_evidence_not_claimed():
    i, r, s = load()
    result = audit.check(i, r, s)
    assert result["original_indicator_count"] == 14
    assert result["source_count"] >= 15
    assert result["theory_count"] == 6
    assert result["assessed_indicators"] == 0
    assert result["demonstrated_phenomenal_consciousness"] is False
    assert i["date"] == "2026-10-31"
    assert [x["id"] for x in i["indicators"]] == list(audit.EXPECTED)


def test_generated_readable_indicators_match_the_literature_source():
    i, r, _ = load()
    rendered = audit.render(i, r)
    assert (LIT / "INDICATOR_MATRIX.md").read_text() == rendered
    for name in audit.EXPECTED:
        assert f"**{name}**" in rendered
    assert "No C1/C2/C3 experiments have been run" in rendered


@pytest.mark.parametrize("mutation", ["missing", "claimed_conscious", "unvalidated_pass",
                                        "bad_dependency", "no_theory"])
def test_adversarial_claim_mutations_fail(mutation):
    i, r, s = load()
    if mutation == "missing":
        i["indicators"].pop()
    elif mutation == "claimed_conscious":
        s["phenomenal_consciousness_demonstrated"] = True
    elif mutation == "unvalidated_pass":
        i["indicators"][0]["status"] = "CONFIRMED"
    elif mutation == "bad_dependency":
        i["indicators"][0]["dependencies_to_consider"] = ["GWT-999"]
    elif mutation == "no_theory":
        s["indicators"][0]["canonical_refs"] = ["FREESTYLE-1"]
    with pytest.raises(audit.ResearchIntegrityError):
        audit.check(i, r, s)


def test_no_single_model_or_assay_claims_phenomenal_sufficiency():
    i, r, s = load()
    assert all(x["can_infer_phenomenal_consciousness"] is False
               for x in i["indicators"])
    assert all(x["status"] == "NOT_ASSESSED" for x in i["indicators"])
    assert all(x["status"] == "UNTESTED" for x in s["indicators"])
    assert not s["phenomenal_consciousness_demonstrated"]
    paper = (LIT.parent / "paper/CONSCIOUSNESS_RESEARCH_PROGRAM.md").read_text()
    assert "C0" in paper
    assert "14" in paper
    assert "C1/C2/C3" in paper
    assert "not" in paper.lower()
