# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 08:49:35 2019

@author: annet
"""
import logging
from solar.charge import ChargeEV
from solar.definitions.logger_config import FILEHANDLER, Filter, LOG_LEVEL

NAME = 'solar'
logger = logging.getLogger(NAME)
logger.setLevel(LOG_LEVEL)
logger.addHandler(FILEHANDLER)
FILTER = Filter(NAME)
logger.addFilter(FILTER)


__version__ = '1.0.0'

if __name__ == '__main__':
    print(f'main v{__version__}')
    ev = ChargeEV()
    loggerDict = logging.root.manager.loggerDict
    loggers = [name for name in loggerDict if 'solar' in name]
    logger.debug(loggers)
    ev.run()
