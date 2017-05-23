import numpy as np
from . import DTYPE

__all__ = [
	'ptepm2ep',
]


def ptepm2ep(rec):
    vects = np.empty(rec.shape[0], dtype=[('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])
    vects['px'] = rec['pT'] * np.cos(rec['phi'])
    vects['py'] = rec['pT'] * np.sin(rec['phi'])
    vects['pz'] = rec['pT'] * np.sinh(rec['eta'])
    vects['E'] = np.sqrt(vects['px']**2 + vects['py']**2 + vects['pz']**2 + rec['mass']**2)
    return vects
