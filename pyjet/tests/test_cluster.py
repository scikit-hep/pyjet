from pyjet import cluster
from pyjet.testdata import get_event
from numpy.testing import assert_array_equal
from nose.tools import assert_true, assert_equal, assert_almost_equal
from numpy.lib.recfunctions import append_fields
import numpy as np


def test_cluster():
    sequence = cluster(get_event(), R=0.6, p=-1, ep=True)
    jets = sequence.inclusive_jets()
    assert_equal(len(jets), 91)
    assert_almost_equal(jets[0].pt, 983.28, 2)


def test_userinfo():
    event = get_event()
    event = append_fields(event, 'id', data=np.arange(len(event)))
    sequence = cluster(event, R=0.6, p=-1, ep=True)
    jets = sequence.inclusive_jets()
    for jet in jets:
        for constit in jet:
            assert_equal(constit.id, constit.info['id'])
