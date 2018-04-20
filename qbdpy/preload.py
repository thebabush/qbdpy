from qbdpy import ffi, lib


# Magic tricks that might get removed in the future
_globals = globals()
for _name, _value in lib.__dict__.items():
    if _name.lower().startswith('qbdipreload_'):
        _globals[_name[12:]] = _value


def on_start(f):
    @ffi.def_extern()
    def qbdipreload_on_start(*args):
        return f(*args)
    return f


def on_premain(f):
    @ffi.def_extern()
    def qbdipreload_on_premain(*args):
        return f(*args)
    return f


def on_main(f):
    @ffi.def_extern()
    def qbdipreload_on_main(*args):
        return f(*args)
    return f


def on_run(f):
    @ffi.def_extern()
    def qbdipreload_on_run(*args):
        return f(*args)
    return f


def on_exit(f):
    @ffi.def_extern()
    def qbdipreload_on_exit(*args):
        return f(*args)
    return f

