#!/usr/bin/env python

from qbdpy import qbdi, preload, util, qbdpy, ffi


vm = None
counter = 0


def on_bb(vm_ref, vm_state, gpr, fpr, _):
    global counter
    counter += 1
    return qbdi.CONTINUE


@preload.on_run
def on_run(vm_ref, start, stop):
    global vm
    vm = qbdpy.VM.from_ref(vm_ref)
    vm.add_vm_event_cb(qbdi.BASIC_BLOCK_ENTRY, on_bb)
    vm.run(start, stop)
    return preload.NO_ERROR


@preload.on_exit
def on_exit(*args):
    print('=' * 80)
    print('Basic blocks executed: {}'.format(counter))
    return preload.NO_ERROR

