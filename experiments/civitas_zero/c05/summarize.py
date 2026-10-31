"""Reproducible paper-quality C0.5 feasibility figure and audit table.

This does not test a consciousness indicator. Both initial matching and
transient-null continuation are algebraically constructed controls.
"""
from __future__ import annotations
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent
WORLDS=(11,21)
PREFIX="matched_fault_W"
SEED="A211"


def verify():
    rows=[]
    for world in WORLDS:
        original=json.loads((ROOT/"data"/f"{PREFIX}{world}_{SEED}.json").read_text())
        controlled=json.loads((ROOT/"data_transient"/f"{PREFIX}{world}_{SEED}.json").read_text())
        assert original["world_seed"]==controlled["world_seed"]==world
        assert controlled["agent_seed"]==211
        assert controlled["n_eligible_agents"]==original["n_eligible_agents"]
        assert abs(controlled["mean_first_step_hidden_diff"]-original["mean_first_step_hidden_diff"])<1e-12
        assert abs(controlled["mean_delayed_hidden_diff_by_step"][0]-original["mean_delayed_hidden_diff_by_step"][0])<1e-12
        assert controlled["mean_first_step_hidden_diff"]<1e-12
        assert controlled["mean_first_step_logits_diff"]<1e-12
        assert controlled["max_transient_fault_future_hidden_diff"]<1e-12
        assert controlled["max_transient_fault_future_logits_diff"]<1e-12
        assert controlled["fraction_diverged_by_second_step"]==1.
        assert all(
            x["transient_pair_action_kind_mismatches"]==0
            and not x["full_observation_histories_matched"]
            for x in controlled["individual"]
        )
        rows.append(controlled)
    return rows


def svg(rows):
    width,height=900,470
    parts=[
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="C0.5 matched internal and external faults">',
        '<rect width="900" height="470" fill="#fff"/>',
        '<text x="48" y="52" font-family="Arial,sans-serif" font-size="25" font-weight="700" fill="#0f172a">Same first action. Different causal mechanism.</text>',
        '<text x="48" y="82" font-family="Arial,sans-serif" font-size="13" fill="#475569">Real Latent Worlds recurrent controllers · two pilot worlds · open-loop counterfactual sensory replay</text>',
        '<text x="49" y="115" font-family="Arial,sans-serif" font-size="13" fill="#64748b">Average maximum absolute hidden-state difference between intervention arms</text>',
        '<line x1="103" y1="390" x2="835" y2="390" stroke="#64748b"/>',
        '<line x1="103" y1="390" x2="103" y2="155" stroke="#64748b"/>',
    ]
    colors={11:"#2563eb",21:"#0f766e"}
    ticks=(0.,.05,.10,.15)
    maxy=.15
    for t in ticks:
        y=390-215*t/maxy
        parts.append(f'<text x="90" y="{y+4:.1f}" font-family="Arial,sans-serif" font-size="12" text-anchor="end" fill="#64748b">{t:.2f}</text>')
        parts.append(f'<line x1="103" y1="{y:.1f}" x2="835" y2="{y:.1f}" stroke="#e2e8f0"/>')
    for k in range(6):
        x=111+k*138
        parts.append(f'<text x="{x}" y="418" font-family="Arial,sans-serif" text-anchor="middle" font-size="13" fill="#475569">{k}</text>')
    parts.append('<text x="458" y="445" font-family="Arial,sans-serif" text-anchor="middle" font-size="13" fill="#475569">Recurrent updates after intervention (0 = immediate)</text>')
    for r in rows:
        world=r["world_seed"]
        vals=[r["mean_first_step_hidden_diff"]]+r["mean_delayed_hidden_diff_by_step"]
        coords=[(111+k*138,390-215*val/maxy) for k,val in enumerate(vals)]
        path=" ".join(f'{x:.1f},{y:.1f}' for x,y in coords)
        col=colors[world]
        parts.append(f'<polyline points="{path}" fill="none" stroke="{col}" stroke-width="3.5"/>')
        for x,y in coords:parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{col}" stroke="#fff" stroke-width="1.5"/>')
        parts.append(f'<text x="{coords[-1][0]-10}" y="{coords[-1][1]-12}" font-family="Arial,sans-serif" text-anchor="end" font-size="14" fill="{col}">W{world}, n={r["n_eligible_agents"]}</text>')
    parts += [
        '<line x1="515" y1="141" x2="553" y2="141" stroke="#64748b" stroke-width="3" stroke-dasharray="5 4"/>',
        '<text x="561" y="146" font-family="Arial,sans-serif" font-size="13" fill="#64748b">Transient null: ≈ 0 at every step</text>',
        '<text x="49" y="466" font-family="Arial,sans-serif" font-size="11" fill="#64748b">Mechanism and initial equality are engineered. Inputs at intervention are NOT matched. No agent self-monitoring measured.</text>',
        '</svg>',
    ]
    return "\n".join(parts)+"\n"


def main():
    rows=verify()
    out=ROOT/"figures"
    out.mkdir(parents=True,exist_ok=True)
    (out/"matched_faults.svg").write_text(svg(rows))
    lines=[
        "# C0.5 actual-world pilot: mechanistic identifiability gate",
        "",
        "**Exploratory only. NOT a validated artificial consciousness indicator.**",
        "",
        "| World | Real agents | Initial hidden difference | Initial logits difference | Diverged at second step | Max transient-null future hidden difference |",
        "|:--|--:|--:|--:|--:|--:|",
    ]
    for r in rows:
        lines.append(
            f'| W{r["world_seed"]} | {r["n_eligible_agents"]} | '
            f'{r["mean_first_step_hidden_diff"]:.2e} | '
            f'{r["mean_first_step_logits_diff"]:.2e} | '
            f'{100*r["fraction_diverged_by_second_step"]:.0f}% | '
            f'{r["max_transient_fault_future_hidden_diff"]:.2e} |')
    lines += [
        "",
        "The first-step equality and transient null **follow from the chosen",
        "interventions algebraically**. They are unit-calibration successes,",
        "not discoveries about agent cognition. Raw sensory histories differ",
        "in the first step; a sensor-available classifier can detect the cause",
        "without introspection. Delayed divergence under the persistent fault",
        "does not show that the untrained organism can identify, interpret,",
        "or act on the distinction.",
        "",
        "World is the unit of physics replication; only TWO exploratory",
        "worlds were studied, and agent instances are correlated.",
        "Open-loop input replay does not measure counterfactual survival.",
        "",
        "**Decision: NO-GO for claims of self-modeling or consciousness.**",
        "GO for designing a new agent-accessible, reward-relevant matched",
        "fault benchmark with alternative-route and causal-action controls.",
        "",
        "Original near prior art: Phua (2025), arXiv:2512.19155;",
        "Butlin et al. (2026), doi:10.1016/j.tics.2025.10.011;",
        "Tang et al. (2026), arXiv:2610.38911.",
        ""
    ]
    (out/"C05_RESULTS.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__=="__main__":
    main()
