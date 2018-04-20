import os
import sys

from qbdpy import preload
from qbdpy._qbdi import ffi, lib


script = os.getenv('QBDPY_SCRIPT', None)
if script:
    # Init QBDPYPreload
    lib.qbdipreload_hook_init();

    # Import the user script
    script_dir, script_path = os.path.split(script)
    if not script_dir:
        script_dir = '.'
    sys.path.append(script_dir)
    __import__(script_path[:script_path.rfind('.')])


@ffi.def_extern()
def qbdipreload_on_start(main):
    if preload._on_start:
        return preload._on_start(main)
    else:
        return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_premain(gprCtx, fpuCtx):
    if preload._on_premain:
        return preload._on_premain(gprCtx, fpuCtx)
    else:
        return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_main(argc, argv):
    if preload._on_main:
        return preload._on_main(argc, argc)
    else:
        return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_run(vm, start, stop):
    if preload._on_run:
        return preload._on_run(vm, start, stop)
    else:
        return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_exit(status):
    if preload._on_exit:
        return preload._on_exit(status)
    else:
        return lib.QBDIPRELOAD_NOT_HANDLED
