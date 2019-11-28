# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 13:59:26 2019

@author: annet
"""
import logging
import os
from datetime import datetime

__version__ = '0.1.2'

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
