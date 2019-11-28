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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = '0.0.8'
print(f'teslavehicle.py v{__version__}')

STATE_VENT = 'vent'
STATE_CLOSE = 'close'


class Vehicle():
    def __init__(self, api_client, vehicle):
        '''Initialise Vehicle class'''
        self._api_client = api_client
        self._vehicle = vehicle
        self._vehicle_id = vehicle['id']
        logger.info('Vehicle class initialised')

    def is_mobile_access_enabled(self):
        '''True if mobile access allowed'''
        return self._api_client.get(
                'vehicles/{}/mobile_enabled'.format(self.id))

    def get_vehicle_state(self):
        '''returns dict with vehicle state information'''
        return self._api_client.get(
                'vehicles/{}/data_request/vehicle_state'.format(self.id))

    def get_drive_state(self) -> dict:
        '''returns dict with drive state information'''
        return self._api_client.get(
                'vehicles/{}/data_request/drive_state'.format(self.id))

    def get_gui_settings(self) -> dict:
        '''Return GUI settings'''
        return self._api_client.get(
                'vehicles/{}/data_request/gui_settings'.format(self.id))

    def wake_up(self) -> dict:
        '''Wake-up car'''
        return self._api_client.post(
                'vehicles/{}/wake_up'.format(self.id))

    @property
    def id(self):
        '''Vehicle Id: required for API calls'''
        return self._vehicle['id']

    @property
    def display_name(self):
        '''Car name set by car driver'''
        return self._vehicle['display_name']

    @property
    def vin(self):
        '''Allocated VIN (Vehicle Identification Number)'''
        return self._vehicle['vin']

    @property
    def state(self):
        '''online or offline'''
        return self._vehicle['state']

    def get_charge_state(self):
        '''get state of car with '''
        return self._api_client.get(
                'vehicles/{}/data_request/charge_state'.format(
                        self._vehicle_id))

    def start_charging(self) -> dict:
        '''Start charging -> {'reason': '', 'result': True}'''
        return self._api_client.post(
                'vehicles/{}/command/charge_start'.format(self._vehicle_id))

    def stop_charging(self) -> dict:
        '''Stop charging -> {'reason': '', 'result': True}'''
        return self._api_client.post(
                'vehicles/{}/command/charge_stop'.format(self._vehicle_id))

    def set_charge_limit(self, percentage: int):
        '''Set charge level -> {'reason': '', 'result': True}'''
        percentage = round(percentage)
        if 50 <= percentage <= 100:
            return self._api_client.post(
                    'vehicles/{}/command/set_charge_limit'.format(
                            self._vehicle_id), {'percent': percentage})

            logger.error('Charge limit outside allowed range')
            raise ValueError('Percentage should be between 50 and 100')

    def get_climate_state(self):
        return self._api_client.get(
                'vehicles/{}/data_request/climate_state'.format(
                        self._vehicle_id))

    def start_climate(self):
        return self._api_client.post(
                'vehicles/{}/command/auto_conditioning_start'.format(
                        self._vehicle_id))

    def stop_climate(self):
        return self._api_client.post(
                'vehicles/{}/command/auto_conditioning_stop'.format(
                        self._vehicle_id))

    def set_temperature(self, driver_temperature, passenger_temperature=None):
        return self._api_client.post(
            'vehicles/{}/command/set_temps'.format(self._vehicle_id),
            {'driver_temp': driver_temperature,
             'passenger_temp': passenger_temperature or driver_temperature}
            )

    def _set_sunroof_state(self, state):
        return self._api_client.post(
            'vehicles/{}/command/sun_roof_control'.format(self._vehicle_id),
            {'state': state}
            )

    def _vent_sunroof(self):
        return self._set_sunroof_state(STATE_VENT)

    def _close_sunroof(self):
        return self._set_sunroof_state(STATE_CLOSE)

    def flash_lights(self):
        return self._api_client.post(
                'vehicles/{}/command/flash_lights'.format(self._vehicle_id))

    def honk_horn(self):
        return self._api_client.post(
                'vehicles/{}/command/honk_horn'.format(self._vehicle_id))

    def open_charge_port(self):
        return self._api_client.post(
                'vehicles/{}/command/charge_port_door_open'.format(
                        self._vehicle_id))
