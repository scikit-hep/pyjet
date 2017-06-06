import os
from pkg_resources import resource_filename
from numpy import genfromtxt
from .. import DTYPE_EP
from ..utils import ep2ptepm


__all__ = [
    'get_event',
]


def get_event(name='single-event.dat', ep=False):
    filepath = resource_filename('pyjet', os.path.join('testdata', name))
    event = genfromtxt(filepath, dtype=DTYPE_EP)
    if not ep:
        event = ep2ptepm(event)
    return event
