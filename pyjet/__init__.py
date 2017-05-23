import numpy as np
from ._libpyjet import cluster

__all__ = [
    'cluster',
]

DTYPE = np.float64
VECTOR_DTYPE = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])
