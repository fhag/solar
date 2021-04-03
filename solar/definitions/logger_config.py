# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Configuration file for logger used throughout the modules
Created on Thu Nov  7 13:59:26 2019
"""
import logging
import os
from datetime import datetime
import teslapy

__version__ = '0.1.7'

LOGGER_FNAME = f'solar/logs/main_{datetime.now():%Y_%m_%d_%H%M}.log'
LOG_LEVEL = logging.DEBUG

FILEHANDLER = logging.FileHandler(os.path.normpath(LOGGER_FNAME), mode='w')
FILEHANDLER.setLevel(LOG_LEVEL)
FILE_FORMATTER = logging.Formatter(
    '%(asctime)s|%(filename)24s|%(levelname)7s|%(funcName)25s|' +
    '%(lineno)3d |%(message)s',
    "%d%b%y %H:%M.%S")
FILEHANDLER.setFormatter(FILE_FORMATTER)

CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(LOG_LEVEL)
CONSOLE_FORMATTER = logging.Formatter(
    '%(name)-12s: %(levelname)-8s %(message)s')
CONSOLE.setFormatter(CONSOLE_FORMATTER)


solarlogger = logging.getLogger('solar')
logger = logging.getLogger(__name__)
logger.error('Kein Fehler')

__version__ = '1.0.2'
print(__version__)

loggerDict = logging.root.manager.loggerDict
loggers = [name for name in loggerDict if 'solar' in name]
loggers.append('teslapy')
for ilogger in loggers:
    print(ilogger)
    if isinstance(loggerDict[ilogger], logging.Logger):
        loggerDict[ilogger].setLevel(LOG_LEVEL)
        handlers = loggerDict[ilogger].handlers
        for handler in handlers:
            loggerDict[ilogger].removeHandler(handler)
        loggerDict[ilogger].addHandler(FILEHANDLER)
        loggerDict[ilogger].addHandler(CONSOLE)
        print(loggerDict[ilogger])


class Filter():
    '''define my own filter'''

    def __init__(self, name=''):
        self.name = name
        self.nlen = len(name)
        print(f'Filter: {name}')

    def filter(self, record):
        '''create filter methode'''
        print(f'filterrecord:{record}')
        if self.nlen == 0:
            return True
        if self.name == record.name:
            return True
        if record.name.find(self.name, 0, self.nlen) != 0:
            print(f'False: {record}')
            return False
        return record.name[self.nlen] == "."


def list_loggers(loggers):
    loggerDict = logging.root.manager.loggerDict
    loggerlen = max([len(lgs) for lgs in loggers]) + 3
    for ilogger in loggers:
        print(f'{ilogger:{loggerlen}} : {loggerDict[ilogger]}')
        for handler in loggerDict[ilogger].handlers:
            print(f'   {ilogger:{loggerlen - 3}} : {handler}')
