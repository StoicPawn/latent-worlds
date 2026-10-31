"""Generate a publication-style opportunity figure from completed pilot worlds.

The underlying opportunities are observer-side upper bounds, not agent achievements.
Uses only the standard library and audited fixed experimental settings.
"""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/foresight_pilot/results.json"
OUT = ROOT / "figures"


def audit(raw: dict) -> list[dict]:
    if raw.get("status") != "EXPLORATORY_ONLY":
        raise ValueError("This report is an exploratory pilot only")
    worlds = tuple(int(x) for x in raw["worlds"])
    waves = tuple(float(x) for x in raw["waves"])
    if worlds != (11, 21, 31) or waves != (0.0, 1.5):
        raise ValueError("Frozen pilot settings mismatch")
    rows = raw["rows"]
    if len(rows) != 6 or {(v["world_seed"], v["wave_strength"]) for v in rows} != {
        (w, q) for w in worlds for q in waves
    }:
        raise ValueError("Missing world × wave-strength cell")
    for row in rows:
        if int(row["samples"]) != 176:
            raise ValueError("Incomplete sampling grid")
        gain = float(row["mean_foresight_advantage"])
        if gain < -1e-10:
            raise ValueError("An oracle cannot lose to its myopic comparator")
    return rows


def render(rows: list[dict]) -> str:
    table = {(r["world_seed"], r["wave_strength"]): r for r in rows}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 450" role="img" aria-label="Pilot perfect-foresight opportunity in three artificial worlds">',
        '<rect width="900" height="450" fill="#ffffff"/>',
        '<text x="42" y="49" font-family="Arial,sans-serif" font-size="24" font-weight="700" fill="#0f172a">Does the world reward anticipation?</text>',
        '<text x="42" y="77" font-family="Arial,sans-serif" font-size="14" fill="#64748b">Observer-only foresight opportunity · 3 discovery worlds · 176 candidate decisions per condition</text>',
        '<text x="42" y="122" font-family="Arial,sans-serif" font-size="13" fill="#334155">Extra energetic value of an ideal informed route chooser (units/decision)</text>',
        '<line x1="95" y1="364" x2="820" y2="364" stroke="#64748b" stroke-width="1.6"/>',
    ]
    for world, xc in [(11, 230), (21, 460), (31, 690)]:
        for wave, color, offset in ((0.0, "#94a3b8", -34), (1.5, "#0f766e", 34)):
            val = table[(world, wave)]["mean_foresight_advantage"]
            bar_height = max(1.5, val * 203)
            x = xc + offset - 22
            y = 364 - bar_height
            parts.append(f'<rect x="{x}" y="{y:.2f}" width="44" height="{bar_height:.2f}" rx="6" fill="{color}"/>')
            label = f"{val:.3f}"
            parts.append(f'<text x="{xc + offset}" y="{max(152,y-10):.2f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="{color}">{escape(label)}</text>')
        parts.append(f'<text x="{xc}" y="393" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" fill="#0f172a" font-weight="600">W{world}</text>')
    parts.extend([
        '<rect x="303" y="420" width="15" height="12" rx="2" fill="#94a3b8"/>',
        '<text x="325" y="431" font-family="Arial,sans-serif" font-size="12" fill="#475569">No resource wave</text>',
        '<rect x="465" y="420" width="15" height="12" rx="2" fill="#0f766e"/>',
        '<text x="487" y="431" font-family="Arial,sans-serif" font-size="12" fill="#475569">Wave strength 1.5</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main():
    rows = audit(json.loads(DATA.read_text(encoding="utf-8")))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "foresight_opportunity.svg").write_text(render(rows), encoding="utf-8")
    lines = [
        "# Exploratory ecological foresight pilot",
        "",
        "Observer-only ideal route choice, not an agent-cognition result.",
        "",
        "| World | Resource wave | Mean extra energetic value per decision | Relative gain | Decision samples |",
        "|:--|--:|--:|--:|--:|",
    ]
    for row in sorted(rows, key=lambda r: (r["world_seed"], r["wave_strength"])):
        lines.append(
            f'| W{row["world_seed"]} | {row["wave_strength"]:.1f} | {row["mean_foresight_advantage"]:.4f} | {row["relative_mean_advantage"]:.3f} | {row["samples"]} |'
        )
    lines += [
        "",
        "All three physical worlds are PILOT discovery worlds. No independent confirmatory",
        "effect size, standard error, population learning, or agent autonomy is implied.",
        "The oracle has privileged future state information unavailable to organisms.",
        "",
    ]
    (OUT / "FORESIGHT_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
