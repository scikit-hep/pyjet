import os
from pkg_resources import resource_filename
from numpy import genfromtxt
from .. import DTYPE_EP


__all__ = [
    'get_filepath',
]


def get_event(name='single-event.dat'):
    filepath = resource_filename('pyjet', os.path.join('testdata', name))
    return genfromtxt(filepath, dtype=DTYPE_EP)
