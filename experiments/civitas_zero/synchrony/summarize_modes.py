"""Compare state-plastic and frozen networks on the synchrony pilot.

All four populations are *exploratory* and share two world-law seeds.
No significance test is meaningful with only two independent worlds.
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data/synchrony_pilot"
FIG = BASE / "figures"
WORLD_SEEDS = (11, 21)
MODES = ("frozen", "state")


def read() -> list[dict]:
    rows = []
    for world in WORLD_SEEDS:
        for mode in MODES:
            prefix = f"W{world}_A201_{mode}_500"
            a = json.loads((DATA / f"{prefix}.json").read_text())
            b = json.loads((DATA / f"{prefix}_individual_audit.json").read_text())
            if a["source_world"] != world or a["mode"] != mode or a["agent_seed"] != 201:
                raise ValueError("Bad world or treatment provenance")
            if b["source_trace"] != prefix + ".npz":
                raise ValueError("Bad trace link")
            rows.append({"world": world, "mode": mode, "pooled": a,
                         "individual": b})
    return rows


def make_svg(rows: list[dict]) -> str:
    vals = [x["individual"]["summary"]["mean_gain_vs_exchanged"] for x in rows]
    ymax = max(0.1, max(abs(x) for x in vals) * 1.25)
    base, height = 245, 125
    colors = {"frozen": "#64748b", "state": "#0f766e"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 460" role="img" aria-label="Individual forecast advantage by learning mode">',
        '<rect width="880" height="460" fill="#fff"/>',
        '<text x="45" y="49" font-family="Arial,sans-serif" font-size="23" font-weight="700" fill="#0f172a">Individual memory: plastic versus frozen</text>',
        '<text x="45" y="80" font-family="Arial,sans-serif" font-size="14" fill="#64748b">Mean matched-time NRMSE advantage · two exploratory world laws · NOT causal</text>',
        f'<line x1="90" y1="{base}" x2="820" y2="{base}" stroke="#475569" stroke-width="1.7" stroke-dasharray="6 5"/>',
        '<text x="825" y="250" font-family="Arial,sans-serif" font-size="12" fill="#475569">zero</text>',
    ]
    for row in rows:
        x = (275 if row["world"] == 11 else 625) + (-46 if row["mode"] == "frozen" else 46)
        gain = float(row["individual"]["summary"]["mean_gain_vs_exchanged"])
        y = base - height * gain / ymax
        parts.extend([
            f'<line x1="{x}" x2="{x}" y1="{base:.2f}" y2="{y:.2f}" stroke="{colors[row["mode"]]}" stroke-width="47" stroke-linecap="round"/>',
            f'<text x="{x}" y="{y+(-18 if gain>=0 else 28):.2f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" fill="{colors[row["mode"]]}" font-weight="700">{gain:+.3f}</text>',
        ])
    for x, label in ((275, "W11"), (625, "W21")):
        parts.append(f'<text x="{x}" y="422" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" fill="#0f172a" font-weight="700">{label}</text>')
    parts.extend([
        '<rect x="278" y="441" width="14" height="12" rx="2" fill="#64748b"/>',
        '<text x="299" y="452" font-family="Arial,sans-serif" font-size="12" fill="#475569">Frozen</text>',
        '<rect x="395" y="441" width="14" height="12" rx="2" fill="#0f766e"/>',
        '<text x="416" y="452" font-family="Arial,sans-serif" font-size="12" fill="#475569">State plasticity 0.0003</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    rows = read()
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "synchrony_learning_modes.svg").write_text(make_svg(rows))
    lines = [
        "# Exploratory matched-time forecast audit by learning condition",
        "",
        "NOT a confirmatory finding: only two world-law seeds; 201 is a single",
        "population RNG seed applied to both arms. The per-agent carrier sample",
        "sizes are endogenous, correlated, and unequal.",
        "",
        "| World | Mode | Eligible agents | Private better than exchange | Mean NRMSE advantage | Harvest |",
        "|:--|:--|--:|--:|--:|--:|",
    ]
    for row in rows:
        summ = row["individual"]["summary"]
        lines.append(f'| W{row["world"]} | {row["mode"]} | '
                     f'{row["individual"]["n_eligible_agents"]} | '
                     f'{summ["fraction_individual_better_than_exchange"]*100:.1f}% | '
                     f'{summ["mean_gain_vs_exchanged"]:+.4f} | '
                     f'{row["pooled"]["total_harvest"]:.1f} |')
    lines.extend([
        "",
        "Positive NRMSE advantage means the original agent hidden state predicts",
        "better than a different same-world same-time agent hidden state.",
        "No inferential p-value is calculated from agent-level replicates.",
        "The relevant independent unit for cross-physics generalization is WORLD.",
        "This audit does not show a functional action effect or consciousness.",
        "",
    ])
    (FIG / "SYNCHRONY_MODES.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
