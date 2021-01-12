#!/usr/bin/env python

import os
import subprocess
import sys

import numpy

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext


# Manual override, you can just set this here in a pinch, instead of:
# pip install . --global-option="build_ext" --global-option="--external-fastjet"
external_fastjet = False


def fastjet_prefix(fastjet_config="fastjet-config"):
    try:
        prefix = (
            subprocess.Popen([fastjet_config, "--prefix"], stdout=subprocess.PIPE)
            .communicate()[0]
            .strip()
        )
    except IOError:
        sys.exit("Unable to locate fastjet-config. Is it in your $PATH?")

    if hasattr(prefix, "decode"):
        prefix = prefix.decode("utf-8")
    return prefix


extra_compile_args = (
    ["/EHsc"]
    if sys.platform.startswith("win")
    else [
        "-Wno-unused-function",
        "-Wno-write-strings",
    ]
)

libpyjet = Extension(
    "pyjet._libpyjet",
    sources=["pyjet/src/_libpyjet.pyx"],
    depends=[
        "pyjet/src/fastjet.h",
        "pyjet/src/2to3.h",
        "pyjet/src/fastjet.pxd",
    ],
    language="c++",
    include_dirs=[
        "pyjet/src",
        numpy.get_include(),
    ],
    extra_compile_args=extra_compile_args,
)


class build_ext(_build_ext):
    user_options = _build_ext.user_options + [
        ("external-fastjet", None, "Build with external fastjet"),
    ]

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.external_fastjet = False

    def finalize_options(self):
        _build_ext.finalize_options(self)
        if external_fastjet or self.external_fastjet:
            prefix = fastjet_prefix()
            libpyjet.include_dirs.append(os.path.join(prefix, "include"))
            libpyjet.library_dirs = [os.path.join(prefix, "lib")]
            libpyjet.runtime_library_dirs = libpyjet.library_dirs
            libpyjet.libraries = "fastjettools", "fastjet", "CGAL", "gmp"
            if sys.platform.startswith("darwin"):
                libpyjet.extra_link_args.append(
                    "-Wl,-rpath," + os.path.join(prefix, "lib")
                )
        elif "pyjet/src/fjcore.cpp" not in libpyjet.sources:
            libpyjet.sources.append("pyjet/src/fjcore.cpp")
            libpyjet.depends.append("pyjet/src/fjcore.h")
            libpyjet.define_macros = [("PYJET_STANDALONE", None)]


extras = {"dev": ["pytest"], "test": ["pytest"]}
extras["all"] = sum(extras.values(), [])

setup(
    ext_modules=[libpyjet],
    cmdclass={
        "build_ext": build_ext,
    },
    extras_require=extras,
)
