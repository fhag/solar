# -*- coding: utf-8 -*-
"""
Main program to start solar power monitoring and charging car if enough
solar power available

@author: gfi
"""
import logging
import time
from solar.charge import ChargeEV
from solar.definitions.logger_config import logger


NAME = 'solar'
logger.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

__version__ = '1.0.5'
print(f'{__name__:40s} v{__version__}')

if __name__ == '__main__':
    ev = ChargeEV()
    # ev.run()
    logger.warning(f'Main program terminated at {time.asctime()}')
    logger.warning('=' * 100)
