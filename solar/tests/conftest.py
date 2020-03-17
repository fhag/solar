# -*- coding: utf-8 -*-
''' test all functions '''
import os
import pytest
import types
import numpy as np
import shutil
import time
from ..car import Car
from ..car import __version__ as carversion
from ..charge import ChargeEV
from ..charge import __version__ as chargeversion
from ..definitions.pvdataclasses import PVStatus
from .tests_log import logger

__version__ = '0.1.56'

EMAIL, PW, VIN, HOME = 'test', 'test', '123', (12, 34)


ftext = f'testing car.py:v{carversion} and charge.py:v{chargeversion}'
logger.info(ftext)


@pytest.fixture(scope='function')
def tmp_dir():
    ''' creates am empty directory for testing
        returns directory name
    '''
    _emptyTmpDir = '_tmpe' + str(np.random.randint(10000, 99999)) + '/'
    os.makedirs(_emptyTmpDir)
    # ~ os.makedirs(_emptyTmpDir + 'data/')
    os.chdir(_emptyTmpDir)
    logger.info(f'tmp_dir: {_emptyTmpDir!r} initialised')
    yield _emptyTmpDir
    stime = time.time()
    os.chdir('..')
    shutil.rmtree(_emptyTmpDir)
    logger.info(f'tmp_dir removed: {time.time() - stime:.3f} sec')


@pytest.fixture(scope='function')
def car():
    ''' temp ChargeEV instance'''
    class Test_func():
        ts = [{'timestamp': i*1000} for i in range(1, 15)]
        bool_charge_limit = True
        response_start_charging = dict(result=True, reason='alles ok')
        response_stop_charging = dict(result=True, reason='alles ok')
        response_set_charge_limit = dict(result=True, reason='alles ok')

        def wake_up(self):
            return dict(state='online')

        def get_charge_state(self):
            return self.ts.pop(0)

        def get_drive_state(self):
            return self.ts.pop(0)

        def get_climate_state(self):
            return self.ts.pop(0)

        def get_vehicle_state(self):
            return self.ts.pop(0)

        def set_charge_limit(self, climit):
            self.charge_limit_soc = climit
            return self.response_set_charge_limit

        def start_charging(self):
            return self.response_start_charging

        def stop_charging(self):
            return self.response_stop_charging
    actual_init = Car.__init__
    Car.__init__ = lambda *args, **kwargs: None
    func = Test_func()
    Car.func = func
    car = Car(EMAIL, PW, VIN, HOME)
    car.home = HOME
    car.latitude, car.longitude = HOME
    car.update_values = types.MethodType(lambda *args, **kwargs: True, car)
    car.charge_limit_soc_min, car.charge_limit_soc_max = 50, 100
    car.fname_charging_status = 'data/temp.csv'
    car.send_status = lambda x: True
#    from send_status import send_status
#    car.send_status = send_status
    yield car
    Car.__init__ = actual_init


@pytest.fixture(scope='function')
def ev(car):
    ''' temp ChargeEV instance'''
    class ChargeModbus():
        ok = True

        def run_collect(self):
            return PVStatus(ok=self.ok)
    ChargeEV.__init__ = lambda *args, **kwargs: None
    ChargeEV.send_status = lambda *args, **kwargs: None
    ev = ChargeEV()
    ev.modbus = ChargeModbus()
    ev.car = car
    yield ev
