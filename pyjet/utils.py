import numpy as np
from . import DTYPE_EP, DTYPE_PTEPM

__all__ = [
	'ptepm2ep',
        'ep2ptepm',
]


def ptepm2ep(rec):
    # convert (pT, eta, phi, mass) into (E, px, py, pz)
    vects = np.empty(rec.shape[0], dtype=DTYPE_EP)
    vects['px'] = rec['pT'] * np.cos(rec['phi'])
    vects['py'] = rec['pT'] * np.sin(rec['phi'])
    vects['pz'] = rec['pT'] * np.sinh(rec['eta'])
    vects['E'] = np.sqrt(vects['px']**2 + vects['py']**2 + vects['pz']**2 + rec['mass']**2)
    return vects


def ep2ptepm(rec):
    # convert (E, px, py, pz) into (pT, eta, phi, mass)
    vects = np.empty(rec.shape[0], dtype=DTYPE_PTEPM)
    ptot = np.sqrt(np.power(rec['px'], 2) + np.power(rec['py'], 2) + np.power(rec['pz'], 2))
    costheta = np.divide(rec['pz'], ptot)
    costheta[ptot == 0] = 1.
    good_costheta = np.power(costheta, 2) < 1
    vects['pT'] = np.sqrt(np.power(rec['px'], 2) + np.power(rec['py'], 2))
    vects['eta'][good_costheta] = -0.5 * np.log(np.divide(1. - costheta, 1. + costheta))
    vects['eta'][~good_costheta & (rec['pz'] == 0.)] = 0.
    vects['eta'][~good_costheta & (rec['pz'] > 0.)] = 10e10
    vects['eta'][~good_costheta & (rec['pz'] < 0.)] = -10e10
    vects['phi'] = np.arctan2(rec['py'], rec['px'])
    vects['phi'][(rec['py'] == 0) & (rec['px'] == 0)] = 0
    mass2 = np.power(rec['E'], 2) - np.power(ptot, 2)
    neg_mass2 = mass2 < 0
    mass2[neg_mass2] *= -1
    vects['mass'] = np.sqrt(mass2)
    vects['mass'][neg_mass2] *= -1
    return vects
