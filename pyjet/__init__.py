import numpy as np
from ._libpyjet import (PyClusterSequence, PyClusterSequenceArea,
                        PyJetDefinition, PyPseudoJet,
                        DTYPE, DTYPE_PTEPM, DTYPE_EP, USING_EXTERNAL_FASTJET)

__all__ = [
    'cluster',
]


def cluster(vectors, algo='genkt', area=None, ep=False, **kwargs):
    """
    Perform jet clustering on a numpy array of 4-vectors in (pT, eta, phi,
    mass) representation, otherwise (E, px, py, pz) representation if ep=True

    Parameters
    ----------

    vectors: np.ndarray or PyPseudoJet
        Array of 4-vectors or a PyPseudoJet in which case the PyPseudoJet
        constituents are used as inputs to the jet clustering
    algo: PyJetDefinition or str (optional, default='genkt')
        The jet definition as a PyJetDefinition or a string naming the jet
        algorithm in which case the additional keywork arguments are used to
        construct the PyJetDefinition
    area: str (optional, default=None)
        The type of jet area to compute
    ep: bool (optional, default=False)
        First four fields of ``vectors`` are (pT, eta, phi, mass) if ep=False
        or (E, px, py, pz) if ep=True

    Returns
    -------

    sequence : PyClusterSequence
        A wrapped ClusterSequence.

    """
    if isinstance(algo, str):
        algo = PyJetDefinition(algo, **kwargs)
    if area is not None:
        return PyClusterSequenceArea(vectors, algo, area, ep=ep)
    return PyClusterSequence(vectors, algo, ep=ep)
