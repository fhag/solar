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
*class* Car contains all Tesla car data and methods to access car
Methods for self.func are imported from *class* Vehicle in module
teslaapiclient.teslavehicle
"""

import math
import time
import os
import csv
import json
import logging
from solar.teslaapi import TeslaApiClient, AuthenticationError, ApiError
from solar.definitions.pvdataclasses import CarData
from solar.definitions.access_data import EMAIL, PW, VIN, HOME
from solar.send_status import send_status

__version__ = '0.1.57'
print(f'car v{__version__}')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Car(CarData):
    '''
    Dataclass containing all Tesla car status and data collected from vehicle

    * methods to collect data, update data and start and stop charging
    * checks credentials and correct vin at startup
    * home = (latitude, longitude) of car's home location
    '''

    def __init__(self, email, pw, vin, home):
        super().__init__(home)
        self.__version__ = __version__
        logger.info('car.py v%s', __version__)
        try:
            self.client = TeslaApiClient(email, pw)
            self.vehicles = self.client.list_vehicles()
            self.func = [v for v in self.vehicles if v.vin == vin][0]
            self.send_status = send_status
            self._get_charging_status()
        except IndexError:
            ftext = 'Unknown car with VIN:%s' % vin
            logger.critical(ftext)
            send_status(ftext)
        except AuthenticationError as err:
            logger.critical(err)
            send_status(err)
        else:
            ftext = f' Car v{__version__} for {vin} initialized and started '
            ftext = ftext.center(100, '-')
            print(ftext)
            logger.info(ftext)

    def _km_from_home(self) -> float:
        """
        Calculate the Haversine distance.

        * origin : tuple of float (lat, long)
        * destination : tuple of float (lat, long)
        * -> distance_in_km : float
        """
        lat1, lon1 = self.location
        lat2, lon2 = self.home
        radius = 6371  # m
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        alpha = (math.sin(dlat / 2) * math.sin(dlat / 2) +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlon / 2) * math.sin(dlon / 2))
        charlie = 2 * math.atan2(math.sqrt(alpha), math.sqrt(1 - alpha))
        return radius * charlie

    def _km_to_seconds(self) -> float:
        '''Transform distance into waittime'''
        return self._km_from_home() * self._km2seconds_factor

    def current_power_start_stop(self) -> tuple:
        '''
        Get current start and stop power limits subject tocar charging level.

        Levels are defined in *cardefaults.json*
        '''
        if self.battery_level < self.evsoc_limit_low:
            return self.evstart_power_low, self.evstop_power_low
        return self.evstart_power_high, self.evstop_power_high

    def athome(self) -> bool:
        '''Return True if car is at home'''
        return self._km_from_home() < self._athome_km

    def _try_start_charging(self) -> bool:
        '''start_until car online'''
        for _ in range(self.ev_trials):
            response = self.func.start_charging()
            if response['result'] or response['reason'] == 'charging':
                return True
            time.sleep(self.sleep_between_func)
        ftext = f'Could not start_charging car: {response}'
        logger.warning(ftext)
        return False

    def _try_stop_charging(self) -> bool:
        '''stop_charging until car online'''
        for _ in range(self.ev_trials):
            response = self.func.stop_charging()
            if response['result'] or response['reason'] == 'not_charging':
                return True
            time.sleep(self.sleep_between_func)
        ftext = f'Could not stop_charging: {response}'
        logger.warning(ftext)
        return False

    def _try_set_charge_limit(self, charge_limit):
        '''remember old limit and set new limit with exception handling'''
        try:
            _charge_limit = int(float(charge_limit))
        except ValueError:
            _charge_limit = self.evsoc_std
        _charge_limit = min(self.charge_limit_soc_max, _charge_limit)
        _charge_limit = max(_charge_limit, self.charge_limit_soc_min)
        try:
            for _ in range(self.ev_trials):
                response = self.func.set_charge_limit(_charge_limit)
                condition = any([response['result'],
                                 'already' in response['reason']])
                if condition:
                    logger.debug('New soc limit=%s   -> %s', _charge_limit,
                                 response)
                    self._reset_timestamp()
                    return True
                time.sleep(self.sleep_between_func)
        except (AssertionError, ApiError,
                AuthenticationError, json.JSONDecodeError) as err:
            logger.warning(err, exc_info=False)
            return False
        else:
            ftext = f'NOT successful: {response}'
            logger.error(ftext)
            return False

    def _try_wake_up(self) -> dict:
        '''wake up car until car online'''
        for _ in range(self.ev_trials):
            response = self.func.wake_up()
            if response['state'].upper() != 'ASLEEP':
                return response
            time.sleep(self.sleep_between_func)
        ftext = f'Could not wake up car: {response}'
        logger.warning(ftext)
        return dict()

    def update_car(self) -> bool:
        '''Update car instance with all car data and timestamp'''
        timestamps = list()
        try:
            attempt = 'wake_up'
            data = self._try_wake_up()
            attempt = 'get_charge_state'
            data.update(self.func.get_charge_state())
            timestamps.append(data['timestamp'])
            attempt = 'get_drive_state'
            data.update(self.func.get_drive_state())
            timestamps.append(data['timestamp'])
            attempt = 'get_climate_state'
            data.update(self.func.get_climate_state())
            timestamps.append(data['timestamp'])
            attempt = 'get_vehicle_state'
            data.update(self.func.get_vehicle_state())
            timestamps.append(data['timestamp'])
            data.update(dict(data_ok=True))
            data.update(dict(timestamp=max(timestamps)/1000))
            self.data = data  # for debugging
            logger.debug(data)
            keys = self.__dict__.keys()
            for key, value in data.items():
                if key in keys:
                    setattr(self, key, value)
            logger.debug('Car data successfully updated:%s', self)
            return True
        except (ApiError, AuthenticationError) as err:
            ftext = f'Unable to get car_state due to={err} for {attempt!r}'
            logger.warning('%s |%s', ftext, self)
            self.__dict__.update(dict(data_ok=False))
            return False
        except Exception as err:
            ftext = f'Unexpected Exception due to={err} for {attempt!r}'
            logger.critical('%s |%s', ftext, self, exc_info=True)
            self.__dict__.update(dict(data_ok=False))
            return False

    def update_car_if(self) -> bool:
        '''
        Conditional update of car instance with all car data  and timestamp if:

        * car is driving or

        * car is close enough and last recent update is old enough
        '''
        elapsed_seconds = max(0, time.time() - self.timestamp)
        not_driving = self.shift_state != 'D'
        ftext = ('shift_state=%s, !driving=%s, battery_level=%2.0f' %
                 (self.shift_state, not_driving, self.battery_level))
        if elapsed_seconds < self._km_to_seconds() and not_driving:
            logger.debug('Car too far away: %.1f sec, elapsed=%.1f sec| %s',
                         self._km_to_seconds(), elapsed_seconds, ftext)
            return False
        if elapsed_seconds < self.seconds_btw_updates and not_driving:
            logger.debug('Last update too recent:%5.0f sec vs. %6.0f sec| %s',
                         self.seconds_btw_updates, elapsed_seconds, ftext)
            return False
        logger.debug('Before update_car:  %s', ftext)
        self.update_car()
        if self.data_ok:
            logger.debug('Update_car successful: %s', ftext)
            return True
        logger.warning('Update_car failed: %s', ftext)
        return False

    def _charging_needed(self) -> bool:
        '''True if charging needed'''
        fully_charged = max(self.evsoc_limit_high, self.charge_limit_soc)
        return self.battery_level < fully_charged

    def _get_new_soc_limit(self) -> int:
        '''return new soc limit to set'''
        return max(self.charge_limit_soc, self.evsoc_limit_high)


    def _save_charging_status(self):
        '''save charging flag status to file'''
        if os.path.exists(self.fname_charging_status):
            new_file = False
        else:
            logger.info('New file  :%s', self.fname_charging_status)
            new_file = True
        savedict = dict(Zeit=time.ctime())
        savedict.update(dict(charging_flag=self.charging_flag))
        savedict.update(dict(last_charge_limit_soc=self.last_charge_limit_soc))
        savedict.update(dict(time=time.time()))
        try:
            with open(self.fname_charging_status, 'a+', newline='') as csvfile:
                colnames = list(savedict.keys())
                writer = csv.DictWriter(csvfile, fieldnames=colnames,
                                        dialect='excel',
                                        delimiter=';')
                if new_file:
                    writer.writeheader()
                writer.writerow(savedict)
        except (PermissionError, Exception) as err:
            ftext = f'Could not save charging_status: {err}'
            logger.warning(ftext, exc_info=True)
            self.send_status(ftext)

    def _get_charging_status(self):
        '''get charging_flag status from file'''
        if not os.path.exists(self.fname_charging_status):
            self.charging_flag = False
            self.last_charge_limit_soc = 0
        try:
            with open(self.fname_charging_status, 'r') as csvfile:
                reader = csvfile.read()
            for line in reversed(reader.split('\n')):
                if line != '':
                    break
            self.charging_flag = (line.split(';')[1] == 'True')
            self.last_charge_limit_soc = int(line.split(';')[2])
        except (PermissionError, FileNotFoundError, Exception) as err:
            ftext = f'Missing file {self.fname_charging_status}'
            ftext += f' \nCould not get charging_status: {err}'
            logger.warning(ftext, exc_info=False)
            self.send_status(ftext)

    def _start_car_charging(self) -> bool:
        '''start charging car with exception handling'''
        try:
            self._try_wake_up()
            last_charge_limit = self.charge_limit_soc
            if self.last_charge_limit_soc == 0:
                if self._try_set_charge_limit(self._get_new_soc_limit()):
                    self.last_charge_limit_soc = last_charge_limit
            if not self.charging_flag:
                response = self._try_start_charging()
                if response:
                    self.charging_flag = True
                    self._save_charging_status()
                    self._reset_timestamp()
                    logger.info('Car charging started:%s', response)
                    return True
        except (AssertionError, ApiError, json.JSONDecodeError) as err:
            logger.warning(err, exc_info=False)
            return False
        except AuthenticationError as err:
            msg = '\n{}\n\nself._start_car_charging in car.py v{}'
            self.send_status(msg.format(err, __version__))
            logger.critical(err, exc_info=False)
            raise AuthenticationError('Please check credentials for car login')
        else:
            logger.error('Assertion: unable to start charging')
            return False

    def _stop_car_charging(self) -> bool:
        '''stop charging car with exception handling'''
        try:
            self._try_wake_up()
            if self.last_charge_limit_soc > 0:
                new_limit = self.last_charge_limit_soc
                if self._try_set_charge_limit(new_limit):
                    self.last_charge_limit_soc = 0
            if self.charging_flag:
                if self._try_stop_charging():
                    self.charging_flag = False
                    self._save_charging_status()
                    self._reset_timestamp()
                    logger.debug('Car charging stopped')
                    return True
        except (AssertionError, ApiError, json.JSONDecodeError) as err:
            logger.warning(err, exc_info=False)
            return False
        except AuthenticationError as err:
            msg = '\n{}\n\nself._start_car_charging in car.py v{}'
            self.send_status(msg.format(err, __version__))
            logger.critical(err, exc_info=False)
            raise AuthenticationError('Please check credentials for car login')
        else:
            logger.error('Unable or unnecessary to stop car_charging')
            return False

    def _reset_timestamp(self) -> None:
        '''reset timestamp to trigger self.car_update() on next call'''
        self.timestamp -= self.seconds_btw_updates

    def start_charging(self) -> tuple:
        '''
        Start charging car if all conditions are met and set *charging_flag*
        '''
        self.update_car_if()
        conditions = dict()
        conditions.update(dict(data_ok=self.data_ok))
        conditions.update(dict(athome=self.athome()))
        conditions.update(
            dict(charge_port=(self.charge_port_latch == 'Engaged')))
        conditions.update(dict(charging_needed=self._charging_needed()))
        ftext = f'conditions: {conditions} | '
        ftext += f'charging_flag: {self.charging_flag}'
        logger.info(ftext)
        if all(conditions.values()):
            if self.charging_flag:
                return (True, True)  # do nothing - already charging
            response = self._start_car_charging()
            logger.debug(response)
            return (True, False)
        return (False, self.stop_charging())

    def stop_charging(self) -> bool:
        '''
        Stop charging car if *charging_flag* set - else no wake up!'''
        if self.battery_level == 0:
            logger.warning('battery level is 0 --> force update_car')
            self.update_car()
        if self.charging_flag or self.last_charge_limit_soc > 0:
            return self._stop_car_charging()
        return False   # do nothing


if __name__ == '__main__':
    car = Car(EMAIL, PW, VIN, HOME)  # car.update_car_if()
