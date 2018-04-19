#!/usr/bin/env python

import re
import subprocess
import os
import shutil
import functools

import pycparser.c_generator

from IPython import embed as fuck
import glob


_name_counter = -1
def mk_name():
    global _name_counter
    _name_counter += 1
    return '__pQDBI_unused__{}__'.format(_name_counter)


_bitfield_matcher = re.compile(r'^\s+(?:/\*.*?\*/\s*)?:\s*(\d+)\s*([;,])')
_include_matcher = re.compile(r'^#include\s+(?:"(.*)"|<(.*)?>)\s*$')
def fix_bitfield(line):   # Workaround for cffi
    if _bitfield_matcher.match(line):                             # Motherfucking anonymous bitfields
        bitsize, line_end = _bitfield_matcher.match(line).groups()
        bitsize = int(bitsize)
        return '{}: {}{}'.format(mk_name(), bitsize, line_end)
    return line


def fix_includes(line):
    if _include_matcher.match(line):
        groups = _include_matcher.match(line).groups()
        if groups[1]:
            header = groups[1]
            if not header.startswith('QBDI'):
                return '//PATCH//' + line
    return line


_define_matcher = re.compile(r'^#define\s+(\S+)\s+(\d+)\s*$')
def fix_defines(line):
    m = _define_matcher.match(line)
    if m:
        return 'const int {} = {};'.format(m.group(1), m.group(2))
    return line


shutil.rmtree('./patched', ignore_errors=1)
os.makedirs('./patched/cffi')
shutil.copytree('/usr/include/QBDI', './patched/preprocessor/QBDI')
shutil.copy('/usr/include/QBDI.h', './patched/preprocessor/')
shutil.copy('/usr/include/QBDIPreload.h', './patched/preprocessor/')

shutil.copy('/usr/include/QBDIPreload.h', './patched/cffi/')
#shutil.copy('/usr/include/QBDI.h', './patched/cffi/')
# shutil.copytree('/usr/include/QBDI', './patched/cffi/QBDI')


def patch_header(fname, fixer):
    with open(fname, 'r+') as f:
        code = '\n'.join([fixer(l) for l in f.read().splitlines()])
        f.seek(0)
        f.truncate()
        f.write(code)


headers = []
headers += glob.glob('./patched/preprocessor/*')
headers += glob.glob('./patched/preprocessor/*/*')
headers = (h for h in headers if h.endswith('.h'))
for header in headers:
    print('Patching "{}"...'.format(header))
    patch_header(header, fix_bitfield)


# headers = []
# headers += glob.glob('./patched/cffi/*')
# headers += glob.glob('./patched/cffi/*/*')
# headers = (h for h in headers if h.endswith('.h'))
# for header in headers:
    # print('Patching "{}"...'.format(header))
    # patch_header(header, fix_bitfield)

patch_header('./patched/cffi/QBDIPreload.h', fix_includes)
patch_header('./patched/cffi/QBDIPreload.h', fix_defines)
pre = open('./patched/cffi/QBDIPreload.h', 'r').read()
pre = '#define __attribute__(x)\n' + pre
open('/tmp/pre.h', 'w').write(pre)

# p = subprocess.Popen('gcc -E /tmp/pre.h -I./QBDI/include/ -I/home/babuzz/src/pycparser/utils/fake_libc_include'.split(), stdout=subprocess.PIPE)
# p = subprocess.Popen('gcc -nostdinc -E -P /tmp/pre.h -I./QBDI/include/'.split(), stdout=subprocess.PIPE)
p = subprocess.Popen('clang-6.0 -E -P -nostdinc -nobuiltininc /tmp/pre.h -I./patched/preprocessor'.split(), stdout=subprocess.PIPE)
out, err = p.communicate()
out = out.decode('utf8')



def hacks_post(line):
    print(line)
    if '__compile_check' in line:
        return ''
    elif 'qbdi_simulateCall' in line:       # TODO: Figure out how to handle varadic stuff
        return ''
    elif 'qbdi_call' in line:
        return ''
    elif line.startswith('extern int qbdipreload_on_'):
        # return line[len('extern '):]
        # print("FUCK")
        return ''
    return line
out = '\n'.join(hacks_post(l) for l in out.splitlines())


# ARITHMETIC SHIT
out = re.sub(r'\[(\d+)\*(\d+)\]', lambda x: '[{}]'.format(int(x.group(1)) *  int(x.group(2))), out)
out = re.sub(r'=\s*(\d+)<<(\d+)', lambda x: '= {}'.format(int(x.group(1)) << int(x.group(2))), out)


open('/tmp/post.h', 'w').write(out)
