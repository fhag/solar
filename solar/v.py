# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 22:09:09 2019
@author: annet
print version of different modules
"""
__version__ = '1.0.6'
print('running v.py        v{}'.format(__version__))

import importlib
import os

def get_allfiles(path):
    '''get all files'''
    allfiles = list()
    for dirpath, dirnames, filenames in os.walk(path):
#        print(dirpath, ',', dirnames)
#        print(filenames)
        files = [file for file in filenames if file.endswith('.py')]
        allfiles.extend([os.path.join(dirpath, file) for file in files])
    return allfiles


def get_version(modname):
    '''extract version number if available'''
    try:
        mod = importlib.import_module(modname.replace('.py', ''))
        modversion = '{:30s}v{}'.format(modname + '.py', mod.__version__)
    except (ModuleNotFoundError, ValueError):
        modversion = '{:20s}does not exist'.format(modname)
    except AttributeError:
        modversion = '{:20s}has no version number'.format(modname)
    except Exception:
        modversion = 'ERROR'
    return modversion

def get_versionf(file):
    '''return filename and version'''
    relpath = os.path.relpath(file, os.getcwd())
    dirname = os.path.dirname(relpath)
    fname = os.path.basename(file)
    filename = os.path.join(dirname, fname)
    with open(file, 'r') as rfile:
        for line in rfile:
            line = line.replace(' ', '')
            if '__version__=' in line:
                version = line.split("'")[1]
                fversion = '{:40s} v{}'.format(filename, version)
                return fversion
    return None

def get_allversions(filelist):
    '''return a list of str with filename and version'''
    versions = [get_versionf(file) for file in files]
    versions = [version for version in versions if version]
    versions.sort()
    return sorted(versions)

if __name__ == '__main__':
    cwd = os.getcwd()
    files = get_allfiles(cwd)
    versions = get_allversions(files)
    print('\n'.join(versions))
