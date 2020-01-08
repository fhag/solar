# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 08:49:35 2019

@author: annet
"""
import logging
from solar.charge import ChargeEV
from solar.definitions.logger_config import FILEHANDLER, Filter

print(__package__)
print(__name__)

NAME = 'solar'
logger = logging.getLogger(NAME)
logger.setLevel(logging.DEBUG)
logger.addHandler(FILEHANDLER)
FILTER = Filter(NAME)
logger.addFilter(FILTER)

logger.error(logger.handlers)
logger.error(logger.getChild(NAME))

__version__ = '0.1.6'

if __name__ == '__main__':
    print(f'main v{__version__}')

    def __init__(self):
        logger.info('init test')
        self.check_internet()
        logger.info('init test2')

    # ChargeEV.__init__ = __init__

    ev = ChargeEV()
    loggerDict = logging.root.manager.loggerDict
    loggers = [name for name in loggerDict if 'solar' in name]
    logger.critical(loggers)
    ev.run()
