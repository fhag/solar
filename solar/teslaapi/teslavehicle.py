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
import teslapy
from teslapy import VehicleError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = '1.0.1'
print(f'teslavehicle.py v{__version__}')


class Vehicle(teslapy.Vehicle):
    """Wrapper of teslapy.Vehicle to adapt to car module"""

    def g(self, method, **kwargs):
        """ Wrapper method for vehicle command response error handling """
        uri = 'api/1/vehicles/{v.id}/{method}'
        response = self.tesla.request('get', uri, **kwargs)['response']
        return response['result']

    def is_mobile_access_enabled(self):
        '''True if mobile access allowed'''
        # Construct URL and send request
        uri = f"api/1/vehicles/{self['id']}/mobile_enabled"
        return self.tesla.request('GET', uri)['response']

    def get_vehicle_state(self):
        '''returns dict with vehicle state information'''
        return self.get_vehicle_data()['vehicle_state']

    def get_drive_state(self) -> dict:
        '''returns dict with drive state information'''
        return self.get_vehicle_data()['drive_state']

    def get_gui_settings(self) -> dict:
        '''Return GUI settings'''
        return self.get_vehicle_data()['gui_settings']

    def wake_up(self) -> dict:
        '''Wake-up car'''
        self.sync_wake_up()

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
        return self.get_vehicle_data()['charge_state']

    def start_charging(self) -> dict:
        '''Start charging -> {'reason': '', 'result': True}'''
        self.wake_up()
        try:
            return self.command('START_CHARGE')
        except VehicleError as err:
            logger.warning(err)
        return False

    def stop_charging(self) -> dict:
        '''Stop charging -> {'reason': '', 'result': True}'''
        try:
            return self.command('STOP_CHARGE')
        except VehicleError as err:
            logger.warning(err)
        return False

    def set_charge_limit(self, percentage: int):
        '''Set charge level -> {'reason': '', 'result': True}'''
        self.wake_up()
        percentage = round(percentage)
        if 50 <= percentage <= 100:
            kwargs = dict(percent=percentage)
            return self.command('CHANGE_CHARGE_LIMIT', **kwargs)
        logger.error('Charge limit outside allowed range')
        raise ValueError('Percentage should be between 50 and 100')

    def get_climate_state(self):
        return self.get_vehicle_data()['climate_state']

    def start_climate(self):
        """start heating/air conditioning"""
        self.wake_up()
        try:
            return self.command('CLIMATE_ON')
        except VehicleError as err:
            logger.warning(err)
        return False

    def stop_climate(self):
        """Stop heating/air conditioning"""
        self.wake_up()
        try:
            return self.command('CLIMATE_OFF')
        except VehicleError as err:
            logger.warning(err)
        return False

    def set_temperature(self, driver_temperature, passenger_temperature=None):
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
        return self.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', **kwargs)

        # return self._api_client.post(
        #     'vehicles/{}/command/set_temps'.format(self._vehicle_id),
        #     {'driver_temp': driver_temperature,
        #      'passenger_temp': passenger_temperature or driver_temperature}
        # )

    def open_charge_port(self):
        return self.command('CHARGE_PORT_DOOR_OPEN')

    def close_charge_port(self):
        return self.command('CHARGE_PORT_DOOR_CLOSE')
