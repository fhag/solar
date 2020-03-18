# -*- coding: utf-8 -*-
"""
Module containing different dataclasses with some default values.
Default values can be adapted to specific requirements.

"""
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta
from .access_data import HOME, E3DC_IP

__version__ = '0.1.38'
print(f'pvdataclasses.py v{__version__}')


@dataclass(frozen=False)
class PVStatus():
    '''Class to store state variables of PV system'''

    dtime: datetime = 0
    pv: int = 0
    pv1: int = 0
    pv2: int = 0
    soc: int = 0
    netz: int = 0
    akku: int = 0
    haus: int = 0
    ok: bool = False

    def __post_init__(self):
        '''initialize PVStatus'''
        self.pv = self.pv1 + self.pv2


@dataclass(frozen=False)
class Values():
    '''
    Trigger change only if state change is stable over all values

    maxlength of deque determines the how many times conditions must be met
    before triggering start or stop charging
    '''

    maxlength = 5
    values: deque = field(default=deque([False] * maxlength, maxlength))

    def __post_init__(self):
        '''Initialize empty value deque'''
        self.values = self.values.copy()

    def alltrue(self):
        '''Return True if all fields True'''
        return all(self.values)

    def allfalse(self):
        '''Return False if all fields False'''
        return not any(self.values)

    def anytrue(self):
        '''Return True if any value is True'''
        return any(self.values)


@dataclass(frozen=False)
class ChargeDefaults():
    '''Values and variables for system charging'''

    _defaults_path: str = 'solar/definitions/'
    _defaults_file: str = 'newdefaults.json'
    _fname: str = 'PV2_%Y_%m_%d.csv'
    _path: str = 'solar/data/'
    _log_to_file: bool = True
    soc_minimum_start: float = 20
    soc_minimum_stop: float = 20
    charge_state: bool = False
    old_netz_status: bool = False
    check_intervall: int = 60
    state: PVStatus = PVStatus()
    evathome_distance: float = 200  # in meter
    netz_vals: Values = Values()
    coll_vals: Values = Values()
    check_internet_timeout = 300  # in seconds
    e3dc_time_last_connection: float = 0
    e3dc_error_minimum_time: float = 15 * 60  # in seconds


@dataclass(frozen=False)
class ModbusDefaults():
    '''E3DC IP address, collect intervall and data fields to retain.'''

    _tcp_ip: str = E3DC_IP
    keys: list = field(default_factory=list)

    def __post_init__(self):
        '''defines values to keep'''
        self.keys = [40068, 40076, 40070, 40074, 40072, 40083, 40082]
        self.keys = [40036, 40052, 40068, 40076, 40070, 40074, 40072,
                     40083, 40082, 40084]


@dataclass(frozen=False)
class CarDefaults():
    '''Values and variables for system driving'''

    home: tuple
    _defaults_last_update: datetime = datetime(2019, 1, 1, 8, 0)
    _defaults_update_intervall: timedelta = timedelta(seconds=120)
    _athome_km: float = 0.200  # in kilometer
    _km2seconds_factor: float = 60
    seconds_btw_updates: int = 5 * 60
    ev_trials: int = 5
    evsoc_std: int = 70
    evsoc_limit_low: int = 80
    evstart_power_low: int = -3000
    evstop_power_low: int = 6000
    evsoc_limit_high: int = 90
    evstart_power_high: int = -7000
    evstop_power_high: int = 5000
    fname_charging_status: str = 'solar/data/charging_flag.csv'
    last_charge_limit_soc: int = 0
    charging_flag: bool = False
    sleep_between_func: int = 1
    __version__: str = ''


@dataclass(frozen=False)
class CarData(CarDefaults):
    '''State values of car'''

    timestamp: int = 0
    battery_level: int = 0
    charge_limit_soc: int = 0
    charge_limit_soc_max: int = 100
    charge_limit_soc_min: int = 50
    charge_limit_soc_std: int = 0
    charge_port_latch: str = ''
    charging_state: str = ''
    display_name: str = ''
    gps_as_of: int = 0
    latitude: float = 0
    longitude: float = 0
    native_latitude: float = 0
    native_longitude: float = 0
    odometer: float = 0
    power: int = 0
    shift_state: str = ''
    speed: float = 0
    state: str = ''
    time_to_full_charge: float = 0
    timestamp: int = 0
    vehicle_id: int = 0
    vin: str = ''
    data_ok: bool = False


    @property
    def location(self):
        '''Tuple with location'''
        return (self.latitude, self.longitude)

    @property
    def charging(self):
        '''True if car is charging'''
        return self.charging_state == 'Charging'


if __name__ == '__main__':
    p = PVStatus()
    v = Values()
    d = ChargeDefaults()
    m = ModbusDefaults()
    c = CarData(HOME)
    cd = CarDefaults(HOME)
    cd._defaults_update_intervall = timedelta(seconds=1)
    cd.defaults_update_values()
