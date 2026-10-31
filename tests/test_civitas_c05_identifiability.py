"""C0.5 identifiability assay sanity checks on actual recurrent controllers.

The algebraically equal first step is a DESIGN CONTROL, not a
statistical discovery or evidence of self-awareness.
"""
from __future__ import annotations
from dataclasses import replace
import numpy as np
from latent_worlds.agents.base import Genome, Observation
from latent_worlds.agents.recurrent import RecurrentAgent
from experiments.civitas_zero.c05.matched_faults import make_pair, replay_pair, DELTA


def observation(time=100, temp=12.):
    return Observation(
        time=time, x=8, y=8, energy=20, temperature=temp, radiation=.3,
        nearby_resources=[(1, 0, 4)], last_action=None, last_yield=0,
        nearby_signals=[], nearby_marks=[], nearby_objects=[],
        held_object=None, nearby_agents=[], world_width=30, world_height=30,
        context_features_enabled=True,
    )


def prepared_agent():
    a=RecurrentAgent(3, 8, 8, 20, Genome())
    a._ensure(np.random.default_rng(5),len(a._features(observation(),3)),3)
    a.hidden=np.random.default_rng(22).normal(0,.18,size=a.HIDDEN)
    return a


def test_matched_first_step_exact_even_when_weights_and_sensor_differ():
    a=prepared_agent(); obs=observation()
    internal,external,eobs=make_pair(a,obs)
    assert not np.allclose(internal.W_rec,external.W_rec)
    assert eobs.temperature-obs.temperature == 20*DELTA
    r=replay_pair(a,[replace(obs,time=obs.time+k) for k in range(6)])
    assert r["first_step_hidden_max_abs_diff"] < 1e-12
    assert r["first_step_logits_max_abs_diff"] < 1e-12
    assert not r["first_step_action_changed"]
    assert r["subsequent_hidden_max_abs_diff"][0]>1e-9
    assert not r["full_observation_histories_matched"]


def test_zero_history_invalidates_this_specific_identifiability_fixture():
    a=prepared_agent()
    a.hidden[:]=0.
    try: make_pair(a,observation())
    except ValueError: pass
    else: raise AssertionError("Matching requires nonzero recurrent history")


def test_unmatched_lesion_not_declared_the_same_perturbation():
    a=prepared_agent()
    internal,external,ext_obs=make_pair(a,observation())
    x0=a._features(observation(),3)
    x1=a._features(ext_obs,3)
    assert not np.array_equal(x0,x1)
    # Any "monitor" with the two full input histories is not blind!
    assert not np.isclose(x0[1],x1[1])


def test_transient_internal_and_external_faults_are_forever_identical_under_same_inputs():
    a=prepared_agent()
    obs=observation()
    r=replay_pair(a,[replace(obs,time=obs.time+k) for k in range(6)], persistent=False)
    assert r["first_step_hidden_max_abs_diff"] < 1e-12
    assert max(r["subsequent_hidden_max_abs_diff"]) < 1e-12
    assert max(r["subsequent_logits_max_abs_diff"]) < 1e-12
    assert not any(r["subsequent_action_kind_mismatch"])
    assert not r["full_observation_histories_matched"]
