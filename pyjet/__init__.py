import numpy as np
from ._libpyjet import cluster

__all__ = [
    'cluster',
]

DTYPE = np.float64
DTYPE_PTEPM = np.dtype([('pT', DTYPE), ('eta', DTYPE), ('phi', DTYPE), ('mass', DTYPE)])
DTYPE_EP = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])
