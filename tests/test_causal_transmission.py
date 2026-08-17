from latent_worlds.causal_transmission import direct_reception_transmission_assay


def test_direct_assay_smoke():
    r=direct_reception_transmission_assay(0,0,steps=80,assay_start=5,max_events=80,permutations=19)
    assert "by_generation" in r
    assert r["events"] >= 0


def test_direct_assay_scramble_flag():
    r=direct_reception_transmission_assay(0,0,steps=50,assay_start=5,max_events=30,communication_scramble=True,permutations=9)
    assert r["communication_scramble"] is True

from latent_worlds.causal_transmission import counterfactual_payload_transplant_assay

def test_transplant_assay_smoke():
    r=counterfactual_payload_transplant_assay(0,0,steps=60,assay_start=5,max_events=30,permutations=9)
    assert 'supported' in r

from latent_worlds.causal_transmission import causal_variant_reproduction_assay

def test_variant_reproduction_smoke():
    r=causal_variant_reproduction_assay(0,0,steps=60,assay_start=5,max_events=20,min_generation=0,min_cluster_rows=5)
    assert 'supported' in r

from latent_worlds.causal_transmission import direct_secondary_evolution_assay

def test_direct_secondary_assay_smoke():
    r=direct_secondary_evolution_assay(0,0,steps=50,min_generation=0,assay_start=5,permutations=9)
    assert 'replication_status' in r
