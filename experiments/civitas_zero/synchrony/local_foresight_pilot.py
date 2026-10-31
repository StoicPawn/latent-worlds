"""Perceptual-access audit of the ecological value of perfect foresight.

The historical observer-side oracle in Latent Worlds optimizes over every
resource patch worldwide; actual agents can only perceive nearby unoccluded
patches. This pilot estimates the value of future physics *within* the
currently visible action-candidate set. The old global-oracle results are
reused without rerunning or retuning.

This is a deliberately generous observer: it sees all present and future
yield-law values of patches that are visible by location. Actual agents
receive neither the law nor those future values. It is NOT a direct bound
on achievable adaptive fitness when agents can explore over many steps.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from latent_worlds.forecast_value import _choice_value
from latent_worlds.phase_map import long_horizon_config
from latent_worlds.replication import standard_turnover_overrides
from latent_worlds.world import World

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT / "data/foresight_pilot/results.json"
DATA = ROOT / "data/local_foresight_pilot/results.json"
FIG = ROOT / "figures"

WORLDS = (11, 21, 31)
WAVES = (0.0, 1.5)
TIMES = tuple(range(0, 1201, 120))
SPEED = 1.0
GRID = 4


def world_for(world_seed: int, wave: float) -> World:
    cfg = long_horizon_config(
        information_level=.35, signal_cost=.03,
        communication_enabled=True, agent_seed=0,
    )
    overrides = standard_turnover_overrides()
    overrides["active_obstacle_fraction"] = .75
    for k, v in overrides.items():
        if not hasattr(cfg, k):
            raise ValueError(f"Unknown config field: {k}")
        setattr(cfg, k, v)
    cfg.resource_wave_strength = float(wave)
    return World(cfg, seed=int(world_seed))


def visible_indices(world: World, origin: tuple[float, float]) -> list[int]:
    ox, oy = origin
    limit2 = world.config.observation_radius ** 2
    return [
        idx
        for idx, p in enumerate(world.resources)
        if p.richness > .01
        and (p.x - ox) ** 2 + (p.y - oy) ** 2 <= limit2
        and world.line_of_sight(ox, oy, p.x, p.y)
    ]


def score_action_set(world: World, origin: tuple[float, float], t: int,
                     visible: list[int], speed: float = SPEED) -> dict:
    """Same available patches; only knowledge of arrival conditions differs."""
    if not visible:
        return {
            "advantage": 0.0,
            "changed": False,
            "n_options": 0,
            "myopic_realized": None,
            "oracle_realized": None,
        }
    old_scores = [
        _choice_value(world, origin, idx, t, speed=speed,
                      evaluate_at_arrival=False)
        for idx in visible
    ]
    new_scores = [
        _choice_value(world, origin, idx, t, speed=speed,
                      evaluate_at_arrival=True)
        for idx in visible
    ]
    myopic_pick = int(np.argmax(old_scores))
    future_pick = int(np.argmax(new_scores))
    delta = float(new_scores[future_pick] - new_scores[myopic_pick])
    if delta < -1e-11:
        raise AssertionError("Foresight cannot be worse on a fixed candidate set")
    return {
        "advantage": max(0.0, delta),
        "changed": myopic_pick != future_pick,
        "n_options": len(visible),
        "myopic_realized": float(new_scores[myopic_pick]),
        "oracle_realized": float(new_scores[future_pick]),
    }


def local_value(world_seed: int, wave: float) -> dict:
    world = world_for(world_seed, wave)
    x = np.linspace(0.0, world.config.width, GRID)
    y = np.linspace(0.0, world.config.height, GRID)
    origins = [(float(u), float(v)) for u in x for v in y]
    states = []
    for origin in origins:
        visible = visible_indices(world, origin)
        for t in TIMES:
            states.append(score_action_set(world, origin, int(t), visible))
    n = len(states)
    if n != 176:
        raise AssertionError("The local pilot must mirror the global 176 choices")
    visible_rows = [r for r in states if r["n_options"] > 0]
    choice_rows = [r for r in states if r["n_options"] > 1]
    return {
        "world_seed": int(world_seed),
        "wave_strength": float(wave),
        "sample_n": n,
        "sensor_radius": float(world.config.observation_radius),
        "sample_visible_fraction": len(visible_rows) / n,
        "choice_possible_fraction": len(choice_rows) / n,
        "mean_visible_patches": sum(r["n_options"] for r in states) / n,
        "mean_advantage_all_origins": sum(r["advantage"] for r in states) / n,
        "mean_advantage_if_visible": (
            sum(r["advantage"] for r in visible_rows) / len(visible_rows)
            if visible_rows else None
        ),
        "choice_change_fraction_all": sum(r["changed"] for r in states) / n,
        "interpretation": (
            "Observer-only fixed visible-candidate-set value of perfect future "
            "physics. Not an agent policy or a direct multi-step fitness upper bound."
        ),
    }


def make_svg(rows: list[dict]) -> str:
    max_gain = max(max(r["global_forecast_advantage"],
                       r["local_visible_set_advantage"]) for r in rows)
    scale = 205 / max(max_gain, 1e-6)
    p = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 540" role="img" aria-label="Forecast value under global and visible-only candidate sets">',
        '<rect width="940" height="540" fill="#fff"/>',
        '<text x="38" y="48" font-family="Arial,sans-serif" fill="#0f172a" font-weight="700" font-size="24">A forecast the agent cannot act on?</text>',
        '<text x="38" y="76" font-family="Arial,sans-serif" fill="#64748b" font-size="14">Observer-only route-choice pilot · paired candidate sets · same world physics and input times</text>',
        '<text x="38" y="110" font-family="Arial,sans-serif" fill="#475569" font-size="13">Mean extra energetic value of perfect foresight (units per decision)</text>',
    ]
    y0 = 360
    for i, row in enumerate(rows):
        xc = 103 + i * 147
        for offset, col, key in [
            (-22, "#94a3b8", "global_forecast_advantage"),
            (22, "#0f766e", "local_visible_set_advantage"),
        ]:
            v = max(0.0, row[key])
            height = max(2, v * scale)
            x = xc + offset - 16
            y = y0 - height
            p.append(f'<rect x="{x}" y="{y:.2f}" width="32" height="{height:.2f}" rx="5" fill="{col}"/>')
            p.append(f'<text x="{xc+offset}" y="{max(126,y-9):.2f}" font-family="Arial,sans-serif" text-anchor="middle" font-size="12" fill="{col}">{v:.3f}</text>')
        p.append(f'<text x="{xc}" y="386" font-family="Arial,sans-serif" text-anchor="middle" font-size="15" fill="#0f172a" font-weight="600">W{row["world_seed"]}</text>')
        p.append(f'<text x="{xc}" y="403" font-family="Arial,sans-serif" text-anchor="middle" font-size="12" fill="#475569">wave {row["wave_strength"]:.1f}</text>')
    p += [
        f'<line x1="42" x2="919" y1="{y0}" y2="{y0}" stroke="#64748b"/>',
        '<rect x="240" y="452" width="16" height="12" rx="2" fill="#94a3b8"/>',
        '<text x="264" y="463" font-family="Arial,sans-serif" font-size="13" fill="#475569">All-world patches</text>',
        '<rect x="490" y="452" width="16" height="12" rx="2" fill="#0f766e"/>',
        '<text x="514" y="463" font-family="Arial,sans-serif" font-size="13" fill="#475569">Currently visible patches only</text>',
        '<text x="38" y="509" font-family="Arial,sans-serif" font-size="12" fill="#64748b">Comparing incremental advantages on different choice sets does NOT imply a monotone upper-bound relation.</text>',
        '<text x="38" y="528" font-family="Arial,sans-serif" font-size="12" fill="#64748b">Exploratory only · 3 independent physical worlds · no claim of agent learning, cognition, or consciousness</text>',
        '</svg>',
    ]
    return "\n".join(p) + "\n"


def main() -> None:
    old = json.loads(PREVIOUS.read_text())
    assert set(old["worlds"]) == set(WORLDS)
    assert set(old["waves"]) == set(WAVES)
    global_rows = {
        (int(r["world_seed"]), float(r["wave_strength"])): r
        for r in old["rows"]
    }
    rows = []
    for world in WORLDS:
        for wave in WAVES:
            original = global_rows[(world, wave)]
            if original["samples"] != 176 or original["speed"] != SPEED:
                raise ValueError("Global pilot mismatched time/grid or speed")
            local = local_value(world, wave)
            rows.append({
                **local,
                "global_forecast_advantage": original["mean_foresight_advantage"],
                "local_visible_set_advantage": local["mean_advantage_all_origins"],
            })
            print(
                f'W{world} wave={wave:g} global={original["mean_foresight_advantage"]:.5f} '
                f'local={local["mean_advantage_all_origins"]:.5f} '
                f'choice_available={local["choice_possible_fraction"]:.2f}',
                flush=True,
            )
    DATA.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "study": "CIVITAS ZERO v5.5 action-set accessibility pilot",
        "status": "EXPLORATORY_ONLY",
        "worlds": list(WORLDS),
        "waves": list(WAVES),
        "source_global": "experiments/civitas_zero/data/foresight_pilot/results.json",
        "rows": rows,
        "limits": [
            "Visible-only candidate patches match the agent's sensor radius and occlusion.",
            "Both competing route choosers still receive privileged patch yield-law evaluations.",
            "One-step visible candidate choice is NOT a bound on multi-step exploration fitness.",
            "Incremental forecasting advantage need not be monotone under shrinking the candidate set.",
            "Spatial/time samples in a world are correlated, not independent world replications.",
        ],
    }
    DATA.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "accessibility_foresight_pilot.svg").write_text(make_svg(rows))
    lines = [
        "# Does the forecasting opportunity survive perceptual restrictions?",
        "",
        "EXPLORATORY observer-side comparison; no autonomous agent is being tested.",
        "",
        "| World | Wave | Global extra value | Visible-set extra value | At least 2 visible options | Mean visible options |",
        "|:--|--:|--:|--:|--:|--:|",
    ]
    for row in rows:
        lines.append(
            f'| W{row["world_seed"]} | {row["wave_strength"]:.1f} | '
            f'{row["global_forecast_advantage"]:.4f} | '
            f'{row["local_visible_set_advantage"]:.4f} | '
            f'{100*row["choice_possible_fraction"]:.1f}% | '
            f'{row["mean_visible_patches"]:.2f} |'
        )
    lines += [
        "",
        "These are different action sets: the ratio of incremental advantages",
        "is descriptive and NOT a theorem about optimal adaptive fitness.",
        "The observer still knows the current/future yield law; real agents do not.",
        "No claim of spontaneous knowledge, civilisation or consciousness.",
        "",
    ]
    (FIG / "ACCESSIBILITY_PILOT.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
