"""Audit and visualize frozen CIVITAS ZERO v5.4 results.

No model training; all reported numbers are recomputed from the 16 archived
per-seed JSON outputs. Bootstrap CIs are descriptive, not new confirmatory
hypothesis tests, because the experiment already has a preregistered gate.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from random import Random
from statistics import mean
from xml.sax.saxutils import escape

MODES = ("frozen", "output_only", "state")
SEEDS = tuple(range(93, 109))
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 20261031


def sign_test(values: list[float]) -> dict:
    """Exact one-sided binomial sign test, omitting reported ties."""
    positives = sum(x > 0 for x in values)
    negatives = sum(x < 0 for x in values)
    ties = len(values) - positives - negatives
    n = positives + negatives
    p = sum(math.comb(n, k) for k in range(positives, n + 1)) / (2**n) if n else 1.0
    return {"positive": positives, "negative": negatives, "ties": ties, "n": n, "p": p}


def percentile(xs: list[float], q: float) -> float:
    ordered = sorted(xs)
    pos = q * (len(ordered) - 1)
    low = math.floor(pos)
    high = math.ceil(pos)
    return ordered[low] * (high - pos) + ordered[high] * (pos - low) if low != high else ordered[low]


def paired_interval(xs: list[float], *, seed: int = BOOTSTRAP_SEED,
                    n_draws: int = BOOTSTRAP_DRAWS) -> tuple[float, float]:
    """Percentile bootstrap resampling *population seeds*, never agent rows."""
    if not xs:
        raise ValueError("Empty list")
    rng = Random(seed)
    n = len(xs)
    draws = [mean(xs[rng.randrange(n)] for _ in range(n)) for _ in range(n_draws)]
    return (percentile(draws, 0.025), percentile(draws, 0.975))


def load_rows(folder: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest["world_seed"] != 11 or manifest["population_seeds"] != list(SEEDS):
        raise ValueError("Frozen v5.4 world/seed manifest mismatch")
    if manifest["rate_frozen"] != 0.0003 or manifest["conditions"] != list(MODES):
        raise ValueError("The v5.4 treatment or controls changed")
    rows = []
    for seed in SEEDS:
        row = json.loads((folder / f"seed_{seed}.json").read_text(encoding="utf-8"))
        if row.get("agent_seed") != seed or row.get("world_seed") != 11:
            raise ValueError(f"Seed provenance mismatch: {seed}")
        if set(row["conditions"]) != set(MODES):
            raise ValueError(f"Missing or extra treatment: {seed}")
        for mode in MODES:
            c = row["conditions"][mode]
            eligible = c["eligible_carriers"]
            carriers = c["carrier_candidates"]
            if not isinstance(eligible, int) or eligible <= 0:
                raise ValueError(f"Missing eligible carriers: {seed}/{mode}")
            if not isinstance(carriers, int) or not 0 <= carriers <= eligible:
                raise ValueError(f"Invalid numerator: {seed}/{mode}")
            if not math.isclose(c["candidate_fraction"], carriers / eligible, abs_tol=1e-12):
                raise ValueError(f"Fraction inconsistent with counts: {seed}/{mode}")
            if not math.isfinite(c["total_harvest"]):
                raise ValueError(f"Invalid harvest: {seed}/{mode}")
        rows.append(row)
    return manifest, rows


def audit(rows: list[dict]) -> dict:
    if len(rows) != len(SEEDS):
        raise ValueError("Incomplete preregistered seed set")
    results = {}
    for baseline in ("frozen", "output_only"):
        diff = [r["conditions"]["state"]["candidate_fraction"]
                - r["conditions"][baseline]["candidate_fraction"] for r in rows]
        lo, hi = paired_interval(diff, seed=BOOTSTRAP_SEED + (baseline == "output_only"))
        results[baseline] = {"difference": mean(diff), "bootstrap_95": [lo, hi],
                             **sign_test(diff), "pairs": diff}
    harvest = [r["conditions"]["state"]["total_harvest"]
               - r["conditions"]["output_only"]["total_harvest"] for r in rows]
    lo, hi = paired_interval(harvest, seed=BOOTSTRAP_SEED + 2)
    full_gate = all(results[k]["difference"] > 0 and results[k]["p"] <= 0.05
                    for k in results) and mean(harvest) >= 0
    return {
        "title": "CIVITAS ZERO v5.4 frozen prospective replication",
        "world_seed": 11,
        "n_population_seeds": len(rows),
        "preregistered_gate_passed": full_gate,
        "mean_carrier_fraction": {m: mean(r["conditions"][m]["candidate_fraction"] for r in rows)
                                  for m in MODES},
        "carrier_denominators": {m: sum(r["conditions"][m]["eligible_carriers"] for r in rows)
                                 for m in MODES},
        "paired_fraction_effects": results,
        "harvest_state_minus_output": {"difference": mean(harvest),
                                      "bootstrap_95": [lo, hi]},
        "limits": [
            "All 16 population seeds share world W11: not independent world replication.",
            "Bootstrap CIs describe population-seed variability conditional on W11.",
            "Post hoc interval plots are not new confirmatory tests.",
            "Decodability is not causal use, culture, science, or consciousness.",
        ],
    }


def _svg(result: dict) -> str:
    """Clean, dependency-free vector graphic for GitHub and paper drafts."""
    w, h = 900, 530
    palette = {"frozen": "#0f766e", "output_only": "#2563eb"}
    x_positions = {"frozen": 270, "output_only": 645}
    ymid, scale = 275, 950
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="Paired population-seed effects">',
        '<rect width="900" height="530" fill="#ffffff"/>',
        '<text x="48" y="57" fill="#0f172a" font-family="Arial,sans-serif" font-size="25" font-weight="700">When predictive states fail to replicate</text>',
        '<text x="48" y="84" fill="#475569" font-family="Arial,sans-serif" font-size="14">Latent Worlds · v5.4 · frozen rate 0.0003 · 16 paired population seeds · one world (W11)</text>',
        '<line x1="95" y1="275" x2="810" y2="275" stroke="#64748b" stroke-width="1.6" stroke-dasharray="6 5"/>',
        '<text x="820" y="280" fill="#475569" font-family="Arial,sans-serif" font-size="12">zero</text>',
        '<text x="47" y="165" fill="#475569" font-family="Arial,sans-serif" font-size="12">+14 pp</text>',
        '<text x="47" y="389" fill="#475569" font-family="Arial,sans-serif" font-size="12">−10 pp</text>',
    ]
    for k in ("frozen", "output_only"):
        z = result["paired_fraction_effects"][k]
        x = x_positions[k]
        color = palette[k]
        for i, d in enumerate(z["pairs"]):
            # deterministic visual jitter, no stochastic figure generation
            jitter = ((i * 29) % 71) - 35
            y = max(130, min(433, ymid - d * scale))
            parts.append(f'<circle cx="{x + jitter}" cy="{y:.1f}" r="4.1" fill="{color}" fill-opacity="0.43"/>')
        yl = ymid - z["bootstrap_95"][0] * scale
        yh = ymid - z["bootstrap_95"][1] * scale
        ym = ymid - z["difference"] * scale
        parts.extend([
            f'<line x1="{x}" x2="{x}" y1="{yh:.1f}" y2="{yl:.1f}" stroke="{color}" stroke-width="4"/>',
            f'<line x1="{x-11}" x2="{x+11}" y1="{yh:.1f}" y2="{yh:.1f}" stroke="{color}" stroke-width="3"/>',
            f'<line x1="{x-11}" x2="{x+11}" y1="{yl:.1f}" y2="{yl:.1f}" stroke="{color}" stroke-width="3"/>',
            f'<circle cx="{x}" cy="{ym:.1f}" r="8" fill="{color}" stroke="#fff" stroke-width="2"/>',
            f'<text x="{x}" y="465" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="600" fill="#0f172a">vs {escape(k.replace("_", " "))}</text>',
            f'<text x="{x}" y="492" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="{color}">Δ {z["difference"]*100:+.2f} pp · p={z["p"]:.3f}</text>',
        ])
    parts += [
        '<text x="48" y="517" font-family="Arial,sans-serif" font-size="11" fill="#64748b">Dots: paired seed effects; solid bar: descriptive bootstrap interval; no confirmation of E1</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "v54_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v5.4: prospective replication — negative",
        "",
        "Data: W11, 16 new population seeds A93–A108. Rate 0.0003 was selected in v5.3 on other seeds.",
        "",
        "| Contrast | Mean difference (pp) | Descriptive 95% CI (pp) | Exact one-sided sign p | Paired wins |",
        "|:--|--:|:--|--:|--:|",
    ]
    for name, d in result["paired_fraction_effects"].items():
        ci = d["bootstrap_95"]
        lines.append(f'| state − {name} | {100*d["difference"]:+.2f} | [{100*ci[0]:+.2f}, {100*ci[1]:+.2f}] | {d["p"]:.4f} | {d["positive"]}/16 |')
    lines += [
        "",
        f'Fitness: mean state − output harvest = {result["harvest_state_minus_output"]["difference"]:+.2f}.',
        f'**Predeclared joint gate: {"PASS" if result["preregistered_gate_passed"] else "FAIL"}.**',
        "",
        "All seeds share W11. The units of replication are population histories, not agents or time points.",
        "Neither decoder success nor a positive mean effect demonstrates functional forecasting or consciousness.",
        "",
    ]
    (output_dir / "V54_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "v54_effects.svg").write_text(_svg(result), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--data", type=Path, default=root / "data/v54")
    parser.add_argument("--output", type=Path, default=root / "figures")
    args = parser.parse_args()
    _, rows = load_rows(args.data)
    result = audit(rows)
    source_summary = json.loads((args.data / "summary.json").read_text(encoding="utf-8"))
    if result["preregistered_gate_passed"] != source_summary["evaluation"]["gate_passed"]:
        raise RuntimeError("Independent audit disagrees with original frozen gate")
    for name in ("frozen", "output_only"):
        original = source_summary["evaluation"]["carrier_fraction_tests"][name]
        got = result["paired_fraction_effects"][name]
        if abs(original["p_one_sided"] - got["p"]) > 1e-12:
            raise RuntimeError("Sign-test mismatch")
        if abs(original["mean_difference"] - got["difference"]) > 1e-12:
            raise RuntimeError("Paired effect mismatch")
    write_outputs(result, args.output)
    print(json.dumps({
        "gate_passed": result["preregistered_gate_passed"],
        "n_seeds": result["n_population_seeds"],
        "output": str(args.output),
        "paired_summary": {k: {"difference": v["difference"], "p": v["p"],
                              "bootstrap_95": v["bootstrap_95"]}
                           for k, v in result["paired_fraction_effects"].items()},
    }, indent=2))


if __name__ == "__main__":
    main()
