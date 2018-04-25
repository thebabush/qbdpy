#!/usr/bin/env python

# TODO: Figure out why nothing works if this file is called `trace.py`

from qbdpy import qbdi, preload, util, qbdpy, ffi


vm = None


def print_instruction(vm_ref, gpr, fpr, _):
    assert vm._ref == vm_ref
    flags = qbdi.ANALYSIS_INSTRUCTION | qbdi.ANALYSIS_DISASSEMBLY
    inst = vm.get_inst_analysis(flags)
    print('0x{:016X}: {}'.format(inst.address, util.string(inst.disassembly)))
    return qbdi.CONTINUE


@preload.on_run
def on_run(vm_ref, start, stop):
    global vm
    vm = qbdpy.VM.from_ref(vm_ref)
    vm.add_code_cb(qbdi.PREINST, print_instruction)
    vm.run(start, stop)
    return preload.NO_ERROR

