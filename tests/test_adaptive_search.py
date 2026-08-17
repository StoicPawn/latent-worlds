from latent_worlds import adaptive_search


def test_staged_screen_rejects_before_fitness(monkeypatch):
    monkeypatch.setattr(adaptive_search, 'screen_for_late_replication', lambda *a, **k: {'late_generation_communication':False})
    out=adaptive_search.staged_mechanistic_screen(1,0,steps=10)
    assert out['stage']=='depth'
    assert out['mechanistic_candidate'] is False


def test_staged_screen_rejects_scrambled_specificity(monkeypatch):
    monkeypatch.setattr(adaptive_search, 'screen_for_late_replication', lambda *a, **k: {'late_generation_communication':True})
    monkeypatch.setattr(adaptive_search, 'direct_reception_transmission_assay', lambda *a, **k: {'supported':True})
    monkeypatch.setattr(adaptive_search, 'counterfactual_payload_transplant_assay', lambda *a, **k: {'supported':True})
    monkeypatch.setattr(adaptive_search, 'causal_variant_reproduction_assay', lambda *a, **k: {'supported':True})
    out=adaptive_search.staged_mechanistic_screen(1,0,steps=10)
    assert out['stage']=='scrambled_specificity'
    assert out['mechanistic_candidate'] is False
