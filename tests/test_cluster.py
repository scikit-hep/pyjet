from pyjet import cluster, USING_EXTERNAL_FASTJET
from pyjet.testdata import get_event
from numpy.testing import assert_array_equal

import pytest
from pytest import approx

from numpy.lib.recfunctions import append_fields
import numpy as np


def test_cluster():
    sequence = cluster(get_event(), R=0.6, p=-1)
    jets = sequence.inclusive_jets()
    assert len(jets) == 91
    assert jets[0].pt == approx(983.28, abs=2)
    assert isinstance(jets[0].parents, tuple)
    len(jets[0].parents) == 2
    jets[0].parents[0].child.pt == jets[0].pt
    jets[0].parents[0].child == jets[0]

    # too few parameters specified for jet definition
    with pytest.raises(RuntimeError):
        cluster(get_event())

    # hashable
    hash(sequence)
    hash(jets[0])

def test_recluster():
    sequence = cluster(get_event(), R=0.6, p=-1)
    jets = sequence.inclusive_jets()
    assert jets[0].pt == cluster(jets[0], R=0.6, p=-1).inclusive_jets()[0].pt

def test_cluster_vectors_not_structured():
    with pytest.raises(ValueError):
        cluster(np.ones(10), R=0.6, p=-1)

def test_cluster_vectors_fewer_than_four_fields():
    with pytest.raises(ValueError):
        vectors = np.zeros(10, dtype=[('a', 'f8'), ('b', 'f8'), ('c', 'f8')])
        cluster(vectors, R=0.6, p=-1)

def test_cluster_vectors_wrong_type():
    with pytest.raises(ValueError):
        vectors = np.zeros(10, dtype=[('a', 'f8'), ('b', 'f8'), ('c', 'f4'), ('d', 'f8')])
        cluster(vectors, R=0.6, p=-1)

def test_cluster_recombination_schemes():
    recomb_schemes = {
        'E_scheme': (983.28, -0.8676, 36.46),
        'pt_scheme': (983.52, -0.8672, 0.00),
        'pt2_scheme': (983.52, -0.8679, 0.00),
        'Et_scheme': (983.55, -0.8672, 0.00),
        'Et2_scheme': (983.55, -0.8679, 0.00),
        'BIpt_scheme': (983.52, -0.8671, 0.00),
        'BIpt2_scheme': (983.52, -0.8679, 0.00),
        'WTA_pt_scheme': (983.52, -0.8684, 0.14),
        'WTA_modp_scheme': (983.03, -0.8684, 0.14),
    }

    for recomb_scheme, jet in recomb_schemes.items():
        sequence = cluster(get_event(), R=0.6, p=-1, recomb_scheme=recomb_scheme)
        jets = sequence.inclusive_jets()
        
        assert jets[0].pt == approx(jet[0], abs=1e-2)
        assert jets[0].eta == approx(jet[1], abs=1e-4)
        assert jets[0].mass == approx(jet[2], abs=1e-2)

    with pytest.raises(ValueError):
        sequence = cluster(get_event(), R=0.6, p=-1, recomb_scheme='invalid_scheme')

def test_userinfo():
    event = get_event()
    # add an 'id' field to each particle
    event = append_fields(event, 'id', data=np.arange(len(event)))
    sequence = cluster(event, R=0.6, p=-1)
    jets = sequence.inclusive_jets()
    ids = []
    for jet in jets:
        for constit in jet:
            ids.append(constit.id)
            assert constit.id == constit.userinfo['id']
    ids.extend([p.id for p in sequence.unclustered_particles()])
    # are all particles accounted for?
    assert_array_equal(sorted(ids), np.arange(len(event)))

    for jet in jets:
        for constit in jet:
            constit.userinfo = "wow"
            assert constit.userinfo == "wow"

@pytest.mark.skipif(not USING_EXTERNAL_FASTJET, reason="using internal fastjet")
def test_jet_area():
    sequence = cluster(get_event(), R=0.6, p=-1, area='active')
    jets = sequence.inclusive_jets()
    for jet in jets:
        area, error = jet.area
        if len(jet) > 3:  # TODO: need better way to test this
            assert area > 0
