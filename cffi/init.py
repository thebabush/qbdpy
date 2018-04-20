import os
import sys

from qbdpy._qbdi import ffi, lib


@ffi.def_extern()
def qbdipreload_on_start(main):
    return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_premain(gprCtx, fpuCtx):
    return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_main(argc, argv):
    return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_run(vm, start, stop):
    return lib.QBDIPRELOAD_NOT_HANDLED


@ffi.def_extern()
def qbdipreload_on_exit(status):
    return lib.QBDIPRELOAD_NOT_HANDLED


# Needs to be here to avoid overwriting user-defined callbacks
script = os.getenv('QBDPY_SCRIPT', None)
if script:
    # Init QBDPYPreload
    lib.qbdipreload_hook_init();

    # Add path to sys.path
    script_dir, script_path = os.path.split(script)
    if not script_dir:
        script_dir = '.'
    sys.path.append(script_dir)

    # Import the user script
    __import__(script_path[:script_path.rfind('.')])

