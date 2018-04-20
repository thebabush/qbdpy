from qbdpy import ffi


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


def string(char_p):
    return ffi.string(char_p).decode('utf-8')

