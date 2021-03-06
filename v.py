# -*- coding: utf-8 -*-
"""
Print all py source codes and versions
"""

import os
import re
from collections import defaultdict

__version__ = '1.0.21'

re_vnr = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3})')
re_version = re.compile('(?i)version')
re_ftype = re.compile('(\.\w+)$')

include_ftypes = ['.py', '.json', '.html', '.sh']


def get_allfiles(path, extension=''):
    '''get all files'''
    allfiles = list()
    for dirpath, dirnames, filenames in os.walk(path):
        files = [file for file in filenames if file.endswith(extension)]
        allfiles.extend([os.path.join(dirpath, file) for file in files])
    allfiles.sort()
    return allfiles


def get_ftype(fname):
    '''Return file type'''
    try:
        return re.search(re_ftype, fname).group()
    except AttributeError:
        return ''
    return


def check_file(ffname) -> str:
    '''Open file and read version'''
    txt, res = None, None
    with open(ffname, 'rb') as file:
        for line in file:
            try:
                txt = line.decode('utf8').lower()
            except UnicodeDecodeError:
                return ffname, None
            if re.search(re_version, txt):
                try:
                    res = re.search(re_vnr, txt).group()
                except AttributeError:
                    pass
                else:
                    break
    return res, get_ftype(ffname)


if __name__ == '__main__':
    cwd = os.getcwd()
    res = defaultdict(list)
    files = get_allfiles(cwd)
    len_cwd = len(cwd) + 1
    files = [file for file in files if get_ftype(file) in include_ftypes]
    for file in files:
        vnr, ftype = check_file(file)
        if vnr is None:
            vnr = 'Missing'
        if ftype and vnr:
            res[ftype].append((file[len_cwd:], vnr))
    n = 80
    os.system('cls' if os.name=='nt' else 'clear')
    print()
    print(f'v.py {__version__} '.center(n, '-'))
    for key in res.keys():
        print(f' {key} '.center(n, '-'))
        for fn, vnr in res[key]:
            print(f' {vnr:9s} : {fn}')
    print(f'-'.center(n, '-'))
