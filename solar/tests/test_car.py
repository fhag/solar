# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 18:49:25 2019

@author: annet
"""
import pytest
import types
import time
import copy
import os
import stat
from solar.teslaapi import AuthenticationError, ApiError
from solar.tests.conftest import logger, HOME, carversion

# pytest -v -rs tests/test_charge.py
# pytest --cov-report html:cov_html --cov=arequests tests/test_charge.py

__version__ = '0.1.54'

print(f'Running test_car.py v{__version__}')
logger.info(f'Running test_car.py v{__version__}')

testall = True
run_test_switch = pytest.mark.skipif(not testall, reason='tests accomplished')
run_test = pytest.mark.skipif(False, reason='run tests for debugging')
run_test_nyi = pytest.mark.skipif(True, reason='test not yet implemented')

# pytest --cov=solar --cov-report html solar/tests/

# -----------------------------------------------------------------------------
@run_test_switch
def test__km_from_home(car):
    car.latitude, car.longitude = HOME
    assert car._km_from_home() == 0.0
    car.latitude, car.longitude = (11, 33)
    assert round(car._km_from_home(), 4) == 155.6818


@run_test_switch
def test__km_to_seconds(car):
    car.latitude, car.longitude = HOME
    assert car._km_to_seconds() == 0.0
    car.latitude, car.longitude = (11, 33)
    assert round(car._km_to_seconds(), 4) == 9340.9077


@run_test_switch
def test__charging_needed(car):
    car.evsoc_limit_high = 90
    car.charge_limit_soc = 70
    car.battery_level = 80
    assert car._charging_needed()
    car.battery_level = 85
    assert car._charging_needed()
    car.battery_level = 93
    assert not car._charging_needed()
    car.charge_limit_soc = 95
    assert car._charging_needed()


@run_test_switch
def test__get_charging_status(tmp_dir, car):
    car = copy.deepcopy(car)
    car.send_status = types.MethodType(lambda self, x: x, car)
    car.fname_charging_status = 'test2.csv'
    car._get_charging_status()


@run_test_switch
def test_current_power_start_stop(car):
    car.battery_level = 50
    car.evsoc_limit_low = 60
    low = (100, 200)
    high = (300, 400)
    car.evstart_power_low, car.evstop_power_low = low
    car.evstart_power_high, car.evstop_power_high = high
    assert car.current_power_start_stop() == low
    car.battery_level = 70
    assert car.current_power_start_stop() == high


@run_test_switch
def test_athome(car):
    home = (12, 22)
    stillathome = (12.0001, 21.999)
    notathome = (13, 22)
    car._athome_km: float = 0.200  # in kilometer
    car.home = home
    car.latitude, car.longitude = home
    assert car.athome()
    car.latitude, car.longitude = stillathome
    assert car.athome()
    car.latitude, car.longitude = notathome
    print(car.athome, car._km_from_home())
    assert not car.athome()


@run_test_switch
def test__try_start_charging(car):
    car.ev_trials = 3
    car.sleep_between_func = 0
    response = dict(result=True, reason='test')
    car.func.start_charging = types.MethodType(lambda self: response, car.func)
    assert car._try_start_charging()
    response = dict(result=False, reason='test')
    assert car._try_start_charging() is False


@run_test_switch
def test__try_stop_charging(car):
    car.ev_trials = 3
    car.sleep_between_func = 0
    response = dict(result=False, reason='not_charging')
    car.func.stop_charging = types.MethodType(lambda self: response, car.func)
    assert car._try_stop_charging()
    response = dict(result=False, reason='test')
    assert car._try_stop_charging() is False


@run_test_switch
def test__try_set_charge_limit(car):
    car.ev_trials = 3
    car.sleep_between_func = 0
    car.evsoc_std = 66
    car.charge_limit_soc_min, car.charge_limit_soc_max = 50, 100
    response = dict(result=False, reason='already_charging')
    car.func.set_charge_limit = types.MethodType(
            lambda self, x: response, car.func)
    assert car._try_set_charge_limit(77)
    assert car._try_set_charge_limit('test')

    response = dict(result=False, reason='not_charging')
    assert car._try_set_charge_limit(88) is False

    def set_charge_limit(self, x):
        assert 0

    car.func.set_charge_limit = types.MethodType(set_charge_limit, car.func)
    assert car._try_set_charge_limit(77) is False


@run_test_switch
def test__try_wake_up(car):
    response = dict(state='online')
    car.func.wake_up = types.MethodType(lambda self: response, car.func)
    car.sleep_between_func = 0.01
    assert car._try_wake_up()
    response = dict(state='asleep')
    assert not car._try_wake_up()


@run_test_switch
def test_update_car(car):
    car = copy.deepcopy(car)
    resp = dict(timestamp=1234)
    car._try_wake_up = types.MethodType(lambda self: resp, car)
    car.func.get_charge_state = types.MethodType(lambda self: resp, car.func)
    car.func.get_drive_state = types.MethodType(lambda self: resp, car.func)
    car.func.get_climate_state = types.MethodType(lambda self: resp, car.func)
    car.func.get_vehicle_state = types.MethodType(lambda self: resp, car.func)
    assert car.update_car()

    def _try_wake_up(self):
        raise ApiError('intentional error')
    car._try_wake_up = types.MethodType(_try_wake_up, car)
    assert car.update_car() is False

    def _try_wake_up(self):
        raise ValueError('intentional ValueError')
    car._try_wake_up = types.MethodType(_try_wake_up, car)
    assert car.update_car() is False


@run_test_switch
def test_update_car_if(car):
    car = copy.deepcopy(car)
    car.timestamp = time.time()
    car.battery_level = 60
    resp = dict(data_ok=True)
    car.update_car = types.MethodType(lambda self: resp, car)
    seconds = 100
    car._km_to_seconds = types.MethodType(lambda self: seconds, car)
    car.shift_state = 'D'
    assert car.update_car_if() is False
    car.shift_state = 'P'
    assert car.update_car_if() is False
    car.seconds_btw_updates = 100
    seconds = 0
    assert car.update_car_if() is False

    car.timestamp -= 1000
    car.data_ok = True
    assert car.update_car_if()
    print(car.data_ok)


@run_test_switch
def test__get_new_soc_limit(car):
    car.charge_limit_soc = 80
    car.evsoc_limit_high = 90
    assert car._get_new_soc_limit() == 90
    car.charge_limit_soc = 95
    assert car._get_new_soc_limit() == 95


@run_test_switch
def test__save_and_get_charging_status(tmp_dir, car):
    car = copy.deepcopy(car)
    car.send_status = types.MethodType(lambda self, x: x, car)
    car.fname_charging_status = 'test.csv'
    car.charging_flag, car.last_charge_limit_soc = True, 60
    car._save_charging_status()
    assert os.path.exists(car.fname_charging_status)

    car.charging_flag, car.last_charge_limit_soc = 123, 456
    car._get_charging_status()
    assert car.charging_flag
    assert car.last_charge_limit_soc == 60
    car.charging_flag, car.last_charge_limit_soc = False, 60
    car._save_charging_status()
    car.charging_flag, car.last_charge_limit_soc = 123, 456
    car._get_charging_status()
    assert not car.charging_flag
    assert car.last_charge_limit_soc == 60
    car.charging_flag, car.last_charge_limit_soc = True, 99
    car._save_charging_status()
    car.charging_flag, car.last_charge_limit_soc = 123, 456
    car._get_charging_status()
    assert car.charging_flag
    assert car.last_charge_limit_soc == 99

    #  provoke PermissionError
    fname = car.fname_charging_status

    os.chmod(fname, stat.S_IREAD)
    car._save_charging_status()
    os.chmod(fname, stat.S_IWRITE)


@run_test_switch
def test__start_car_charging(car):
    car = copy.deepcopy(car)

    #  settings for success --> True
    car._try_wake_up = types.MethodType(lambda self: True, car)
    car._try_set_charge_limit = types.MethodType(lambda self, x: True, car)
    car._try_start_charging = types.MethodType(lambda self: True, car)
    car.charging_flag = False

    assert car._start_car_charging()
    #  setting for False without Exception --> False
    car.charging_flag = True
    assert car._start_car_charging() is False

    # settings for ApiError --> False
    def _try_wake_up(self):
        raise ApiError('Inentional ApiError')
    car._try_wake_up = types.MethodType(_try_wake_up, car)
    assert car._start_car_charging() is False

    # settings for AuthentificationError --> AuthentificationError
    def _try_wake_up(self):
        raise AuthenticationError('Intentional AuthenticationError')
    car._try_wake_up = types.MethodType(_try_wake_up, car)
    with pytest.raises(AuthenticationError, match='check credentials'):
        car._start_car_charging()


@run_test_switch
def test__stop_car_charging(car):
    car = copy.deepcopy(car)

    #  settings for success --> True
    car._try_wake_up = types.MethodType(lambda self: True, car)
    car._try_set_charge_limit = types.MethodType(lambda self, x: True, car)
    car.last_charge_limit_soc = 50
    car.charging_flag = True
    car._try_stop_charging = types.MethodType(lambda self: True, car)
    car._save_charging_status = types.MethodType(lambda self: True, car)
    car._reset_timestamp = types.MethodType(lambda self: True, car)
    assert car._stop_car_charging()
    #  settings for no success
    car.charging_flag = False
    assert car._stop_car_charging() is False

    # settings for ApiError --> False
    def _try_wake_up(self):
        raise ApiError('Inentional ApiError')
    car._try_wake_up = types.MethodType(_try_wake_up, car)
    assert car._stop_car_charging() is False

    # settings for AuthentificationError --> AuthentificationError
    def _try_wake_up(self):
        raise AuthenticationError('Intentional AuthenticationError')
    car._try_wake_up = types.MethodType(_try_wake_up, car)
    with pytest.raises(AuthenticationError, match='check credentials'):
        car._stop_car_charging()


@run_test_switch
def test__reset_timestamp(car):
    car.timestamp = 10000
    car.seconds_btw_updates = 300
    assert car._reset_timestamp() is None
    assert car.timestamp == 9700


@run_test_switch
def test_start_charging(car):
    car = copy.deepcopy(car)
    car.sleep_between_func = 0
    car.update_car_if = types.MethodType(lambda self: True, car)
    car._start_car_charging = types.MethodType(lambda self: True, car)
    car.stop_charging = types.MethodType(lambda self: True, car)
    # test conditions=True and charging_flag=True
    car.data_ok = True
    car.latitude, car.longitude = car.home
    car.charge_port_latch = 'Engaged'
    car.battery_level, car.charge_limit_soc = 50, 90
    car.charging_flag = True
    assert car.start_charging() == (True, True)
    # test conditions=True and charging_flag=False
    car.charging_flag = False
    assert car.start_charging() == (True, False)
    # test conditions=False and charging_flag=True
    car.charging_flag = True
    car.data_ok = False
    assert car.start_charging() == (False, True)

    # test conditions=False and charging_flag=False
    car.charging_flag = False
    car.stop_charging = types.MethodType(lambda self: False, car)
    assert car.start_charging() == (False, False)


@run_test_switch
def test_stop_charging(car):
    car = copy.deepcopy(car)
    car._stop_car_charging = types.MethodType(lambda self: True, car)
    # test : stop charging
    car.charging_flag = True
    assert car.stop_charging()
    # test : do nothing
    car.charging_flag = False
    assert not car.stop_charging()


def test_final():
    txt = f'test passed car.py v{carversion}|{__name__!r} v{__version__}'
    logger.info(txt)
