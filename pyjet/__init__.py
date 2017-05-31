import numpy as np
from ._libpyjet import (cluster_array, cluster_jet, PyPseudoJet,
                        DTYPE, DTYPE_PTEPM, DTYPE_EP)

__all__ = [
    'cluster',
]


def cluster(vectors, R, p, ep=False):
    """
    Perform jet clustering on a numpy array of 4-vectors in (pT, eta, phi,
    mass) representation, otherwise (E, px, py, pz) representation if ep=True

    Parameters
    ----------

    vectors: np.ndarray or PyPseudoJet
        Array of 4-vectors as (pT, eta, phi, mass) or (E, px, py, pz) if ep=True
    R : float
        Clustering size parameter
    p : int
        Generalized kT clustering parameter (p=1 for kT, p=-1 for anti-kT, p=0 for C/A)

    Returns
    -------

    sequence : PyClusterSequence
        A wrapped ClusterSequence.

    """
    if isinstance(vectors, np.ndarray):
        return cluster_array(vectors, R, p, ep)
    elif isinstance(vectors, PyPseudoJet):
        return cluster_jet(vectors, R, p)
    raise TypeError("vectors is not an ndarray or PyPseudoJet")
