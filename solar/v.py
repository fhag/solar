# -*- coding: utf-8 -*-
"""
Print all py source codes and versions
"""

import os
import importlib
import json

__version__ = '1.0.10'


def get_allfiles(path, extension='.py'):
    '''get all files'''
    allfiles = list()
    for dirpath, dirnames, filenames in os.walk(path):
        files = [file for file in filenames if file.endswith(extension)]
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
                fversion = '{:45s} v{}'.format(filename, version)
                return fversion
    return None


def get_allversions(filelist):
    '''return a list of str with filename and version for .py files'''
    versions = [' python '.center(48, '-')]
    versions.extend(get_versionf(file) for file in files)
    versions = [version for version in versions if version]
    versions.sort()
    return sorted(versions)


def get_alljsonversions(filelist):
    '''return a list of str with filename and version for .json files'''
    versionlist = [' json '.center(48, '-')]
    for file in filelist:
        relpath = os.path.relpath(file, os.getcwd())
        dirname = os.path.dirname(relpath)
        fname = os.path.basename(file)
        filename = os.path.join(dirname, fname)
        try:
            with open(file, 'r') as ofile:
                data = json.loads(ofile.read())
            version = data['__version__']
            versionlist.append('{:45s} v{}'.format(filename, version))
        except (KeyError, json.JSONDecodeError):
            pass
    return versionlist if len(versionlist) > 1 else list()


if __name__ == '__main__':
    cwd = os.getcwd()
    files = get_allfiles(cwd, '.py')
    versions = get_allversions(files)
    files = get_allfiles(cwd, '.json')
    versions.extend(get_alljsonversions(files))
    print('\n'.join(versions))

