"""Recreate the CIVITAS ZERO two-world synchrony pilot report and figure.

Each point is a CORRELATED individual within one world. No agent-level
p-values, spurious confidence intervals, or publication claims are generated.
All figures are SVG with no runtime plotting dependencies.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from xml.sax.saxutils import escape

DATA = Path(__file__).resolve().parents[1] / "data/synchrony_pilot"
FIG = Path(__file__).resolve().parents[1] / "figures"
WORLDS = (11, 21)
AGENT = 201


def load() -> list[dict]:
    records = []
    for world in WORLDS:
        stem = f"W{world}_A{AGENT}_state_500"
        pool = json.loads((DATA / (stem + ".json")).read_text())
        individual = json.loads((DATA / (stem + "_individual_audit.json")).read_text())
        if pool["source_world"] != world or pool["agent_seed"] != AGENT:
            raise ValueError("World/seed mismatch")
        if pool["mode"] != "state" or pool["steps"] != 500:
            raise ValueError("Different experiment conditions")
        if abs(pool["shared_target_max_disagreement"]) > 1e-10:
            raise ValueError("Future target must be shared exactly at each timestamp")
        if individual["source_trace"] != stem + ".npz":
            raise ValueError("Individual analysis refers to another trace")
        if individual["n_eligible_agents"] != len(individual["agents"]):
            raise ValueError("Bad number of eligible individuals")
        records.append({"world": world, "pooled": pool, "individual": individual})
    return records


def render(records: list[dict]) -> str:
    deltas = [
        r["gain_vs_exchanged"]
        for rec in records
        for r in rec["individual"]["agents"]
    ]
    ymax = max(0.08, max(abs(x) for x in deltas) * 1.08)
    mid, span = 265, 157
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 525" role="img" aria-label="World matched individual memory advantage">',
        '<rect width="920" height="525" fill="#ffffff"/>',
        '<text x="46" y="52" font-family="Arial,sans-serif" font-size="25" fill="#0f172a" font-weight="700">Is the forecast in the individual?</text>',
        '<text x="46" y="80" font-family="Arial,sans-serif" font-size="14" fill="#64748b">Exploratory diagnostic · 500 steps per world · state plasticity fixed at 0.0003</text>',
        '<text x="46" y="116" font-family="Arial,sans-serif" font-size="13" fill="#475569">Improvement in NRMSE: exchanged memory − own memory (positive = own better)</text>',
        f'<text x="46" y="{mid-span+5}" font-family="Arial,sans-serif" font-size="12" fill="#475569">+{ymax:.2f}</text>',
        f'<text x="46" y="{mid+span+5}" font-family="Arial,sans-serif" font-size="12" fill="#475569">−{ymax:.2f}</text>',
        f'<line x1="90" x2="850" y1="{mid}" y2="{mid}" stroke="#334155" stroke-width="1.8" stroke-dasharray="7 5"/>',
        '<text x="858" y="270" font-family="Arial,sans-serif" font-size="12" fill="#334155">zero</text>',
    ]
    for rec, xc, color in zip(records, (295, 655), ("#2563eb", "#0f766e")):
        rows = rec["individual"]["agents"]
        for r in rows:
            val = r["gain_vs_exchanged"]
            y = mid - span * val / ymax
            jit = ((r["agent_id"] * 23 + rec["world"] * 11) % 125) - 62
            parts.append(f'<circle cx="{xc+jit}" cy="{y:.2f}" r="4.6" fill="{color}" fill-opacity=".55"/>')
        m = mean(x["gain_vs_exchanged"] for x in rows)
        y = mid - span * m / ymax
        parts.append(f'<line x1="{xc-23}" x2="{xc+23}" y1="{y:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="6"/>')
        parts.append(f'<text x="{xc}" y="458" text-anchor="middle" font-family="Arial,sans-serif" fill="#0f172a" font-size="18" font-weight="700">W{rec["world"]}</text>')
        parts.append(f'<text x="{xc}" y="481" text-anchor="middle" font-family="Arial,sans-serif" fill="{color}" font-size="14">{len(rows)} eligible agents · mean {m:+.3f}</text>')
    parts += [
        '<text x="46" y="515" font-family="Arial,sans-serif" font-size="12" fill="#64748b">Points share the same world future: they are NOT independent replication units. Observer probe ≠ agent causality.</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    records = load()
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "synchrony_exploratory.svg").write_text(render(records))
    lines = [
        "# Two-world synchrony/individual-state pilot",
        "",
        "EXPLORATORY ONLY, not a prospective causal or consciousness finding.",
        "",
        "| World | Pooled raw NRMSE | Pooled true hidden | Pooled time-exchanged | Individual eligible | Own better than exchanged | Mean individual advantage |",
        "|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for rec in records:
        p = rec["pooled"]["outcomes"]
        ind = rec["individual"]
        s = ind["summary"]
        lines.append(
            f'| W{rec["world"]} | {p["raw_only"]["mean_nrmse"]:.4f} | '
            f'{p["individual_hidden"]["mean_nrmse"]:.4f} | '
            f'{p["time_matched_exchange"]["mean_nrmse"]:.4f} | '
            f'{ind["n_eligible_agents"]} | '
            f'{100*s["fraction_individual_better_than_exchange"]:.1f}% | '
            f'{s["mean_gain_vs_exchanged"]:+.4f} |'
        )
    lines += [
        "",
        "NRMSE lower is better; individual advantage = exchanged − true.",
        "The target future forcing is identical for all agents at each t.",
        "Pooled model uses a single decoder for heterogeneous evolving brains.",
        "The individual audit uses independently fitted time-ordered decoders.",
        "Therefore a zero/negative pooled result does not invalidate all",
        "per-agent internal representations; and no agent-row test is independent.",
        "All hypotheses and statistic decisions are exploratory until replicated",
        "on physics-independent holdouts under preregistered rules.",
        "",
    ]
    (FIG / "SYNCHRONY_PILOT.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
