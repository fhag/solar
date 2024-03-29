# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
*class* used by *class* Car with method to manipulate car
"""
import logging
import time
import teslapy
import requests
from teslapy import VehicleError

logger = logging.getLogger(__name__)

__version__ = '1.1.11'
print(f'{__name__:40s} v{__version__}')


class Vehicle(teslapy.Vehicle):
    """Wrapper of teslapy.Vehicle to adapt to car module"""

    def is_mobile_access_enabled(self):
        '''True if mobile access allowed'''
        # Construct URL and send request
        uri = f"api/1/vehicles/{self['id']}/mobile_enabled"
        return self.tesla.request('GET', uri)['response']

    def get_vehicle_state(self):
        '''returns dict with vehicle state information'''
        self.wake_up()
        return self.get_vehicle_data()['vehicle_state']

    def get_drive_state(self) -> dict:
        '''returns dict with drive state information'''
        self.wake_up()
        return self.get_vehicle_data()['drive_state']

    def wake_up(self, last_wake_up=60) -> dict:
        '''Wake-up car'''
        timeout, interval, backoff = 100, 2, 1.2
        elapsed_sec = time.time() - getattr(self, "last_wake_up", 0)
        if elapsed_sec > last_wake_up:
            self['state'] = 'probably asleep'
            self.last_wake_up = time.time()
            logger.info('force wake up')
        logger.info(f'status {self["state"]!r} - {elapsed_sec:3.0f} sec old')
        try:
            self.sync_wake_up(timeout=timeout,
                              interval=interval,
                              backoff=backoff)
        except (VehicleError, requests.exceptions.RequestException) as err:
            logger.error(f'Unable to wake up car due to {err}')
            return {'state': 'ASLEEP'}
        logger.info(f'car "AWAKE" by wake_up with timeout={timeout!r} '
                    f'interval={interval!r} backoff={backoff!r}')
        return {'state': 'AWAKE'}

    @property
    def id(self):
        '''Vehicle Id: required for API calls'''
        return self['id']

    @property
    def display_name(self):
        '''Car name set by car driver'''
        return self['display_name']

    @property
    def vin(self):
        '''Allocated VIN (Vehicle Identification Number)'''
        return self['vin']

    @property
    def state(self):
        '''online or offline'''
        return self['state']

    def get_charge_state(self):
        '''get state of car with '''
        self.wake_up()
        return self.get_vehicle_data()['charge_state']

    def start_charging(self) -> dict:
        '''Start charging -> {'reason': '', 'result': True}'''
        self.wake_up()
        try:
            self.command('START_CHARGE')
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')

    def stop_charging(self) -> dict:
        '''Stop charging -> {'reason': '', 'result': True}'''
        self.wake_up()
        try:
            self.command('STOP_CHARGE')
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')

    def set_charge_limit(self, percentage: int) -> dict:
        '''Set charge level -> {'reason': '', 'result': True}'''
        self.wake_up()
        percentage = int(round(percentage, 0))
        if 50 <= percentage <= 100:
            kwargs = dict(percent=percentage)
            try:
                self.command('CHANGE_CHARGE_LIMIT', **kwargs)
            except (VehicleError, requests.exceptions.RequestException) as err:
                return dict(result=False, reason=str(err))
            else:
                return dict(result=True, reason='')
        logger.error('Charge limit outside allowed range')
        raise ValueError('Percentage should be between 50 and 100')

    def get_climate_state(self):
        return self.get_vehicle_data()['climate_state']

    def start_climate(self) -> dict:
        """start heating/air conditioning"""
        self.wake_up()
        try:
            self.command('CLIMATE_ON')
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')

    def stop_climate(self) -> dict:
        """Stop heating/air conditioning"""
        self.wake_up()
        try:
            self.command('CLIMATE_OFF')
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')

    def set_temperature(self,
                        driver_temperature,
                        passenger_temperature=None) -> dict:
        self.wake_up()
        if driver_temperature is None or passenger_temperature is None:
            settings = self.get_climate_state()
            if driver_temperature is None:
                driver_temperature = settings['driver_temp_setting']
            if passenger_temperature is None:
                passenger_temperature = settings['passenger_temp_setting']
        print(driver_temperature, passenger_temperature)
        kwargs = {'driver_temp': driver_temperature,
                  'passenger_temp': passenger_temperature}
        try:
            self.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', **kwargs)
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')

    def open_charge_port(self) -> dict:
        '''Open charge port of vehicle'''
        self.wake_up()
        try:
            self.command('CHARGE_PORT_DOOR_OPEN')
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')

    def close_charge_port(self) -> dict:
        '''Close charge port of vehicle'''
        self.wake_up()
        try:
            self.command('CHARGE_PORT_DOOR_CLOSE')
        except (VehicleError, requests.exceptions.RequestException) as err:
            return dict(result=False, reason=str(err))
        else:
            return dict(result=True, reason='')
