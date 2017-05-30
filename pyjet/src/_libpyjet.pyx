# cython: experimental_cpp_class_def=True, c_string_type=str, c_string_encoding=ascii

import numpy as np
cimport numpy as np
np.import_array()

cimport cython

from libc.math cimport sin, cos, sinh, sqrt

from libcpp cimport bool
from libcpp.vector cimport vector
from cython.operator cimport dereference as deref

from cpython cimport PyObject
from cpython.ref cimport Py_INCREF, Py_XINCREF, Py_DECREF, Py_XDECREF
from cpython.cobject cimport PyCObject_AsVoidPtr

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

DTYPE_PTEPM = np.dtype([('pT', DTYPE), ('eta', DTYPE), ('phi', DTYPE), ('mass', DTYPE)])
DTYPE_EP = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])

include "FastJet.pxi"

# hide the FastJet banner
silence()


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

    def unclustered_particles(self):
        cdef vector[PseudoJet] jets = self.sequence.unclustered_particles()
        return vector_to_list(jets)

    def childless_pseudojets(self):
        cdef vector[PseudoJet] jets = self.sequence.childless_pseudojets()
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
    cdef PseudoJetUserInfo* userinfo

    @staticmethod
    cdef inline PyPseudoJet wrap(PseudoJet& jet):
        wrapped_jet = PyPseudoJet()
        wrapped_jet.jet = jet
        if jet.has_valid_cluster_sequence() and jet.has_constituents():
            wrapped_jet.constits = jet.constituents()
        if jet.has_user_info():
            wrapped_jet.userinfo = <PseudoJetUserInfo*> jet.user_info_ptr()
        else:
            wrapped_jet.userinfo = NULL
        return wrapped_jet

    def __richcmp__(PyPseudoJet self, PyPseudoJet other, int op):
        # only implement eq (2) and ne (3) ops here
        if op in (2, 3):
            epsilon = 1e-5
            equal = abs(self.e - other.e) < epsilon and \
                    abs(self.px - other.px) < epsilon and \
                    abs(self.py - other.py) < epsilon and \
                    abs(self.pz - other.pz) < epsilon
            return equal if op == 2 else not equal
        else:
            raise NotImplementedError("rich comparison operator %i not implemented" % op)

    @property
    def info(self):
        if self.userinfo != NULL:
            return <object> self.userinfo.info
        return None

    def __getattr__(self, attr):
        userinfo_dict = self.info
        if userinfo_dict:
            try:
                return userinfo_dict[attr]
            except KeyError:
                pass
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, attr))

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

    @property
    def child(self):
        cdef PseudoJet child
        if self.jet.has_child(child):
            py_child = PyPseudoJet()
            py_child.jet = child
            return py_child
        else:
            return None

    @property
    def parents(self):
        cdef PseudoJet p1
        cdef PseudoJet p2
        if self.jet.has_parents(p1, p2):
            py_p1 = PyPseudoJet()
            py_p2 = PyPseudoJet()
            py_p1.jet = p1
            py_p2.jet = p2
            return py_p1, py_p2
        else:
            return None

    def __repr__(self):
        return "PyPseudoJet(pt={0:.3f}, eta={1:.3f}, phi={2:.3f}, mass={3:.3f})".format(
            self.pt, self.eta, self.phi, self.mass)


cdef np.ndarray vector_to_array(vector[PseudoJet]& jets, bool ep=False):
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


cdef list vector_to_list(vector[PseudoJet]& jets):
    cdef list py_jets = []
    for jet in jets:
        py_jets.append(PyPseudoJet.wrap(jet))
    return py_jets


cdef void array_to_pseudojets(np.ndarray vectors, vector[PseudoJet]& output, bool ep):
    """
    The dtype ``vectors`` array can be either::

        np.dtype([('pT', 'f8'), ('eta', 'f8'), ('phi', 'f8'), ('mass', 'f8')])

    or if ``ep=True``::

        np.dtype([('E', 'f8'), ('px', 'f8'), ('py', 'f8'), ('pz', 'f8')])

    """
    cdef char* array = <char*> vectors.data
    cdef DTYPE_t* fourvect
    cdef DTYPE_t E, px, py, pz
    cdef PseudoJet pseudojet
    cdef tuple fields = vectors.dtype.names
    cdef unsigned int num_fields = len(fields)
    cdef unsigned int size = vectors.shape[0], i
    cdef unsigned int rowbytes = vectors.itemsize
    cdef bool handle_userinfo = num_fields > 4
    cdef PseudoJetUserInfo* userinfo
    cdef dict userinfo_dict
    output.clear()
    for i in range(size):
        # shift
        fourvect = <DTYPE_t*> &array[i * rowbytes]
        # Note the constructor argument order is px, py, pz, E
        if ep:
            pseudojet = PseudoJet(fourvect[1], fourvect[2], fourvect[3], fourvect[0])
        else:
            px = fourvect[0] * cos(fourvect[2]) # pt cos(phi)
            py = fourvect[0] * sin(fourvect[2]) # pt sin(phi)
            pz = fourvect[0] * sinh(fourvect[1]) # pt sinh(eta)
            E = sqrt(px*px + py*py + pz*pz + fourvect[3] * fourvect[3])
            pseudojet = PseudoJet(px, py, pz, E)
        if handle_userinfo:
            userinfo_dict = {}
            for field in fields[4:]:
                userinfo_dict[field] = vectors[field][i]
            userinfo = new PseudoJetUserInfo(<PyObject*> userinfo_dict)
            pseudojet.set_user_info(userinfo)
        output.push_back(pseudojet)


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
