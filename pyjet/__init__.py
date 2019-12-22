from ._libpyjet import (ClusterSequence, ClusterSequenceArea,
                        JetDefinition, PseudoJet,
                        DTYPE, DTYPE_PTEPM, DTYPE_EP, USING_EXTERNAL_FASTJET)

from ._version import __version__
from ._version import FASTJET_VERSION, FJCONTRIB_VERSION

__all__ = [
    'cluster',
    DTYPE_PTEPM,
    DTYPE_EP,
    FASTJET_VERSION,
    FJCONTRIB_VERSION
]


def cluster(vectors, algo='genkt', area=None, ep=False, **kwargs):
    """
    Perform jet clustering on a numpy array of 4-vectors in (pT, eta, phi,
    mass) representation, otherwise (E, px, py, pz) representation if ep=True

    Parameters
    ----------

    vectors: np.ndarray or PseudoJet
        Array of 4-vectors or a PseudoJet in which case the PseudoJet
        constituents are used as inputs to the jet clustering
    algo: JetDefinition or str (optional, default='genkt')
        The jet definition as a JetDefinition or a string naming the jet
        algorithm in which case the additional keywork arguments are used to
        construct the JetDefinition
    area: str (optional, default=None)
        The type of jet area to compute
    ep: bool (optional, default=False)
        First four fields of ``vectors`` are (pT, eta, phi, mass) if ep=False
        or (E, px, py, pz) if ep=True

    Returns
    -------

    sequence : ClusterSequence
        A wrapped fastjet::ClusterSequence

    """
    if isinstance(algo, str):
        algo = JetDefinition(algo, **kwargs)
    if area is not None:
        return ClusterSequenceArea(vectors, algo, area, ep=ep)
    return ClusterSequence(vectors, algo, ep=ep)


def get_include():
    from pkg_resources import resource_filename
    return resource_filename('pyjet', 'src')
