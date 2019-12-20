# distutils: language = c++
# cython: language_level=2
# cython: c_string_type=str
# cython: c_string_encoding=ascii
# cython: embedsignature = True

import numpy as np
cimport numpy as np
np.import_array()

cimport cython
from cython.operator cimport dereference as deref

from libcpp cimport bool
from libcpp.vector cimport vector
from libc.math cimport sin, cos, sinh, sqrt

from cpython cimport PyObject
from cpython.ref cimport Py_INCREF, Py_XINCREF, Py_DECREF, Py_XDECREF
from cpython.cobject cimport PyCObject_AsVoidPtr

cimport fastjet

cdef extern from "2to3.h":
    pass

cdef extern from "Python.h":
    long _Py_HashPointer(void*)

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

DTYPE_PTEPM = np.dtype([('pT', DTYPE), ('eta', DTYPE), ('phi', DTYPE), ('mass', DTYPE)])
DTYPE_EP = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])

USING_EXTERNAL_FASTJET = fastjet._USING_EXTERNAL_FASTJET

# hide the FastJet banner and don't print errors
fastjet.silence()

JET_ALGORITHM = {
    'kt': fastjet.kt_algorithm,
    'cambridge': fastjet.cambridge_algorithm,
    'antikt': fastjet.antikt_algorithm,
    'genkt': fastjet.genkt_algorithm,
    'cambridge_for_passive': fastjet.cambridge_for_passive_algorithm,
    'genkt_for_passive': fastjet.genkt_for_passive_algorithm,
    'ee_kt': fastjet.ee_kt_algorithm,
    'ee_genkt': fastjet.ee_genkt_algorithm,
    'plugin': fastjet.plugin_algorithm,
    'undefined': fastjet.undefined_jet_algorithm,
}

JET_AREA = {
    'active': fastjet.active_area,
    'active_explicit_ghosts': fastjet.active_area_explicit_ghosts,
    'one_ghost_passive': fastjet.one_ghost_passive_area,
    'passive': fastjet.passive_area,
    'voronoi': fastjet.voronoi_area,
}


cdef class JetDefinition:
    cdef fastjet.JetDefinition* jdef

    def __cinit__(self):
        self.jdef = NULL

    def __init__(self, algo='undefined', R=None, p=None):
        if self.jdef != NULL:
            del self.jdef
        cdef fastjet.JetAlgorithm _algo
        try:
            _algo = JET_ALGORITHM[algo]
        except KeyError:
            raise ValueError("{0:r} is not a valid jet algorithm".format(algo))
        if R is not None:
            if p is not None:
                self.jdef = new fastjet.JetDefinition(_algo, R, p)
            else:
                self.jdef = new fastjet.JetDefinition(_algo, R)
        else:
            self.jdef = new fastjet.JetDefinition(_algo)

    def __dealloc__(self):
        del self.jdef


cdef class ClusterSequence:
    """ Python wrapper class for fastjet::ClusterSequence
    """
    cdef fastjet.ClusterSequence* sequence
    cdef vector[fastjet.PseudoJet] pseudojets

    def __cinit__(self):
        self.sequence = NULL

    def __init__(self, inputs, JetDefinition jetdef, bool ep=False):
        if self.sequence != NULL:
            del self.sequence
        if isinstance(inputs, np.ndarray):
            # convert numpy array into vector of pseudojets
            array_to_pseudojets(inputs, self.pseudojets, ep)
        elif isinstance(inputs, PseudoJet):
            self.pseudojets = (<PseudoJet> inputs).constits
        else:
            raise TypeError("input is not an ndarray or PseudoJet")
        self.sequence = new fastjet.ClusterSequence(self.pseudojets, deref(jetdef.jdef))

    def __dealloc__(self):
        del self.sequence

    def inclusive_jets(self, double ptmin=0.0, bool sort=True):
        """ return a vector of all jets (in the sense of the inclusive algorithm) with pt >= ptmin.
        """
        cdef vector[fastjet.PseudoJet] jets = self.sequence.inclusive_jets(ptmin)
        if sort:
            jets = fastjet.sorted_by_pt(jets)
        return vector_to_list(jets)

    def n_exclusive_jets(self, double dcut):
        """ return the number of jets (in the sense of the exclusive algorithm)
        that would be obtained when running the algorithm with the given dcut.
        """
        return self.sequence.n_exclusive_jets(dcut)

    def exclusive_jets(self, int njets, bool sort=True):
        """ return a vector of all jets when the event is clustered
        (in the exclusive sense) to exactly njets.
        """
        if int(self.pseudojets.size()) < njets:
            raise ValueError("Requested {0} jets but there are only {1} particles".format(njets, self.pseudojets.size()))
        cdef vector[fastjet.PseudoJet] jets = self.sequence.exclusive_jets(njets)
        if sort:
            jets = fastjet.sorted_by_pt(jets)
        return vector_to_list(jets)

    def exclusive_jets_dcut(self, double dcut, bool sort=True):
        """  return a vector of all jets (in the sense of the exclusive algorithm)
        that would be obtained when running the algorithm with the given dcut.
        """
        njets = self.sequence.n_exclusive_jets(dcut)
        cdef vector[fastjet.PseudoJet] jets = self.sequence.exclusive_jets(njets)
        if sort:
            jets = fastjet.sorted_by_pt(jets)
        return vector_to_list(jets)

    def unclustered_particles(self):
        cdef vector[fastjet.PseudoJet] jets = self.sequence.unclustered_particles()
        return vector_to_list(jets)

    def childless_pseudojets(self):
        cdef vector[fastjet.PseudoJet] jets = self.sequence.childless_pseudojets()
        return vector_to_list(jets)


