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
import json
from collections import deque
from datetime import datetime
from .conftest import logger, chargeversion
from ..definitions.pvdataclasses import PVStatus, Values


__version__ = '0.1.55'
print(f'Running test_charge.py v{__version__}')

logger.info(f'Running test_charge.py v{__version__}')

testall = True
run_test_switch = pytest.mark.skipif(not testall, reason='tests accomplished')
run_test = pytest.mark.skipif(False, reason='run tests for debugging')
run_test_nyi = pytest.mark.skipif(True, reason='test not yet implemented')
not_implemented = pytest.mark.skipif(True,
                                     reason='function not yet implemented')


# ----------------------------------------------------------------------------
@run_test
def test__update_default_values(tmp_dir, ev):
    ev = copy.deepcopy(ev)
    # test for FileNotFoundError
    ev._update_default_values()
    # test for transfer of values
    fname = 'test.json'
    ev._defaults_path = ''
    ev._defaults_file = fname
    ev.soc_minimum_start = 21
    ev.soc_minimum_stop = 6
    ev.car.evsoc_std = 77
    jdata = {"soc_minimum_start": 22, "soc_minimum_stop": 7,
             "evsoc_std": 65, "__version__" : "2.2.2"}
    with open(fname, 'w') as file:
        file.write(json.dumps(jdata))
    ev.defaults_version = '1.1.1'
    ev._update_default_values()
    assert ev.soc_minimum_start == 22
    assert ev.soc_minimum_stop == 7
    assert ev.car.evsoc_std == 65
    # test for general Exception
    ev._defaults_file = fname + '|>:%&'
    with pytest.raises(OSError, match='Invalid'):
        ev._update_default_values()


@run_test_switch
def test__netz(ev):
    ev.car.current_power_start_stop = types.MethodType(
        lambda self: (-5000, 2000), ev)
    ev.state.netz = -3000
    ev.car.charging_flag = True
    n = 5
    ev.netz_vals = Values(deque([False] * n, n))
    assert sum([ev._netz() for i in range(n)]) == 1
    ev.car.charging_flag = False
    assert sum([ev._netz() for i in range(n)]) == 4


@run_test_switch
def test__housebattery_soc_ok(ev):
    ev.state.soc = 0.15
    ev.soc_minimum_start = 0.2
    ev.soc_minimum_stop = 0.05
    ev.car.charging_flag = False
    assert not ev._housebattery_soc_ok()
    ev.state.soc = 0.25
    assert ev._housebattery_soc_ok()

    ev.car.charging_flag = True
    ev.state.soc = 0.15
    assert ev._housebattery_soc_ok()
    ev.state.soc = 0.01
    assert not ev._housebattery_soc_ok()


@run_test_switch
def test_pvstateok(ev):
    print(ev.coll_vals.values, len(ev.coll_vals.values))
    ev.state.ok = True
    assert ev._pvstateok()
    ev.state.ok = False
    print()
    for i in range(len(ev.coll_vals.values) - 1):
        assert ev._pvstateok()
    assert not ev._pvstateok()


@run_test_switch
def test__sleep_time(ev):
    ev.check_intervall = 100
    now = datetime.now().timestamp()
    next_time = ev.check_intervall - now % ev.check_intervall
    assert ev._sleep_time() - next_time < 0.01


