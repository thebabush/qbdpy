from qbdpy._qbdi import ffi, lib
from qbdpy._qbdi.lib import *


_on_start = None
_on_premain = None
_on_main = None
_on_run = None
_on_exit = None


class Wrapper(object):
    """
    Maybe useful automagic wrapper for ffi -> python conversion.
    """

    def __init__(self, obj):
        self.obj = obj

    def __dir__(self):
        return self.obj.__dir__() + ['obj']

    def __getattr__(self, name):
        value = getattr(self.obj, name)
        t = type(value)
        if t == int:
            return value
        elif t == ffi.CData:
            t = ffi.typeof(value)
            if t == ffi.typeof('char *'):
                return ffi.string(value).decode('utf-8')
        return value


def on_start(f):
    global _on_start
    _on_start = f
    return f


def on_premain(f):
    global _on_premain
    _on_premain = f
    return f


def on_main(f):
    global _on_main
    _on_main = f
    return f


def on_run(f):
    global _on_run
    _on_run = f
    return f


def on_exit(f):
    global _on_exit
    _on_exit = f
    return f

