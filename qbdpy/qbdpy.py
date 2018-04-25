from . import ffi, lib, util


class VM(object):
    def __init__(self, cpu=None, mattrs=None, ref=None):
        # Keep references to calbacks so that FFI doesn't remove them
        self._cbs = []
        self._datas = []

        if ref:
            self._ref = ref
            return

        if not cpu:
            cpu = ffi.NULL
        if not mattrs:
            mattrs = ffi.NULL

        vm_p = ffi.new('VMInstanceRef *')
        lib.qbdi_initVM(vm_p, cpu, mattrs)
        self._ref = vm_p[0]

    @classmethod
    def from_ref(cls, ref):
        return VM(ref=ref)

    def update_ref(self, ref):
        self._ref = ref

    def new_stack(self):
        return ffi.new('uint8_t **')

    # STATE MANAGEMENT

    @property
    def gpr_state(self):
        return lib.qbdi_getGPRState(self._ref)

    @gpr_state.setter
    def gpr_state(self, state):
        lib.qbdi_setGPRState(self._ref, state)

    @property
    def fpr_state(self):
        return lib.qbdi_getFPRState(self._ref)

    @fpr_state.setter
    def fpr_state(self, state):
        lib.qbdi_setFPRState(self._ref, state)

    # STATE INITIALIZATION

    def simulate_call(self, gpr, return_address, *args):
        lib.qbdi_simulateCall(gpr, return_address, len(args), *args)

    # EXECUTION

    def run(self, start, stop):
        lib.qbdi_run(self._ref, start, stop)

    def call(self, retval_p, func_addr, *args):
        lib.qbdi_call(self._ref, retval_p, func_addr, len(args), *args)

    # EXECUTION FILTERING

    def add_instrumented_range(self, start, stop):
        lib.addInstrumentedRange(self._ref, start, stop)

    def remove_instrumented_range(self, start, stop):
        lib.removeInstrumentedRange(self._ref, start, stop)

    def add_instrumented_module(self, name):
        return lib.qbdi_addInstrumentedModule(self._ref, name)

    def remove_instrumented_module(self, name):
        return lib.qbdi_removeInstrumentedModule(self._ref, name)

    def add_instrumented_module_from_addr(self, addr):
        return lib.qbdi_addInstrumentedModuleFromAddr(self._ref, addr)

    def remove_instrumented_module_from_remover(self, addr):
        return lib.qbdi_removeInstrumentedModuleFromAddr(self._ref, addr)

    def instrument_all_executable_maps(self):
        return lib.qbdi_instrumentAllExecutableMaps(self._ref)

    def remove_all_instrumented_ranges(self):
        lib.qbdi_removeAllInstrumentedRanges(self._ref)

    # INSTRUMENTATION

    ## Instruction Callback

    def add_code_cb(self, pos, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addCodeCB(self._ref, pos, _code_cb, data)

    def add_code_addr_cb(self, addr, pos, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addCodeAddrCB(self._ref, addr, pos, _code_cb, data)

    def add_code_range_cb(self, start, end, pos, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addCodeRangeCB(self._ref, start, end, pos, _code_cb, data)

    def add_mnemonic_cb(self, mnemonic, pos, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        if type(mnemonic) == str:
            mnemonic = mnemonic.encode('utf-8')
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addMnemonicCB(self._ref, mnemonic, pos, _code_cb, data)

    ## Memory Callback

    def add_mem_access_cb(self, access_type, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addMemAccessCB(self._ref, access_type, _code_cb, data)

    def add_mem_addr_cb(self, addr, access_type, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addMemAddrCB(self._ref, addr, access_type, _code_cb, data)

    def add_mem_range_cb(self, start, end, access_type, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = inst_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addMemRangeCB(self._ref, start, end, access_type, _code_cb, data)

    ## VM Events

    def add_vm_event_cb(self, event_mask, cb, data=None):
        if not data:
            data = ffi.NULL
        else:
            data = ffi.new_handle(data)
            self._datas.append(data)
        _code_cb = vm_callback(cb)
        self._cbs.append(_code_cb)
        return lib.qbdi_addVMEventCB(self._ref, event_mask, _code_cb, data)

    #############

    def get_inst_analysis(self, analysis_type):
        return lib.qbdi_getInstAnalysis(self._ref, analysis_type)

    def record_memory_access(self, access_type):
        return lib.qbdi_recordMemoryAccess(self._ref, access_type)

    def delete_instrumentation(self, cb_id):
        return lib.qbdi_deleteInstrumentation(self._ref, cb_id)

    def get_bb_memory_access(self):
        size_t_p = ffi.new('size_t *')
        ma = lib.qbdi_getBBMemoryAccess(self._ref, size_t_p)
        for i in range(size_t_p[0]):
            yield ma[i]


def aligned_alloc(size, align):
    return lib.qbdi_alignedAlloc(size, align)


def allocate_virtual_stack(gpr, stack_size, stack):
    return lib.qbdi_allocateVirtualStack(gpr, stack_size, stack)


def get_module_names():
    size_t_p = ffi.new('size_t *')
    modules = lib.qbdi_getModuleNames(size_t_p)
    for i in range(size_t_p[0]):
        yield ffi.string(modules[i])


def inst_callback(f):
    @ffi.callback('VMAction(VMInstanceRef, GPRState *, FPRState *, void *)')
    def g(a, b, c, data):
        data = ffi.from_handle(data) if data else None
        return f(a, b, c, data)
    return g


def vm_callback(f):
    @ffi.callback('VMAction(VMInstanceRef, VMState *, GPRState *, FPRState *, void *)')
    def g(a, b, c, d, data):
        data = ffi.from_handle(data) if data else None
        return f(a, b, c, d, data)
    return g

