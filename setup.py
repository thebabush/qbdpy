#!/usr/bin/env python

from setuptools import setup

import build_cffi


setup(
    name='qbdpy',
    version='0.1',
    packages=['qbdpy'],
    ext_modules=[build_cffi.ffi.distutils_extension()],
    install_requires=['cffi'],
    setup_requires=['cffi'],
    # cffi_modules=[                # This is reccomended but double compiles in API/ABI modes :/
        # './build_cffi.py:ffi',
    # ],
    scripts=['scripts/qbdpy'],
)

