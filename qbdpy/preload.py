from qbdpy import ffi, lib


# Magic tricks that might get removed in the future
_globals = globals()
for _name, _value in lib.__dict__.items():
    if _name.lower().startswith('qbdipreload_'):
        _globals[_name[12:]] = _value


_on_start = None
_on_premain = None
_on_main = None
_on_run = None
_on_exit = None


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

