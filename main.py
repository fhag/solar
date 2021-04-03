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
logger.addHandler(FILEHANDLER)
CONSOLE.setLevel(logging.WARNING)
logger.addHandler(CONSOLE)

__version__ = '1.0.1'

if __name__ == '__main__':
    print(f'main v{__version__}')
    ev = ChargeEV()
    loggerDict = logging.root.manager.loggerDict
    loggers = [name for name in loggerDict if 'solar' in name]
    loggers.append('teslapy')
    for ilogger in loggers:
        loggerDict[ilogger].setLevel(LOG_LEVEL)
    ev.run()