cdef class ClusterSequenceArea(ClusterSequence):
    cdef fastjet.AreaDefinition areadef

    def __init__(self, inputs, JetDefinition jetdef, str areatype, bool ep=False):
        if self.sequence != NULL:
            del self.sequence
        cdef fastjet.AreaType _area
        try:
            _area = JET_AREA[areatype]
        except KeyError:
            raise ValueError("{0:r} is not a valid jet area type".format(areatype))
        if isinstance(inputs, np.ndarray):
            # convert numpy array into vector of pseudojets
            array_to_pseudojets(inputs, self.pseudojets, ep)
        elif isinstance(inputs, PseudoJet):
            self.pseudojets = (<PseudoJet> inputs).constits
        else:
            raise TypeError("input is not an ndarray or PseudoJet")
        self.areadef = fastjet.AreaDefinition(_area)
        self.sequence = new fastjet.ClusterSequenceArea(self.pseudojets, deref(jetdef.jdef), self.areadef)



# This class allows us to attach arbitrary info to PseudoJets in python objects
# (e.g. a dict)
cdef cppclass PseudoJetUserInfo(fastjet.UserInfoBase):
    PyObject* info

    __init__(PyObject* info):
        this.info = info
        Py_XINCREF(this.info)

    __dealloc__():
        Py_XDECREF(this.info)



cdef class PseudoJet:
    """ Python wrapper class for fastjet::PseudoJet
    """
    cdef fastjet.PseudoJet jet
    cdef vector[fastjet.PseudoJet] constits

    @staticmethod
    cdef inline PseudoJet wrap(fastjet.PseudoJet& jet):
        cdef PseudoJet wrapped_jet = PseudoJet()
        wrapped_jet.jet = jet
        if jet.has_valid_cluster_sequence() and jet.has_constituents():
            wrapped_jet.constits = jet.constituents()
        return wrapped_jet

    def __repr__(self):
        return "{0}(pt={1:.3f}, eta={2:.3f}, phi={3:.3f}, mass={4:.3f})".format(
            self.__class__.__name__, self.pt, self.eta, self.phi, self.mass)

    def __richcmp__(PseudoJet self, PseudoJet other, int op):
        # only implement eq (2) and ne (3) ops here
        if op in (2, 3):
            epsilon = 1e-5
            equal = abs(self.e - other.e) < epsilon and \
                    abs(self.px - other.px) < epsilon and \
                    abs(self.py - other.py) < epsilon and \
                    abs(self.pz - other.pz) < epsilon
            return equal if op == 2 else not equal
        raise NotImplementedError("rich comparison operator %i not implemented" % op)

    def __hash__(self):
        return _Py_HashPointer(<void*>self)

    @property
    def userinfo(self):
        if self.jet.has_user_info():
            jet = <PseudoJetUserInfo*> self.jet.user_info_ptr()
            return <object> jet.info
        return None

    @userinfo.setter
    def userinfo(self, item):
        self.jet.set_user_info(new PseudoJetUserInfo(<PyObject*> item))


    def __getattr__(self, attr):
        userinfo_dict = self.userinfo
        if userinfo_dict:
            try:
                return userinfo_dict[attr]
            except KeyError:
                pass
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, attr))

    def __contains__(self, other):
        cdef fastjet.PseudoJet* jet = <fastjet.PseudoJet*> PyCObject_AsVoidPtr(other.jet)
        if jet == NULL:
            raise TypeError("object must be of type PseudoJet")
        return self.jet.contains(deref(jet))

    def __len__(self):
        return self.constits.size()

    def __iter__(self):
        cdef fastjet.PseudoJet jet
        for jet in self.constits:
            yield PseudoJet.wrap(jet)

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
        cdef fastjet.PseudoJet child
        if self.jet.has_child(child):
            py_child = PseudoJet()
            py_child.jet = child
            return py_child
        return None

    @property
    def parents(self):
        cdef fastjet.PseudoJet p1
        cdef fastjet.PseudoJet p2
        if self.jet.has_parents(p1, p2):
            py_p1 = PseudoJet()
            py_p2 = PseudoJet()
            py_p1.jet = p1
            py_p2.jet = p2
            return py_p1, py_p2
        return None

    @property
    def area(self):
        # return jet area and uncertainty
        if fastjet.jet_has_area(&self.jet):
            return fastjet.jet_area(&self.jet), fastjet.jet_area_error(&self.jet)
        return None, None


