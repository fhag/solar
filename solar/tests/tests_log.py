# -*- coding: utf-8 -*-
"""
Logger for Atelegram

Created on Tue Nov 13 08:34:14 2018
@author: gfi
"""
import logging
import datetime
__version__ = '0.1.55'


LOG_LEVEL = logging.DEBUG
LOGGER_NAME = 'solar'
LOGGER_FNAME = f'solar/logs/pytest_{datetime.datetime.now():%Y_%m_%d_%H%M}.log'

logger = logging.Logger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)
handler = logging.FileHandler(LOGGER_FNAME, mode='w')
#handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s|%(filename)24s|%(levelname)7s|%(funcName)26s|' +
    '%(lineno)3d|%(process)d|%(thread)d|%(message)s',
    "%d%b%y %H:%M.%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


logger.info('*' * 80)
logger.info('Logger defined in %s', __file__)
logger.info('Name : %s', __name__)
logger.info('Package: %s', __package__)
logger.info('Logger filename: %s', LOGGER_FNAME)
logger.info('*' * 80)


if __name__ == '__main__':
    logger.info('test passed')
