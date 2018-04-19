#!/usr/bin/env python

import cffi

ffi = cffi.FFI()
ffi.cdef(open('/tmp/post.h').read())

ffi.set_source('dbi', '''
#include <QBDIPreload.h>

QBDIPRELOAD_INIT;
''', libraries=['QBDIPreload', 'QBDI', 'python3.5m'], include_dirs=['./patched/preprocessor/'])

ffi.embedding_api('''
int qbdipreload_on_start(void *main);
int qbdipreload_on_premain(void *gprCtx, void *fpuCtx);
int qbdipreload_on_main(int argc, char** argv);
int qbdipreload_on_run(VMInstanceRef vm, rword start, rword stop);
int qbdipreload_on_exit(int status);
''')

ffi.embedding_init_code('''
from dbi import ffi
import dbi

@ffi.def_extern()
def qbdipreload_on_start(*main):
    return dbi.lib.QBDIPRELOAD_NOT_HANDLED
''')

ffi.compile(verbose=1)

