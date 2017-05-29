include "FastJet.pxi"


cdef np.ndarray vector_to_array(vector[PseudoJet]& jets, ep=False):
    # convert vector of pseudojets into numpy array
    cdef np.ndarray np_jets
    if ep:
        np_jets = np.empty(jets.size(), dtype=DTYPE_EP)
    else:
        np_jets = np.empty(jets.size(), dtype=DTYPE_PTEPM)
    cdef DTYPE_t* data = <DTYPE_t *> np_jets.data
    cdef PseudoJet jet
    cdef unsigned int ijet
    if ep:
        for ijet in range(jets.size()):
            jet = jets[ijet]
            data[ijet * 4 + 0] = jet.e()
            data[ijet * 4 + 1] = jet.px()
            data[ijet * 4 + 2] = jet.py()
            data[ijet * 4 + 3] = jet.pz()
    else:
        for ijet in range(jets.size()):
            jet = jets[ijet]
            data[ijet * 4 + 0] = jet.perp()
            data[ijet * 4 + 1] = jet.pseudorapidity()
            data[ijet * 4 + 2] = jet.phi_std()
            data[ijet * 4 + 3] = jet.m()
    return np_jets


cdef object vector_to_list(vector[PseudoJet]& jets):
    py_jets = []
    for jet in jets:
        py_jets.append(PyPseudoJet.wrap(jet))
    return py_jets


cdef void array_to_pseudojets(np.ndarray vectors, vector[PseudoJet]& output, bool ep):
    cdef PseudoJet pseudojet
    cdef unsigned int i
    cdef unsigned int size = vectors.shape[0]
    cdef unsigned int fields = len(vectors.dtype.names)
    cdef DTYPE_t* fourvect
    cdef DTYPE_t* array = <DTYPE_t*> vectors.data
    cdef DTYPE_t E, px, py, pz
    output.clear()
    for i in range(size):
        fourvect = &array[i * fields]
        # Note the constructor argument order is px, py, pz, E
        if ep:
            pseudojet = PseudoJet(fourvect[1], fourvect[2], fourvect[3], fourvect[0])
        else:
            px = fourvect[0] * cos(fourvect[2]) # pt cos(phi)
            py = fourvect[0] * sin(fourvect[2]) # pt sin(phi)
            pz = fourvect[0] * sinh(fourvect[1]) # pt sinh(eta)
            E = sqrt(px*px + py*py + pz*pz + fourvect[3] * fourvect[3])
            pseudojet = PseudoJet(px, py, pz, E)
        output.push_back(pseudojet)


cdef class PyClusterSequence:
    """ Python wrapper class for fastjet::ClusterSequence
    """
    cdef ClusterSequence* sequence

    def __dealloc__(self):
        del self.sequence

    @staticmethod
    cdef inline PyClusterSequence wrap(ClusterSequence* sequence):
        wrapped_sequence = PyClusterSequence()
        wrapped_sequence.sequence = sequence
        return wrapped_sequence

    def inclusive_jets(self, double ptmin=0.0, bool sort=True):
        """ return a vector of all jets (in the sense of the inclusive algorithm) with pt >= ptmin.
        """
        cdef vector[PseudoJet] jets = self.sequence.inclusive_jets(ptmin)
        if sort:
            jets = sorted_by_pt(jets)
        return vector_to_list(jets)


# This class allows us to attach arbitrary info to PseudoJets in python objects
# (e.g. a dict)
cdef cppclass PseudoJetUserInfo(UserInfoBase):
    PyObject* info

    __init__(PyObject* info):
        this.info = info
        Py_XINCREF(this.info)

    __dealloc__():
        Py_XDECREF(this.info)


cdef class PyPseudoJet:
    """ Python wrapper class for fastjet::PseudoJet
    """
    cdef PseudoJet jet
    cdef vector[PseudoJet] constits

    @staticmethod
    cdef inline PyPseudoJet wrap(PseudoJet& jet):
        wrapped_jet = PyPseudoJet()
        wrapped_jet.jet = jet
        if jet.has_valid_cluster_sequence() and jet.has_constituents():
            wrapped_jet.constits = jet.constituents()
        return wrapped_jet

    def __contains__(self, other):
        cdef PseudoJet* jet = <PseudoJet*> PyCObject_AsVoidPtr(other.jet)
        if jet == NULL:
            raise TypeError("object must be of type PyPseudoJet")
        return self.jet.contains(deref(jet))

    def __len__(self):
        return self.constits.size()

    def __iter__(self):
        cdef PseudoJet jet
        for jet in self.constits:
            yield PyPseudoJet.wrap(jet)

    def constituents(self):
        return list(self)

    def constituents_array(self, bool ep=False):
        return vector_to_array(self.constits, ep)

    @property
    def pt(self):
        return self.jet.perp()

    @property
    def eta(self):
        return self.jet.pseudorapidity()

    @property
    def phi(self):
        return self.jet.phi_std()

    @property
    def mass(self):
        return self.jet.m()

    @property
    def e(self):
        return self.jet.e()

    @property
    def et(self):
        return self.jet.Et()

    @property
    def px(self):
        return self.jet.px()

    @property
    def py(self):
        return self.jet.py()

    @property
    def pz(self):
        return self.jet.pz()

    def __repr__(self):
        return "PyPseudoJet(pt={0:.3f}, eta={1:.3f}, phi={2:.3f}, mass={3:.3f})".format(
            self.pt, self.eta, self.phi, self.mass)


@cython.boundscheck(False)
@cython.wraparound(False)
def cluster(np.ndarray vectors, float R, int p, bool ep=False):
    """
    Perform jet clustering on a numpy array of 4-vectors in (pT, eta, phi,
    mass) representation, otherwise (E, px, py, pz) representation if ep=True

    Parameters
    ----------

    vectors: np.ndarray
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
    cdef vector[PseudoJet] pseudojets
    cdef ClusterSequence* sequence

    # convert numpy array into vector of pseudojets
    array_to_pseudojets(vectors, pseudojets, ep)

    # cluster and return PyClusterSequence
    sequence = cluster_genkt(pseudojets, R, p)
    return PyClusterSequence.wrap(sequence)
