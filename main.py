# -*- coding: utf-8 -*-
"""
Main program to start solar power monitoring and charging car if enough
solar power available

@author: gfi
"""
import logging
from solar.charge import ChargeEV
from solar.definitions.logger_config import logger


NAME = 'solar'
logger.setLevel(logging.DEBUG)

__version__ = '1.0.4'
print(f'{__name__:40s} v{__version__}')

if __name__ == '__main__':
    ev = ChargeEV()
    ev.run()
