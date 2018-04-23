#!/usr/bin/env python

from qbdpy import qbdi as q, ffi, util


size_t_p = ffi.new('size_t *')
modules = q.getModuleNames(size_t_p)

for i in range(size_t_p[0]):
    m = modules[i]
    # Convert char * to unicode
    m = util.string(m)
    print(m)

