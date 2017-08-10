from pyjet import cluster, USING_EXTERNAL_FASTJET
from pyjet.testdata import get_event
from numpy.testing import assert_array_equal
from nose.tools import (assert_true, assert_equal, assert_almost_equal,
                        raises, assert_raises)
from nose.plugins.skip import SkipTest
from numpy.lib.recfunctions import append_fields
import numpy as np


def test_cluster():
    sequence = cluster(get_event(), R=0.6, p=-1)
    jets = sequence.inclusive_jets()
    assert_equal(len(jets), 91)
    assert_almost_equal(jets[0].pt, 983.28, 2)
    assert_true(isinstance(jets[0].parents, tuple))
    assert_equal(len(jets[0].parents), 2)
    assert_equal(jets[0].parents[0].child.pt, jets[0].pt)
    assert_equal(jets[0].parents[0].child, jets[0])
    # too few parameters specified for jet definition
    assert_raises(RuntimeError, cluster, get_event())
    # hashable
    hash(sequence)
    hash(jets[0])


def test_recluster():
    sequence = cluster(get_event(), R=0.6, p=-1)
    jets = sequence.inclusive_jets()
    assert_equal(jets[0].pt, cluster(jets[0], R=0.6, p=-1).inclusive_jets()[0].pt)


@raises(ValueError)
def test_cluster_vectors_not_structured():
    cluster(np.ones(10), R=0.6, p=-1)


@raises(ValueError)
def test_cluster_vectors_fewer_than_four_fields():
    vectors = np.zeros(10, dtype=[('a', 'f8'), ('b', 'f8'), ('c', 'f8')])
    cluster(vectors, R=0.6, p=-1)


@raises(ValueError)
def test_cluster_vectors_wrong_type():
    vectors = np.zeros(10, dtype=[('a', 'f8'), ('b', 'f8'), ('c', 'f4'), ('d', 'f8')])
    cluster(vectors, R=0.6, p=-1)


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
            assert_equal(constit.id, constit.info['id'])
    ids.extend([p.id for p in sequence.unclustered_particles()])
    # are all particles accounted for?
    assert_array_equal(sorted(ids), np.arange(len(event)))


def test_jet_area():
    if not USING_EXTERNAL_FASTJET:
        raise SkipTest("using internal fastjet")
    sequence = cluster(get_event(), R=0.6, p=-1, area='active')
    jets = sequence.inclusive_jets()
    for jet in jets:
        area, error = jet.area
        if len(jet) > 3:  # TODO: need better way to test this
            assert_true(area > 0)
