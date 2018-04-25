#!/usr/bin/env python

import sys
import math
import ctypes
from qbdpy import qbdpy, ffi, qbdi, preload, util


vm = None
udata = {"insn": 0, "cmp": 0}


def vmCB(vm_ref, evt, gpr, fpr, data):
    if evt.event & qbdi.BASIC_BLOCK_ENTRY:
        print("[*] Basic Block: 0x%x -> 0x%x" % \
                (evt.basicBlockStart, evt.basicBlockEnd))
    elif evt.event & qbdi.BASIC_BLOCK_EXIT:
        for acs in vm.get_bb_memory_access():
            print("@ {:#x} {:#x}:{:#x}".format(acs.instAddress,
                                               acs.accessAddress, acs.value))
    return qbdi.CONTINUE


def insnCB(vm_ref, gpr, fpr, data):
    data['insn'] += 1
    types = qbdi.ANALYSIS_INSTRUCTION | qbdi.ANALYSIS_DISASSEMBLY
    types |= qbdi.ANALYSIS_OPERANDS | qbdi.ANALYSIS_SYMBOL
    inst = vm.get_inst_analysis(types)
    print("%s;0x%x: %s" % (util.string(inst.module), inst.address, util.string(inst.disassembly)))
    for op in range(inst.numOperands):
        op = inst.operands[op]
        if op.type == qbdi.OPERAND_IMM:
            print("const: {:d}".format(op.value))
        elif op.type == qbdi.OPERAND_GPR:
            print("reg: {:s}".format(util.string(op.regName)))
    return qbdi.CONTINUE


def cmpCB(vm, gpr, fpr, data):
    data['cmp'] += 1
    return qbdi.CONTINUE


@preload.on_run
def qbdpypreload_on_run(vm_ref, start, stop):
    global vm, udata
    vm = qbdpy.VM.from_ref(vm_ref)

    # get sin function ptr
    libcname = 'libSystem.dylib' if sys.platform == 'darwin' else 'libm.so.6'
    libc = ctypes.cdll.LoadLibrary(libcname)
    funcPtr = ctypes.cast(libc.sin, ctypes.c_void_p).value

    # init VM
    vm.add_vm_event_cb(qbdi.BASIC_BLOCK_ENTRY | qbdi.BASIC_BLOCK_EXIT, vmCB, None)
    state = vm.gpr_state
    success = qbdpy.allocate_virtual_stack(state, 0x100000, vm.new_stack())
    vm.add_instrumented_module_from_addr(funcPtr)
    vm.record_memory_access(qbdi.MEMORY_READ_WRITE)

    # add callbacks on instructions
    iid = vm.add_code_cb(qbdi.PREINST, insnCB, udata)
    iid2 = vm.add_mnemonic_cb("CMP*", qbdi.PREINST, cmpCB, udata)

    # Cast double arg to long
    arg = 1.0
    carg = util.encode_float(arg)

    # set FPR argument
    fpr = vm.fpr_state
    ffi.memmove(fpr.xmm0, carg, 16)
    vm.fpr_state = fpr
    vm.simulate_call(state, 0x42424242)
    vm.gpr_state = state

    # call sin(1.0)
    success = vm.run(funcPtr, 0x42424242)

    # Retrieve output FPR state
    fpr = vm.fpr_state

    # Cast long arg to double
    res = util.decode_float(fpr.xmm0)
    print("%f (python) vs %f (qbdi)" % (math.sin(arg), res))
    vm.delete_instrumentation(iid)
    vm.delete_instrumentation(iid2)

    return preload.NO_ERROR
