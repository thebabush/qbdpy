from qbdpy import ffi, lib


# Magic tricks that might get removed in the future
_globals = globals()
for _name, _value in lib.__dict__.items():
    _name_l = _name.lower()
    if _name_l.startswith('qbdi_'):
        _globals[_name[5:]] = _value
    elif not _name_l.startswith('qbdipreload_'):
        _globals[_name] = _value

