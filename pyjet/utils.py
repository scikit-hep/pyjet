import numpy as np
from . import DTYPE_EP, DTYPE_PTEPM

__all__ = [
    'ptepm2ep',
    'ep2ptepm',
]


def ptepm2ep(rec):
    """ Convert (pT, eta, phi, mass) into (E, px, py, pz)

    Note that the field names of the input array need not match "pT", "eta",
    "phi", or "mass". This function only assumes that the first four fields
    are those quantities. Garbage in, garbage out.
    """
    pt, eta, phi, mass = rec.dtype.names[:4]
    vects = np.empty(rec.shape[0], dtype=DTYPE_EP)
    vects['px'] = rec[pt] * np.cos(rec[phi])
    vects['py'] = rec[pt] * np.sin(rec[phi])
    vects['pz'] = rec[pt] * np.sinh(rec[eta])
    vects['E'] = np.sqrt(vects['px']**2 + vects['py']**2 + vects['pz']**2 + rec[mass]**2)
    return vects


def ep2ptepm(rec):
    """ Convert (E, px, py, pz) into (pT, eta, phi, mass)

    Note that the field names of the input array need not match "E", "px",
    "py", or "pz". This function only assumes that the first four fields
    are those quantities. Garbage in, garbage out.
    """
    E, px, py, pz = rec.dtype.names[:4]
    vects = np.empty(rec.shape[0], dtype=DTYPE_PTEPM)
    ptot = np.sqrt(np.power(rec[px], 2) + np.power(rec[py], 2) + np.power(rec[pz], 2))
    costheta = np.divide(rec[pz], ptot)
    costheta[ptot == 0] = 1.
    good_costheta = np.power(costheta, 2) < 1
    vects['pT'] = np.sqrt(np.power(rec[px], 2) + np.power(rec[py], 2))
    vects['eta'][good_costheta] = -0.5 * np.log(np.divide(1. - costheta, 1. + costheta))
    vects['eta'][~good_costheta & (rec[pz] == 0.)] = 0.
    vects['eta'][~good_costheta & (rec[pz] > 0.)] = 10e10
    vects['eta'][~good_costheta & (rec[pz] < 0.)] = -10e10
    vects['phi'] = np.arctan2(rec[py], rec[px])
    vects['phi'][(rec[py] == 0) & (rec[px] == 0)] = 0
    mass2 = np.power(rec[E], 2) - np.power(ptot, 2)
    neg_mass2 = mass2 < 0
    mass2[neg_mass2] *= -1
    vects['mass'] = np.sqrt(mass2)
    vects['mass'][neg_mass2] *= -1
    return vects
