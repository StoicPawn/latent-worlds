"""Pure audit of v5.4 preregistered gate; no simulation and no holdout access."""
import importlib.util
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[1] / "experiments/civitas_zero/benchmark_v54_prospective.py"
spec = importlib.util.spec_from_file_location("civitas_v54", RUNNER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def _row(seed, frozen=.10, output=.12, state=.17, fh=100, oh=110, sh=120):
    return {"agent_seed":seed,"world_seed":11,"conditions":{
        "frozen":{"eligible_carriers":10,"carrier_candidates":1,"candidate_fraction":frozen,"total_harvest":fh},
        "output_only":{"eligible_carriers":10,"carrier_candidates":1,"candidate_fraction":output,"total_harvest":oh},
        "state":{"eligible_carriers":10,"carrier_candidates":1,"candidate_fraction":state,"total_harvest":sh},
    }}

def test_frozen_protocol():
    assert m.WORLD_SEED == 11
    assert m.AGENT_SEEDS == tuple(range(93,109))
    assert m.RATE == .0003
    assert m.MODES == ("frozen","output_only","state")

def test_sign_math():
    assert m.exact_sign_pvalue([1]*16)["p_one_sided"] == 2**-16
    assert m.exact_sign_pvalue([1]*12+[-1]*4)["p_one_sided"] == sum(__import__("math").comb(16,k) for k in range(12,17))/65536
    z=m.exact_sign_pvalue([0,0,0])
    assert z["p_one_sided"] == 1.0 and z["ties"] == 3

def test_gate_requires_both_controls_and_fitness():
    rows=[_row(s) for s in m.AGENT_SEEDS]
    assert m.evaluate(rows)["gate_passed"]
    for x in rows:
        x["conditions"]["state"]["total_harvest"]=90
    assert not m.evaluate(rows)["gate_passed"]
    for x in rows:
        x["conditions"]["state"]["total_harvest"]=120
        x["conditions"]["state"]["candidate_fraction"]=.11
    assert not m.evaluate(rows)["gate_passed"]

def test_missing_eligibility_must_fail():
    rows=[_row(s) for s in m.AGENT_SEEDS]
    rows[0]["conditions"]["state"]["candidate_fraction"]=None
    assert not m.evaluate(rows)["gate_passed"]
