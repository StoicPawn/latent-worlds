"""Audit the scientific provenance of CIVITAS ZERO's theory-first programme.

Checks the 14 original indicator IDs, scientific-literature provenance,
theoretical dependencies, and lack of fabricated consciousness results.
Generates a readable Markdown indicator matrix from versioned JSON.

This tool checks *reporting integrity*, NOT the truth of scientific
theories, the accuracy of publication metadata or AI consciousness.
No external network, API keys or large scientific packages required.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
EXPECTED = (
    "RPT-1", "RPT-2",
    "GWT-1", "GWT-2", "GWT-3", "GWT-4",
    "HOT-1", "HOT-2", "HOT-3", "HOT-4",
    "AST-1", "PP-1", "AE-1", "AE-2",
)
FAMILIES = {
    "RPT": "Recurrent Processing",
    "GWT": "Global Workspace",
    "HOT": "Higher-Order / Metacognitive",
    "AST": "Attention Schema",
    "PP": "Predictive Processing",
    "AE": "Agency / Embodiment",
}
ASSAYS = {"C1", "C2", "C3"}


class ResearchIntegrityError(ValueError):
    """A paper-facing research claim fails the frozen evidence rules."""


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(indicators: dict, bibliography: dict, programmes: dict) -> dict:
    """Statically verify that no speculative indicator is reported as proven."""
    rows = indicators["indicators"]
    ids = [x["id"] for x in rows]
    if tuple(ids) != EXPECTED:
        raise ResearchIntegrityError("Exactly 14 theory-derived IDs in original order required")
    if len(ids) != len(set(ids)):
        raise ResearchIntegrityError("Duplicate theory indicator")

    papers = bibliography["entries"]
    refs = [p["id"] for p in papers]
    if len(refs) < 12 or len(refs) != len(set(refs)):
        raise ResearchIntegrityError("Incomplete or duplicate primary-source ledger")
    if bibliography["updated_on"] != indicators["date"]:
        raise ResearchIntegrityError("Literature/indicator review dates diverged")
    if "butlin2026" not in refs or "butlin2023" not in refs:
        raise ResearchIntegrityError("Missing provenance of canonical indicators")
    for p in papers:
        if not re.fullmatch(r"20\d\d(?:-\d\d(?:-\d\d)?)?", str(p["online_date"])):
            raise ResearchIntegrityError(f"Invalid source date: {p['id']}")
        if not str(p["url"]).startswith(("https://doi.org/", "https://arxiv.org/",
                                         "https://escholarship.org/")):
            raise ResearchIntegrityError(f"Unverifiable source URL form: {p['id']}")
        if not p["lesson"] or not p["status"] or not p["title"]:
            raise ResearchIntegrityError(f"Uninterpretable evidence item: {p['id']}")

    if indicators["main_source_id"] != "butlin2026":
        raise ResearchIntegrityError("Canonical indicator provenance was changed")
    for row in rows:
        if row["id"].split("-")[0] != row["theory"] or row["theory"] not in FAMILIES:
            raise ResearchIntegrityError(f"Indicator family mismatch {row['id']}")
        if row["status"] != "NOT_ASSESSED":
            raise ResearchIntegrityError(
                f"No consciousness indicator has been experimentally assessed: {row['id']}"
            )
        if row["can_infer_phenomenal_consciousness"] is not False:
            raise ResearchIntegrityError(f"Unsupported phenomenal claim: {row['id']}")
        if not row["minimal_counterexample"] or not row["computational_paraphrase"]:
            raise ResearchIntegrityError(f"Missing specificity challenge: {row['id']}")
        if not set(row["candidate_assays"]) <= ASSAYS:
            raise ResearchIntegrityError(f"Noncanonical test suite in {row['id']}")
        deps = row["dependencies_to_consider"]
        if row["id"] in deps or len(deps) != len(set(deps)) or any(d not in ids for d in deps):
            raise ResearchIntegrityError(f"Invalid dependency caution: {row['id']}")

    if programmes["phenomenal_consciousness_demonstrated"] is not False:
        raise ResearchIntegrityError("Unsubstantiated phenomenality report")
    if {v["id"] for v in programmes["indicators"]} != ASSAYS:
        raise ResearchIntegrityError("Engineering suites changed unexpectedly")
    if any(v["status"] != "UNTESTED" for v in programmes["indicators"]):
        raise ResearchIntegrityError("Unrun engineering suites labelled tested")
    valid_refs = set(ids)
    for suite in programmes["indicators"]:
        if not set(suite["canonical_refs"]) <= valid_refs:
            raise ResearchIntegrityError(f"Unrecognized canonical refs in {suite['id']}")
    expected_refs = {
        "C1": {"HOT-2", "HOT-3", "AE-2"},
        "C2": {"GWT-2", "GWT-3", "GWT-4", "RPT-1"},
        "C3": {"HOT-2", "HOT-3", "AST-1", "PP-1"},
    }
    for suite in programmes["indicators"]:
        if set(suite["canonical_refs"]) != expected_refs[suite["id"]]:
            raise ResearchIntegrityError(f"Unreviewed theory-to-assay mapping: {suite['id']}")

    return {
        "source_count": len(refs),
        "theory_count": len(FAMILIES),
        "original_indicator_count": len(ids),
        "assessed_indicators": sum(r["status"] != "NOT_ASSESSED" for r in rows),
        "demonstrated_phenomenal_consciousness": False,
        "research_cutoff": indicators["date"],
    }


def _esc(s: str) -> str:
    return str(s).replace("|", "/").replace("\n", " ")


def render(indicators: dict, bibliography: dict) -> str:
    """Generate deterministic GitHub Markdown; no manual status editing."""
    texts = [
        "# Theory-derived indicators relevant to AI consciousness",
        "",
        f"**Literature verified through {indicators['date']}.**",
        "Canonical IDs come from Butlin et al. (2023, 2026), not CIVITAS ZERO.",
        "The following are engineering **paraphrases** and example falsifying",
        "countermodels, not validated sufficient conditions for experience.",
        "",
        "All indicators are **NOT ASSESSED**. C1, C2 and C3 are our own experimental",
        "assay groupings; they are *not* Butlin's official indicator categories.",
        "Indicators overlap and can have dependencies; summing passes would be misleading.",
        "",
        f"Main source: [Butlin et al. 2026]({_esc(next(p['url'] for p in bibliography['entries'] if p['id']=='butlin2026'))})",
        "",
    ]
    for theory, family in FAMILIES.items():
        texts.extend([
            f"## {family} ({theory})",
            "",
            "| ID | Engineering interpretation | Naive false-positive mechanism | Proposed assay | Status |",
            "|:--|:--|:--|:--|:--|",
        ])
        for r in indicators["indicators"]:
            if r["theory"] != theory:
                continue
            tests = ", ".join(r["candidate_assays"]) or "No experiment proposed"
            texts.append(
                f"| **{r['id']}** | {_esc(r['computational_paraphrase'])} | "
                f"{_esc(r['minimal_counterexample'])} | {_esc(tests)} | "
                f"{r['status']} |"
            )
        texts.append("")
    texts += [
        "## Theory-to-engineering dependencies (caution, not a proof)",
        "",
        "Butlin et al. describe overlapping conditions (including GWT-3/4 and",
        "RPT-1); dependencies are not statistically independent 'votes'.",
        "",
    ]
    for r in indicators["indicators"]:
        if r["dependencies_to_consider"]:
            texts.append(f"- **{r['id']}**: consider {', '.join(r['dependencies_to_consider'])}.")
    texts += [
        "",
        "## Methods and interpretation",
        "",
        "See [critical review](REVIEW_2026-10-31.md),",
        "[adversarial predictions](THEORY_ADJUDICATION.md) and",
        "[source ledger](SOURCES.json). Functional computation may shift",
        "credences under a theory but cannot establish substrate-independent",
        "phenomenal consciousness or justify a numeric 'proto-consciousness score'.",
        "",
        "**No C1/C2/C3 experiments have been run.** Historical population and",
        "foraging results are *not* consciousness-indicator evidence.",
        "",
    ]
    return "\n".join(texts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="Require generated Markdown to match checked-in file")
    args = ap.parse_args()
    indicators = _read(BASE / "BUTLIN_INDICATORS.json")
    refs = _read(BASE / "SOURCES.json")
    programmes = _read(BASE.parent / "paper/INDICATOR_MATRIX.json")
    result = check(indicators, refs, programmes)
    output = BASE / "INDICATOR_MATRIX.md"
    rendered = render(indicators, refs)
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            raise ResearchIntegrityError(
                "Indicator matrix inconsistent: regenerate and commit it"
            )
    else:
        output.write_text(rendered, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
