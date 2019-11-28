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

__version__ = '0.1.3'

LOGGER_FNAME = f'solar/logs/main_{datetime.now():%Y_%m_%d_%H%M}.log'
LOG_LEVEL = logging.DEBUG

FORMATTER = logging.Formatter(
        '%(asctime)s|%(filename)24s|%(levelname)7s|%(funcName)25s|' +
        '%(lineno)3d |%(message)s',
        "%d%b%y %H:%M.%S")
FILEHANDLER = logging.FileHandler(os.path.normpath(LOGGER_FNAME), mode='w')
FILEHANDLER.setLevel(LOG_LEVEL)
FILEHANDLER.setFormatter(FORMATTER)


class Filter():
    '''define my own filter'''

    def __init__(self, name=''):
        self.name = name
        self.nlen = len(name)

    def filter(self, record):
        '''create filter methode'''
        if self.nlen == 0:
            return True
        if self.name == record.name:
            return True
        if record.name.find(self.name, 0, self.nlen) != 0:
            return False
        return record.name[self.nlen] == "."
