# cython: experimental_cpp_class_def=True, c_string_type=str, c_string_encoding=ascii

from libc.stdlib cimport malloc, free

import numpy as np
cimport numpy as np
np.import_array()

cimport cython

from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.string cimport string, const_char
from cython.operator cimport dereference as deref

from cpython cimport PyObject

from cpython.cobject cimport (PyCObject_AsVoidPtr,
                              PyCObject_Check,
                              PyCObject_FromVoidPtr)

from libcpp.memory cimport shared_ptr
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

# for jet clustering:
dtype_jet = np.dtype([('pT', DTYPE), ('eta', DTYPE), ('phi', DTYPE), ('mass', DTYPE)])
dtype_constit = np.dtype([('ET', DTYPE), ('eta', DTYPE), ('phi', DTYPE)])
# for pythia/hepmc:
dtype_particle = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE), ('mass', DTYPE),
                           ('prodx', DTYPE), ('prody', DTYPE), ('prodz', DTYPE), ('prodt', DTYPE),
                           ('pdgid', DTYPE)])
# for Delphes output
dtype_fourvect = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])

include "FastJet.pyx"
