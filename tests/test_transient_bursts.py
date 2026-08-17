from latent_worlds.longitudinal import _transient_communication_bursts

def _e(t,good,gens=1):
    val={"excess":0.2 if good else 0.0,"p_upper":0.03 if good else 1.0}
    return {"time":t,"recent_signal_evidence":{"encoding":dict(val),"uptake_action":dict(val),"receiver_rows":40,"broadcast_rows":40},"recent":{"signal_generation_count":gens}}

def test_transient_burst_requires_three_consecutive_strong_crossgen_windows():
    epochs=[_e(0,False),_e(100,True,2),_e(200,True,2),_e(300,True,2),_e(400,False)]
    b=_transient_communication_bursts(epochs)
    assert len(b)==1 and b[0]["start_time"]==100 and b[0]["cross_generational"]

def test_two_windows_are_not_enough_anymore():
    epochs=[_e(0,False),_e(100,True,2),_e(200,True,2),_e(300,False)]
    assert _transient_communication_bursts(epochs)==[]
