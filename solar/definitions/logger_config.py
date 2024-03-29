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

__version__ = '1.1.42'
print(f'{__name__:40s} v{__version__}')

def list_loggers(loggers):
    loggerDict = logging.root.manager.loggerDict
    loggerlen = max([len(lgs) for lgs in loggers]) + 3
    for ilogger in loggers:
        if isinstance(loggerDict[ilogger], logging.Logger):
            for handler in loggerDict[ilogger].handlers:
                print(f'   {ilogger:{loggerlen - 3}} : {handler}')


LOGGER_FNAME = f'solar/logs/main_{datetime.now():%Y_%m_%d_%H%M}.log'
LOG_LEVEL = logging.DEBUG

FILEHANDLER = logging.FileHandler(os.path.normpath(LOGGER_FNAME), mode='w')
FILEHANDLER.setLevel(LOG_LEVEL)
FILE_FORMATTER = logging.Formatter(
    '%(asctime)s|%(filename)28s|%(levelname)8s|%(funcName)25s|' +
    '%(lineno)3d| %(message)s',
    "%d%b%y %H:%M.%S")
FILEHANDLER.setFormatter(FILE_FORMATTER)

CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(LOG_LEVEL)
CONSOLE_FORMATTER = logging.Formatter(
    '%(asctime)s|%(name)-28s:%(levelname)-8s|'
    '%(funcName)25s|%(lineno)3d|%(message)s')
CONSOLE_FORMATTER = FILE_FORMATTER  # fort testing
CONSOLE.setFormatter(CONSOLE_FORMATTER)


# solarlogger = logging.getLogger('solar')
# logger = logging.getLogger(__name__)
logger = logging.getLogger('solar')
logger.warning('Logger test ohne Filehandler - kein Fehler')


loggerDict = logging.root.manager.loggerDict
loggers = [name for name in loggerDict if 'solar' in name]
loggers.append('teslapy')
skip_loggers = ['solar.teslaapi', 'solar']
for logger_name in (set(loggers) - set(skip_loggers)):
    ilogger = loggerDict[logger_name]
    if isinstance(ilogger, logging.Logger):
        ilogger.setLevel(LOG_LEVEL)
        ilogger.handlers.clear()
        if logger_name not in skip_loggers:
            ilogger.addHandler(FILEHANDLER)
            ilogger.addHandler(CONSOLE)
logger.error('Logger test mit Filehandler - kein Fehler - 2')


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


