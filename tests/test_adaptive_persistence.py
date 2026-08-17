from latent_worlds.adaptive_persistence import adaptive_persistence_assay

def test_adaptive_persistence_shape():
    r=adaptive_persistence_assay(0,0,horizons=(20,25),overrides={
        'reproduction_threshold':15.0,'reproduction_cost':6.0,'resource_regrowth':0.07})
    assert r['horizons']==[20,25]
    assert len(r['results'])==2
    assert 0.0 <= r['supported_fraction'] <= 1.0
    assert isinstance(r['all_horizons_supported'],bool)
