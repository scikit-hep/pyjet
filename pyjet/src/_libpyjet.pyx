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
from cpython.ref cimport Py_INCREF, Py_XINCREF, Py_DECREF, Py_XDECREF
from cpython.cobject cimport (PyCObject_AsVoidPtr,
                              PyCObject_Check,
                              PyCObject_FromVoidPtr)

from libcpp.memory cimport shared_ptr
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

DTYPE_PTEPM = np.dtype([('pT', DTYPE), ('eta', DTYPE), ('phi', DTYPE), ('mass', DTYPE)])
DTYPE_EP = np.dtype([('E', DTYPE), ('px', DTYPE), ('py', DTYPE), ('pz', DTYPE)])

include "FastJet.pyx"

# hide the FastJet banner
silence()
