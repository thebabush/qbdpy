#!/usr/bin/env python

from qbdpy import preload
from qbdpy._qbdi import lib


@preload.on_start
def on_start(main):
    print('start')
    return preload.QBDIPRELOAD_NOT_HANDLED


@preload.on_premain
def on_premain(*args):
    print('premain')
    return preload.QBDIPRELOAD_NOT_HANDLED


@preload.on_main
def on_main(*args):
    print('main')
    return preload.QBDIPRELOAD_NOT_HANDLED


@preload.on_run
def on_run(*args):
    print('run')
    print('=' * 80)
    lib.qbdi_run(*args)
    return preload.QBDIPRELOAD_NOT_HANDLED


@preload.on_exit
def on_exit(*args):
    print('=' * 80)
    print('exit')
    return preload.QBDIPRELOAD_NOT_HANDLED