cdef np.ndarray vector_to_array(vector[fastjet.PseudoJet]& jets, bool ep=False):
    # convert vector of pseudojets into numpy array
    cdef np.ndarray np_jets
    if ep:
        np_jets = np.empty(jets.size(), dtype=DTYPE_EP)
    else:
        np_jets = np.empty(jets.size(), dtype=DTYPE_PTEPM)
    cdef DTYPE_t* data = <DTYPE_t *> np_jets.data
    cdef fastjet.PseudoJet jet
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


cdef list vector_to_list(vector[fastjet.PseudoJet]& jets):
    cdef list py_jets = []
    for jet in jets:
        py_jets.append(PseudoJet.wrap(jet))
    return py_jets


cdef int array_to_pseudojets(np.ndarray vectors, vector[fastjet.PseudoJet]& output, bool ep) except -1:
    """
    The dtype ``vectors`` array can be either::

        np.dtype([('pT', 'f8'), ('eta', 'f8'), ('phi', 'f8'), ('mass', 'f8')])

    or if ``ep=True``::

        np.dtype([('E', 'f8'), ('px', 'f8'), ('py', 'f8'), ('pz', 'f8')])

    """
    cdef char* array = <char*> vectors.data
    cdef DTYPE_t* fourvect
    cdef DTYPE_t E, px, py, pz
    cdef fastjet.PseudoJet pseudojet
    if vectors.dtype.names is None:
        raise ValueError("vectors must be a structured array where the first four fields are of type float64")
    cdef tuple fields = vectors.dtype.names
    cdef unsigned int num_fields = len(fields)
    if num_fields < 4:
        raise ValueError("vectors has {0} fields but at least four are required".format(num_fields))
    else:
        # check that first four fields are float64 otherwise the pointer
        # arithmetic below will fail miserably
        for field in fields[:4]:
            if vectors.dtype[field] != DTYPE:
                raise ValueError("the first four fields of vectors must be of type float64")
    cdef unsigned int size = vectors.shape[0], i
    cdef unsigned int rowbytes = vectors.itemsize
    cdef bool handle_userinfo = num_fields > 4
    cdef PseudoJetUserInfo* userinfo
    cdef dict userinfo_dict
    output.clear()
    for i in range(size):
        # shift
        fourvect = <DTYPE_t*> &array[i * rowbytes]
        # Note the fastjet.PseudoJet constructor argument order is px, py, pz, E
        if ep:
            pseudojet = fastjet.PseudoJet(fourvect[1], fourvect[2], fourvect[3], fourvect[0])
        else:
            px = fourvect[0] * cos(fourvect[2]) # pt cos(phi)
            py = fourvect[0] * sin(fourvect[2]) # pt sin(phi)
            pz = fourvect[0] * sinh(fourvect[1]) # pt sinh(eta)
            E = sqrt(px*px + py*py + pz*pz + fourvect[3] * fourvect[3])
            pseudojet = fastjet.PseudoJet(px, py, pz, E)
        if handle_userinfo:
            userinfo_dict = {}
            for field in fields[4:]:
                userinfo_dict[field] = vectors[field][i]
            userinfo = new PseudoJetUserInfo(<PyObject*> userinfo_dict)
            pseudojet.set_user_info(userinfo)
        output.push_back(pseudojet)
