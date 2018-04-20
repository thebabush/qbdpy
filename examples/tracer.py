#!/usr/bin/env python

# TODO: Figure out why nothing works if this file is called `trace.py`

from qbdpy import preload
from qbdpy._qbdi import lib, ffi


@ffi.callback('VMAction(VMInstanceRef, GPRState*, FPRState*, void*)')
def print_instruction(vm, gpr, fpr, _):
    flags = lib.QBDI_ANALYSIS_INSTRUCTION | lib.QBDI_ANALYSIS_DISASSEMBLY
    inst = lib.qbdi_getInstAnalysis(vm, flags)
    print('0x{:016X}: {}'.format(inst.address, ffi.string(inst.disassembly).decode('utf8')))
    return lib.QBDI_CONTINUE


@preload.on_run
def on_run(vm, start, stop):
    lib.qbdi_addCodeCB(vm, lib.QBDI_PREINST, print_instruction, ffi.NULL)
    lib.qbdi_run(vm, start, stop)
    return lib.QBDIPRELOAD_NO_ERROR

