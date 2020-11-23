#!/usr/bin/env python

import os
import sys
import platform
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install as _install


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
    sources=['pyjet/src/_libpyjet.pyx'],
    depends=[
        'pyjet/src/fastjet.h',
        'pyjet/src/2to3.h',
        'pyjet/src/fastjet.pxd',
        ],
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
        elif 'pyjet/src/fjcore.cpp' not in libpyjet.sources:
            libpyjet.sources.append('pyjet/src/fjcore.cpp')
            libpyjet.depends.append('pyjet/src/fjcore.h')
            libpyjet.define_macros = [('PYJET_STANDALONE', None)]

    def build_extensions(self):
        _build_ext.build_extensions(self)


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

extras = {"dev": ["pytest"], "test": ["pytest"]}
extras["all"] = sum(extras.values(), [])

setup(
    #package_data={
    #    'pyjet': [
    #        'testdata/*.dat',
    #        'src/*.pxd', 'src/*.h', 'src/*.cpp',
    #    ],
    #},
    ext_modules=[libpyjet],
    cmdclass={
        'build_ext': build_ext,
        'install': install,
    },
    extras_require=extras,
)
