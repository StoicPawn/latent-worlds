import numpy as np
from latent_worlds.semantic_autopsy import _kmeans, _silhouette, _farthest_other_center

def test_signal_clustering_helpers():
    x=np.array([[0,0],[0.1,0],[3,3],[3.1,3]],float)
    labels,centers=_kmeans(x,2,seed=2)
    assert len(set(labels))==2
    assert _silhouette(x,labels)>0.5
    q=_farthest_other_center((0.0,0.0),centers)
    assert len(q)==2


def test_causal_codebook_assay_smoke():
    from latent_worlds.semantic_autopsy import causal_codebook_assay
    out=causal_codebook_assay(1,1,steps=80,max_events=25)
    assert "events" in out and "clusters" in out


def test_directional_substitution_assay_smoke():
    from latent_worlds.semantic_autopsy import directional_substitution_assay
    out=directional_substitution_assay(1,1,steps=80,max_events=20,min_pair_events=2)
    assert 'pairs' in out and 'clusters' in out


def test_single_pass_content_assay_smoke_and_stratification():
    from latent_worlds.semantic_autopsy import counterfactual_content_assay_single_pass
    out=counterfactual_content_assay_single_pass(1,1,steps=90,max_events=40,max_events_per_generation=10,min_generation_events=3)
    assert 'events' in out and 'by_generation' in out
    assert out.get('single_pass') is True or out['events']==0
