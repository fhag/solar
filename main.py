# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 08:49:35 2019

@author: annet
"""
import logging
from solar.charge import ChargeEV
from solar.definitions.logger_config import FILEHANDLER, CONSOLE, LOG_LEVEL

NAME = 'solar'
logger = logging.getLogger(NAME)

__version__ = '1.0.2'
print(__version__)

if __name__ == '__main__':
    print(f'main v{__version__}')
    ev = ChargeEV()
    ev.run()