@run_test_switch
def test_get_new_values(ev):
    ev.modbus.collect = types.MethodType(lambda self: dict(ok=True), ev)
    ev.modbus.data2pvstate = types.MethodType(
        lambda self, x: PVStatus(
            **{k: v for k, v in x.items() if k in PVStatus.__dict__}),
        ev)
    ev.modbus.data2dict = types.MethodType(lambda self, x: x, ev)
    ev.modbus._tcp_ip = '1.0.0.127'
    ev.save_to_csv = types.MethodType(lambda self, x: True, ev)
    ev.state = ev.get_new_values()
    print(ev.state)
    assert ev.state.ok
    ev.modbus.collect = types.MethodType(lambda self: dict(ok=False), ev)
    ev.state = ev.get_new_values()
    assert not ev.state.ok
    # E3DC interruption
    ev.modbus.collect = types.MethodType(lambda self: self.no_attribute, ev)
    ev.e3dc_time_last_connection = time.time()
    ev.state = ev.get_new_values()
    ev.state = ev.get_new_values()
    ev.state = ev.get_new_values()
    ev.state = ev.get_new_values()
    time.sleep(0.001)
    assert time.time() - ev.e3dc_time_last_connection > 0
    # E3DC error (interruption longer than self.e3dc_error_minimum_time
    ev.e3dc_time_last_connection = time.time() - 2 * ev.e3dc_error_minimum_time
    ev.state = ev.get_new_values()
    assert ev.e3dc_time_last_connection == 0
    # E3DC error repeated
    ev.state = ev.get_new_values()
    assert ev.e3dc_time_last_connection == 0
    # E3DC connection reestablished
    ev.modbus.collect = types.MethodType(lambda self: dict(ok=False), ev)
    ev.e3dc_time_last_connection = 0
    ev.state = ev.get_new_values()
    assert ev.e3dc_time_last_connection == pytest.approx(time.time(), abs=0.1)
    ev.state = ev.get_new_values()
    ev.state = ev.get_new_values()
    ev.state = ev.get_new_values()
    ev.state = ev.get_new_values()
    assert ev.e3dc_time_last_connection == pytest.approx(time.time(), abs=0.1)


@run_test_switch
def test_filename(ev):
    ev._path = 'test/'
    ev._fname = 'P123%Y'
    fname = datetime.now().strftime('test/P123%Y')
    assert ev.filename == fname


@run_test_switch
def test_save_to_csv(tmp_dir, ev):
    ev = copy.deepcopy(ev)
    ev._path = ''
    dict2save = dict(Netz=-1000, PV=200, SNr_t='hallo')
    print(ev.filename)
    ev.save_to_csv(dict2save)
    dict2save = dict(Netz=100, PV=300, SNr_t='hallo4')
    ev.save_to_csv(dict2save)
    dict2save = dict(Netz=100, PV=400, SNr_t='hallo3')
    ev.save_to_csv(dict2save)
    dict2save = dict(Netz=100, PV=500, SNr_t='hallo2')
    ev.save_to_csv(dict2save)
    dict2save = dict(Netz=100, PV=600, SNr_t='hallo1')
    ev.save_to_csv(dict2save)
    print(ev.filename)

    os.chmod(ev.filename, stat.S_IREAD)
    ev.save_to_csv(dict2save)
    os.chmod(ev.filename, stat.S_IWRITE)


@run_test_switch
def test_check_internet(ev):
    ev = copy.deepcopy(ev)
    assert ev.check_internet(sleeptime=0.01)

    ev.check_internet_timeout = 1
    with pytest.raises(KeyboardInterrupt, match='No internet'):
        ev.check_internet(sleeptime=0.01, www='test')


@run_test_switch
def test_run(ev):

    def _sleep_time(self):
        raise TypeError('test1')
    ev._sleep_time = types.MethodType(_sleep_time, ev)
    assert ev.run() is None

    def _sleep_time(self):
        raise IndexError('test2')
    ev._sleep_time = types.MethodType(_sleep_time, ev)
    ev.get_new_values = types.MethodType(lambda self: PVStatus(ok=False), ev)
    assert ev.run() is None

    ev.car.func.ts = [{'timestamp': i*1000} for i in range(1, 70)]
    ev.start_charging = types.MethodType(lambda self: True, ev)
    ev.stop_charging = types.MethodType(lambda self: True, ev)
    ev.get_new_values = types.MethodType(lambda self: PVStatus(ok=True), ev)
    ev._netz = types.MethodType(lambda self: True, ev)
    ev._housebattery_soc_ok = types.MethodType(lambda self: True, ev)
    ev._pvstateok = types.MethodType(lambda self: True, ev)
    ev._car_at_home = types.MethodType(lambda self: True, ev)
    ev.car.charging_flag = True
    assert ev.run() is None

    ev.car.charging_flag = False
    assert ev.run() is None

    ev._car_at_home = types.MethodType(lambda self: False, ev)
    ev.car.charging_flag = True
    ev.car.func.ts = [{'timestamp': i*1000} for i in range(1, 7)]
    assert ev.run() is None

    ev.car.charging_flag = False
    assert ev.run() is None


def test_final():
    txt = f'test passed charge.py v{chargeversion}|{__name__!r} v{__version__}'
    logger.info(txt)
