from qbdpy._qbdi import ffi, lib
from qbdpy._qbdi.lib import *


_on_start = None
_on_premain = None
_on_main = None
_on_run = None
_on_exit = None


def on_start(f):
    global _on_start
    @ffi.def_extern()
    def qbdipreload_on_start(main):
        return f(main)
    _on_start = qbdipreload_on_start
    return f


def on_premain(f):
    global _on_premain
    @ffi.def_extern()
    def qbdipreload_on_premain(*args):
        return f(*args)
    _on_premain = qbdipreload_on_premain
    return f


def on_main(f):
    global _on_main
    @ffi.def_extern()
    def qbdipreload_on_main(*args):
        return f(*args)
    _on_main = qbdipreload_on_main
    return f


def on_run(f):
    global _on_run
    @ffi.def_extern()
    def qbdipreload_on_run(*args):
        return f(*args)
    _on_run = qbdipreload_on_run
    return f


def on_exit(f):
    global _on_exit
    @ffi.def_extern()
    def qbdipreload_on_exit(*args):
        return f(*args)
    _on_exit = qbdipreload_on_exit
    return f

