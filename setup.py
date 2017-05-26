#!/usr/bin/env python

import sys

# Check Python version
if sys.version_info < (2, 6):
    sys.exit("pyjet only supports python 2.6 and above")

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins

try:
    # Try to use setuptools if installed
    from setuptools import setup, Extension
    from pkg_resources import parse_version, get_distribution

    if get_distribution('setuptools').parsed_version < parse_version('0.7'):
        # setuptools is too old (before merge with distribute)
        raise ImportError

    from setuptools.command.build_ext import build_ext as _build_ext
    from setuptools.command.install import install as _install
    use_setuptools = True

except ImportError:
    # Use distutils instead
    from distutils.core import setup, Extension
    from distutils.command.build_ext import build_ext as _build_ext
    from distutils.command.install import install as _install
    use_setuptools = False

import os
import platform
import subprocess
from glob import glob

# Prevent setup from trying to create hard links
# which are not allowed on AFS between directories.
# This is a hack to force copying.
try:
    del os.link
except AttributeError:
    pass

local_path = os.path.dirname(os.path.abspath(__file__))
# setup.py can be called from outside the source directory
os.chdir(local_path)
sys.path.insert(0, local_path)


def fastjet_prefix(fastjet_config='fastjet-config'):
    try:
        prefix = subprocess.Popen(
            [fastjet_config, '--prefix'],
            stdout=subprocess.PIPE).communicate()[0].strip()
    except IOError:
        sys.exit("unable to locate fastjet-config. Is it in your $PATH?")
    if sys.version > '3':
        prefix = prefix.decode('utf-8')
    return prefix


libpyjet = Extension(
    'pyjet._libpyjet',
    sources=['pyjet/src/_libpyjet.cpp'],
    depends=['pyjet/src/core.h'],
    language='c++',
    include_dirs=[
        'pyjet/src',
    ],
    extra_compile_args=[
        '-Wno-unused-function',
        '-Wno-write-strings',
    ])

external_fastjet = False


class build_ext(_build_ext):
    user_options = _build_ext.user_options + [
        ('external-fastjet', None, None),
    ]

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.external_fastjet = False

    def finalize_options(self):
        global libpyjet
        global external_fastjet
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process
        try:
            del builtins.__NUMPY_SETUP__
        except AttributeError:
            pass
        import numpy
        libpyjet.include_dirs.append(numpy.get_include())
        if external_fastjet or self.external_fastjet:
            prefix = fastjet_prefix()
            libpyjet.include_dirs += [os.path.join(prefix, 'include')]
            libpyjet.library_dirs = [os.path.join(prefix, 'lib')]
            libpyjet.runtime_library_dirs = libpyjet.library_dirs
            libpyjet.libraries = 'fastjettools fastjet CGAL gmp'.split()
            if platform.system() == 'Darwin':
                libpyjet.extra_link_args.append(
                    '-Wl,-rpath,' + os.path.join(prefix, 'lib'))
        else:
            libpyjet.sources.append('pyjet/src/fjcore.cpp')
            libpyjet.depends.append('pyjet/src/fjcore.h')
            libpyjet.define_macros = [('PYJET_STANDALONE', None)]


class install(_install):
    user_options = _install.user_options + [
        ('external-fastjet', None, None),
    ]

    def initialize_options(self):
        _install.initialize_options(self)
        self.external_fastjet = False

    def finalize_options(self):
        global external_fastjet
        if self.external_fastjet:
            external_fastjet = True
        _install.finalize_options(self)


# Only add numpy to *_requires lists if not already installed to prevent
# pip from trying to upgrade an existing numpy and failing.
try:
    import numpy
except ImportError:
    build_requires = ['numpy']
else:
    build_requires = []

if use_setuptools:
    setuptools_options = dict(
        setup_requires=build_requires,
        install_requires=build_requires,
        extras_require={
            'with-numpy': ('numpy',),
        },
        zip_safe=False,
    )
else:
    setuptools_options = dict()

setup(
    name='pyjet',
    version='0.1.0',
    description='The interface between FastJet and NumPy',
    long_description=''.join(open('README.rst').readlines()),
    maintainer='Noel Dawe',
    maintainer_email='noel@dawe.me',
    license='GPLv3',
    url='http://github.com/ndawe/pyjet',
    packages=[
        'pyjet',
        'pyjet.tests',
        'pyjet.testdata',
    ],
    package_data={
        'pyjet': ['testdata/*.dat'],
    },
    ext_modules=[libpyjet],
    cmdclass={
        'build_ext': build_ext,
        'install': install,
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: C++',
        'Programming Language :: Cython',
        'Development Status :: 3 - Alpha',
    ],
    **setuptools_options
)
