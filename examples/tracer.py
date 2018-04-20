#!/usr/bin/env python

# TODO: Figure out why nothing works if this file is called `trace.py`

from qbdpy import qbdi, preload, util
from qbdpy.qbdi import ffi


@ffi.callback('VMAction(VMInstanceRef, GPRState*, FPRState*, void*)')
def print_instruction(vm, gpr, fpr, _):
    flags = qbdi.ANALYSIS_INSTRUCTION | qbdi.ANALYSIS_DISASSEMBLY
    inst = qbdi.getInstAnalysis(vm, flags)
    print('0x{:016X}: {}'.format(inst.address, util.string(inst.disassembly)))
    return qbdi.CONTINUE


@preload.on_run
def on_run(vm, start, stop):
    qbdi.addCodeCB(vm, qbdi.PREINST, print_instruction, ffi.NULL)
    qbdi.run(vm, start, stop)
    return preload.NO_ERROR

