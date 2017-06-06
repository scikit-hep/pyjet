from pyjet import DTYPE
from pyjet.utils import ep2ptepm, ptepm2ep
from pyjet.testdata import get_event
from numpy.testing import assert_array_almost_equal
import numpy as np


def test_vector_conversion():
    event = get_event(ep=True)
    assert_array_almost_equal(
        event.view(DTYPE),
        ptepm2ep(ep2ptepm(event)).view(DTYPE))
