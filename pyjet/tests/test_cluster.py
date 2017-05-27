from pyjet import cluster
from pyjet.testdata import get_event
from numpy.testing import assert_array_equal
from nose.tools import assert_true, assert_equal, assert_almost_equal


def test_cluster():
    sequence = cluster(get_event(), R=0.6, p=-1, ep=True)
    jets = sequence.inclusive_jets()
    assert_equal(len(jets), 91)
    assert_almost_equal(jets[0].pt, 983.28, 2)
