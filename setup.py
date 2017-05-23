#!/usr/bin/env python

try:
    import numpy as np
except ImportError:
    raise RuntimeError(
        "numpy cannot be imported. numpy must be installed "
        "prior to installing pyjet")

try:
    # try to use setuptools if installed
    from pkg_resources import parse_version, get_distribution
    from setuptools import setup, Extension
    if get_distribution('setuptools').parsed_version < parse_version('0.7'):
        # before merge with distribute
        raise ImportError
except ImportError:
    # fall back on distutils
    from distutils.core import setup
    from distutils.extension import Extension

import os
import sys
import subprocess
from glob import glob

try:
    from Cython.Build import cythonize
    src = 'pyjet/src/_libpyjet.pyx'
except ImportError:
    src = 'pyjet/src/_libpyjet.cpp'
    cythonize = lambda x: x

# Prevent setup from trying to create hard links
# which are not allowed on AFS between directories.
# This is a hack to force copying.
try:
    del os.link
except AttributeError:
    pass

standalone = True

local_path = os.path.dirname(os.path.abspath(__file__))
# setup.py can be called from outside the source directory
os.chdir(local_path)
sys.path.insert(0, local_path)

libpyjet = Extension(
    'pyjet._libpyjet',
    sources=[src, 'pyjet/src/fjcore.cpp'],
    depends=glob('pyjet/src/*.h'),
    language='c++',
    include_dirs=[
        np.get_include(),
        'pyjet/src',
        #'/usr/local/include',
    ],
    #library_dirs=[
    #    '/usr/local/lib',
    #],
    #libraries='fastjetcontribfragile fastjettools fastjet CGAL'.split(),
    define_macros=[('PYJET_STANDALONE', None)] if standalone else [],
    extra_compile_args=[
        '-Wno-unused-function',
        '-Wno-write-strings',
    ])

setup(
    name='pyjet',
    version='0.0.1',
    maintainer='Noel Dawe',
    maintainer_email='noel@dawe.me',
    license='GPLv3',
    packages=[
        'pyjet',
        'pyjet.tests',
        'pyjet.testdata',
    ],
    package_data={
        'pyjet': ['testdata/*.dat'],
    },
    ext_modules=cythonize([libpyjet]),
)
