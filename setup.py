#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='qbdpy',
    version='0.1',
    packages=find_packages(),
    install_requires=['cffi'],
    setup_requires=['cffi'],
    cffi_modules=[
        './qbdpy/build_all.py:ffi',
    ],
)

