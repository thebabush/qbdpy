#!/usr/bin/env python

import glob
import os
import re
import shutil
import subprocess
import tempfile

import cffi


_name_counter = -1
def mk_unique_name(line):
    global _name_counter
    _name_counter += 1
    return '__pQDBI_unused__{}__'.format(_name_counter)


_bitfield_matcher = re.compile(r'^\s+(?:/\*.*?\*/\s*)?:\s*(\d+)\s*([;,])')
def patch_bitfield(line):   # Workaround for cffi
    if _bitfield_matcher.match(line):                             # Motherfucking anonymous bitfields
        bitsize, line_end = _bitfield_matcher.match(line).groups()
        bitsize = int(bitsize)
        return '{}: {}{}'.format(mk_unique_name(line), bitsize, line_end)
    return line


_include_matcher = re.compile(r'^#include\s+(?:"(.*)"|<(.*)?>)\s*$')
def patch_includes(line):
    if _include_matcher.match(line):
        groups = _include_matcher.match(line).groups()
        if groups[1]:
            header = groups[1]
            if not header.startswith('QBDI'):
                return '//PATCH//' + line
    return line


_define_matcher = re.compile(r'^#define\s+(\S+)\s+(\d+)\s*$')
def patch_defines(line):
    m = _define_matcher.match(line)
    if m:
        return 'const int {} = {};'.format(m.group(1), m.group(2))
    return line


def patch_file(fname, patcher):
    with open(fname, 'r+') as f:
        code = patch_string(f.read(), patcher)
        f.seek(0)
        f.truncate()
        f.write(code)


def patch_file_prepend(fname, content):
    with open(fname, 'r+') as f:
        code = content + f.read()
        f.seek(0)
        f.truncate()
        f.write(code)


def patch_arithmetic_expressions(path):
    with open(path, 'r+') as f:
        code = f.read()

        # ...[123*456]
        code = re.sub(r'\[(\d+)\*(\d+)\]', lambda x: '[{}]'.format(int(x.group(1)) *  int(x.group(2))), code)
        # ....= 123<<456
        code = re.sub(r'=\s*(\d+)<<(\d+)', lambda x: '= {}'.format(int(x.group(1)) << int(x.group(2))), code)

        f.seek(0)
        f.truncate()
        f.write(code)
    return code


def patch_string(code, patcher):
    return '\n'.join([patcher(l) for l in code.splitlines()])


_varadic_matcher = re.compile(r'.*qbdi_\S+?[AV]\(.*')
def patch_problematic(line):
    if '__compile_check' in line:
        return ''
    elif line.startswith('extern int qbdipreload_on_'):
        return ''
    elif _varadic_matcher.match(line):
        return ''

    return line


def listdir_rec(path, f=lambda x: True):
    for root, dirs, files in os.walk(path):
        for name in files:
            fname = os.path.join(root, name)
            if f(fname):
                yield fname


class Builder(object):
    def __init__(self, out_dir, include_dir):
        self.include_dir = include_dir
        self.out_dir = out_dir

        self.cffi_inc_dir = os.path.join(self.out_dir, 'include')
        self.cffi_patched_dir = os.path.join(self.out_dir, 'patched')
        self.cffi_pre_dir = os.path.join(self.out_dir, 'preloader')

    def resolve_include(self, path):
        return os.path.join(self.include_dir, path)

    def build_all(self):
        os.makedirs(self.cffi_inc_dir)
        os.makedirs(self.cffi_patched_dir)
        os.makedirs(self.cffi_pre_dir)

        # Fix bitfield includes
        shutil.copytree(os.path.join(self.include_dir, 'QBDI'), os.path.join(self.cffi_inc_dir, 'QBDI'))
        shutil.copy(os.path.join(self.include_dir, 'QBDI.h'), self.cffi_inc_dir)

        # Patched includes for preprocessing
        shutil.copytree(os.path.join(self.include_dir, 'QBDI'), os.path.join(self.cffi_patched_dir, 'QBDI'))
        shutil.copy(os.path.join(self.include_dir, 'QBDI.h'), self.cffi_patched_dir)
        shutil.copy(os.path.join(self.include_dir, 'QBDIPreload.h'), self.cffi_inc_dir)

        # Main source
        main_h = os.path.join(self.cffi_pre_dir, 'main.h')
        shutil.copy(os.path.join(self.include_dir, 'QBDIPreload.h'), main_h)

        # Patch headers (bitfield)
        print('Fixing headers...')
        headers = listdir_rec(self.cffi_inc_dir, lambda x: x.endswith('.h'))
        self.fix_headers(headers)

        # Patch #include
        headers = listdir_rec(self.cffi_patched_dir, lambda x: x.endswith('.h'))
        self.patch_headers(headers)
        self.fix_headers(headers)

        # Patch main file
        print('Patching main...')
        self.patch_main(main_h)

        # Actualy build
        print('Building...')
        return self.build_ffi(main_h)


    def build_ffi(self, main_h):
        ffi = cffi.FFI()

        # This is passed to a real compiler
        ffi.set_source(
            'qbdpy._qbdi',
            open('./cffi/source.c').read(),
            libraries=['QBDIPreload', 'QBDI'],
            include_dirs=[self.cffi_inc_dir]
        )

        # Alternative:
        # ffi.set_source(
            # 'qbdpy._qbdi',
            # open('~/src/QBDI/tools/QBDIPreload/src/linux_preload.c').read(),
            # libraries=['QBDI'],
            # include_dirs=[self.cffi_inc_dir, self.cffi_inc_dir + '/QBDI/']
        # )

        # Declaration shared between python and C
        ffi.cdef(open(main_h).read())

        # External interface of the .so
        ffi.embedding_api(open('./cffi/embedding.h').read())

        # Python code called at .so load
        ffi.embedding_init_code(open('./cffi/init.py').read())

        return ffi

    def fix_headers(self, paths):
        global _name_counter
        for path in paths:
            _name_counter = -1
            patch_file(path, patch_bitfield)

    def patch_main(self, path):
        global _name_counter
        patch_file_prepend(path, '#define __attribute__(x)\n')
        patch_file(path, patch_includes)
        patch_file(path, patch_defines)
        self.preprocess_header(path)
        _name_counter = -1
        patch_file(path, patch_bitfield)
        patch_file(path, patch_problematic)
        patch_arithmetic_expressions(path)

    def patch_headers(self, paths):
        for path in paths:
            patch_file(path, patch_includes)

    def preprocess_header(self, path):
        p = subprocess.Popen(
            [
                'gcc',
                '-E',
                '-P',
                '-nostdinc',
                path,
                '-I{}'.format(self.cffi_patched_dir),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        code, err = p.communicate()

        if err:
            err = err.decode('utf8')
            print(err)
            if p.returncode != 0:
                exit(p.returncode)

        code = code.decode('utf8')
        open(path, 'w').write(code)


def build_all():
    build_dir = os.path.join(tempfile.gettempdir(), 'qbdpy_tmp')
    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir)

    builder = Builder(build_dir, '/usr/include/')
    return builder.build_all()


ffi = build_all()
if __name__ == '__main__':
    ffi.compile()

