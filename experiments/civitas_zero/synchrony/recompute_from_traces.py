"""Recompute pilot metrics from immutable observer-only trajectories.

Corrects a discovered lookahead bug in the *secondary* time-lagged
negative control. Real/within-time/exchanged/mean pooled and individual
primary comparisons must stay IDENTICAL or the audit aborts.

Use --apply once after scientific review; --check in CI thereafter.
Preserve the original before/after numbers in CORRECTION_LOG.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from within_time_exchange import diagnose
from individual_audit import run_audit

DATA = Path(__file__).resolve().parents[1] / "data/synchrony_pilot"
WORLDS = (11, 21)
MODES = ("state", "frozen")
BAD_POOLED_KEY = "time_misaligned_mean"
BAD_INDIVIDUAL_KEY = "time_shifted_mean"
METHOD = "strict_past_only_lag_no_cyclic_wrap_v1"


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-12 * max(1.0, abs(a), abs(b))


def _recompute(trace: Path, old: dict) -> dict:
    with np.load(trace, allow_pickle=False) as f:
        sample = {k: f[k] for k in ("times", "ids", "raw", "hidden", "target")}
    sample.update(world_seed=old["source_world"], agent_seed=old["agent_seed"],
                  mode=old["mode"], n_initial=old["n_initial"], n_final=old["n_final"],
                  total_harvest=old["total_harvest"])
    return diagnose(sample)


def audit(*, apply: bool) -> str:
    lines = [
        "# Correction of a secondary pilot negative control",
        "",
        "Before the manuscript branch was published, code review found that",
        "the circular time-shift of population-mean hidden states could access",
        "later timestamps, including the held-out future test segment.",
        "This is lookahead and is not a valid negative control.",
        "",
        "The corrected surrogate uses ONLY past timestamps, without wraparound.",
        "The original same-time exchange and individual-state comparisons",
        "are unchanged to numerical precision. Raw trajectories are immutable.",
        "",
        "| World | Mode | Old leaky lag NRMSE | New past-only lag NRMSE |",
        "|:--|:--|--:|--:|",
    ]
    for world in WORLDS:
        for mode in MODES:
            stem = f"W{world}_A201_{mode}_500"
            trace = DATA / f"{stem}.npz"
            pooled_path = DATA / f"{stem}.json"
            individual_path = DATA / f"{stem}_individual_audit.json"
            pooled = json.loads(pooled_path.read_text())
            actual = _recompute(trace, pooled)
            for name, metrics in actual["outcomes"].items():
                if name == BAD_POOLED_KEY:
                    continue
                for key in ("mean_nrmse", "per_horizon_nrmse"):
                    x, y = pooled["outcomes"][name][key], metrics[key]
                    if isinstance(x, list):
                        if not all(_same(a, b) for a, b in zip(x, y)):
                            raise AssertionError(f"Primary pooled metric changed: {stem}/{name}/{key}")
                    elif not _same(x, y):
                        raise AssertionError(f"Primary pooled metric changed: {stem}/{name}/{key}")
            older_individual = json.loads(individual_path.read_text())
            new_individual = run_audit(trace)
            if len(older_individual["agents"]) != len(new_individual["agents"]):
                raise AssertionError("Individual carrier count changed")
            for a, b in zip(older_individual["agents"], new_individual["agents"]):
                if a["agent_id"] != b["agent_id"]:
                    raise AssertionError("Individual identity changed")
                for n, score in b["scores"].items():
                    if n != BAD_INDIVIDUAL_KEY and not _same(score, a["scores"][n]):
                        raise AssertionError(f"Primary individual score changed: {stem}/{n}")
                for k in ("gain_vs_raw", "gain_vs_exchanged", "gain_vs_population_mean"):
                    if not _same(a[k], b[k]):
                        raise AssertionError(f"Primary individual inference changed: {stem}/{k}")
            old_val = pooled["outcomes"][BAD_POOLED_KEY]["mean_nrmse"]
            new_val = actual["outcomes"][BAD_POOLED_KEY]["mean_nrmse"]
            lines.append(f"| W{world} | {mode} | {old_val:.5f} | {new_val:.5f} |"
                         if apply else f"| W{world} | {mode} | [previous value in log] | {new_val:.5f} |")
            if apply:
                if "past_only_control_revision" in pooled:
                    raise RuntimeError("The correction was already applied; rerun --check")
                pooled["outcomes"] = actual["outcomes"]
                pooled["past_only_control_revision"] = METHOD
                pooled_path.write_text(json.dumps(pooled, indent=2, sort_keys=True) + "\n")
                new_individual["past_only_control_revision"] = METHOD
                individual_path.write_text(json.dumps(new_individual, indent=2) + "\n")
            else:
                if pooled.get("past_only_control_revision") != METHOD:
                    raise ValueError(f"Missing correction provenance {stem}")
                if older_individual.get("past_only_control_revision") != METHOD:
                    raise ValueError(f"Missing individual correction provenance {stem}")
                if not _same(old_val, new_val):
                    raise AssertionError(f"Stale lag negative control {stem}")
                for a, b in zip(older_individual["agents"], new_individual["agents"]):
                    if not _same(a["scores"][BAD_INDIVIDUAL_KEY], b["scores"][BAD_INDIVIDUAL_KEY]):
                        raise AssertionError(f"Stale individual lag control {stem}")
    lines += [
        "",
        "Only derived, never raw, observer-side outputs were recomputed.",
        "All original/within-time-exchange comparisons stayed exactly fixed.",
        "No claim of artificial consciousness, selected prediction or causality.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = p.parse_args()
    msg = audit(apply=args.apply)
    if args.apply:
        (DATA / "CORRECTION_LOG.md").write_text(msg, encoding="utf-8")
    print(msg)
