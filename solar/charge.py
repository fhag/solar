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
This module collects data from E3DC System via Modbus-Interface.
If conditions to possibly start charging the car, *car.start_charging*
is called. In any other case car.*stop_charging* is called.

Data is collected from E3DC every minute (_sleep_time).

The key data collected are:

- SOC of housebattery

The conditions to start charging the car are:

- the data could be read from E3DC (no transmission error)

- power delivered to network larger than evsoc_minimum

- the minimum state of charge (SOC) of the housebattery overstepped


In order to avoid excessive switching the conditions must be stable for
5 minutes
"""

import os
import csv
import urllib
import json
import time
import logging
from datetime import datetime
from collections import namedtuple
from .definitions.pvdataclasses import ChargeDefaults, PVStatus
from .chargemodbus import ChargeModbus, Modbus_exceptions
from .car import Car
from .definitions.access_data import EMAIL, VIN, HOME
from .send_status import send_status

__version__ = '1.1.55'
print(f'{__name__:40s} v{__version__}')

logger = logging.getLogger(__name__)


class ChargeEV(ChargeDefaults):
    '''class for charging with PV power'''

    def __init__(self):
        super().__init__()
        self.__version__ = __version__
        self.defaults_version = ''
        self.check_internet()
        self.send_status = send_status
        self.modbus = ChargeModbus()
        try:
            self.car = Car(EMAIL, VIN, HOME)
        except (AttributeError, Exception) as err:
            logger.info('No connection to tesla car possible - '
                        f'check credentials \n   --> [{err!r}]')
        self.state = self.get_new_values()
        self.car.update_car()
        msgs = [f'charge.py v{__version__} with '
                f'car.py v{self.car.__version__} successfully started.']
        ftext = 'Car connection to {!r} with VIN {!r} established at {}.'
        name = self.car.display_name if self.car.display_name else 'n.a.'
        vin = self.car. vin if self.car.vin else 'n.a.'
        msgs.append(ftext.format(name, vin, datetime.now()))
        ftext = 'E3DC connection to {!r} established at {}.'
        msgs.append(ftext.format(self.modbus._tcp_ip, datetime.now()))
        print(msgs)
        msg = '\n'.join(msgs)
        self.send_status(msg)
        logger.info(msg)

    def _update_default_values(self) -> None:
        '''Read updated values if available'''
        try:
            fname = ''.join([self._defaults_path, self._defaults_file])
            fname = os.path.normpath(fname)
            with open(fname, 'rb') as file:
                new_values = json.loads(file.read())
            for key, value in new_values.items():
                try:
                    new_values[key] = int(new_values[key])
                except ValueError:
                    pass
            if new_values['__version__'] != self.defaults_version:
                logger.info(str(new_values).replace(', ', '\n        '))
                self.defaults_version = new_values['__version__']
            # update charge defaults
            charge_keys = set(self.__dict__.keys()) & set(new_values.keys())
            for key in charge_keys:
                setattr(self, key, new_values[key])
            # update car defaults
            car_keys = set(self.car.__dict__.keys()) & set(new_values.keys())
            # logger.debug(keys)
            for key in car_keys:
                setattr(self.car, key, new_values[key])
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning('FileNotFoundError: %s', fname)
        except Exception as err:
            logger.critical(err, exc_info=True)
            raise

    def _netz(self) -> bool:
        '''True if enough sun power for charging'''
        netz_start_limit, \
            netz_stopp_limit = self.car.current_power_start_stop()
        if self.car.charging_flag:
            self.netz_vals.values.append(self.state.netz <= netz_stopp_limit)
        else:
            self.netz_vals.values.append(self.state.netz <= netz_start_limit)
        if self.netz_vals.alltrue():
            new_status = True
        elif self.netz_vals.allfalse():
            new_status = False
        else:
            new_status = self.old_netz_status
        ftext = str(self.car.current_power_start_stop())
        ftext += f' | {self.netz_vals} | new_status:{new_status}'
        ftext += f'|  old_status:{self.old_netz_status}'
        logger.debug(ftext)
        self.old_netz_status = new_status
        return new_status

    def _housebattery_soc_ok(self) -> bool:
        '''True if house battery SOC > self.soc_minimum or NaN'''
        if self.car.charging_flag:
            soc_minimum = self.soc_minimum_stop
        else:
            soc_minimum = self.soc_minimum_start
        return self.state.soc >= soc_minimum

    def _pvstateok(self) -> bool:
        '''True if contact to modbus, False after loosing contact'''
        self.coll_vals.values.append(self.state.ok)
        return self.coll_vals.anytrue()

    def _sleep_time(self) -> float:
        '''Return sleep time in seconds to next full minute'''
        now = datetime.now().timestamp()
        return max(0, self.check_intervall - now % self.check_intervall)

    def get_new_values(self) -> PVStatus:
        '''Return new state values from E3DC system via modbus interface'''
        try:
            delay = time.time() - self.e3dc_time_last_connection
            pvdata = self.modbus.collect()
            pvdict = self.modbus.data2dict(pvdata)
            if self._log_to_file:
                pvdict.update(dict(Charging=self.car.charging_flag))
                self.save_to_csv(pvdict)
            response = self.modbus.data2pvstate(pvdata)
            if delay > self.e3dc_error_minimum_time:
                ftext = 'E3DC Connection established to {} at {}'
                ftext = ftext.format(self.modbus._tcp_ip, datetime.now())
                logger.info(ftext)
                # self.send_status(ftext)
            self.e3dc_time_last_connection = time.time()
            return response
        except (Modbus_exceptions.ConnectionException, AttributeError):
            if delay > self.e3dc_error_minimum_time:
                if self.e3dc_time_last_connection == 0:
                    ftext = 'E3DC Connection with {} error already notified'
                    logger.debug(ftext.format(self.modbus._tcp_ip))
                else:
                    ftext = 'E3DC Connection to {} lost at {}'
                    ftext = ftext.format(self.modbus._tcp_ip, datetime.now())
                    logger.info(ftext)
                    self.send_status(ftext)
                    self.e3dc_time_last_connection = 0
            else:
                logger.warning('E3DC Connection interruption of %s',
                               '{:.1f} seconds'.format(delay))
            return PVStatus()

    @property
    def filename(self):
        '''Return valid filename for data file

        - self._path: path for data file directory

        - self._fname: template for file name
        '''
        return self._path + datetime.now().strftime(self._fname)

    def save_to_csv(self, dict2save: dict):
        '''Append all collected data from E3DC to a CSV file'''
        omit_cols = ['SNr_t', 'S10_FW_t']
        savedict = {k: v for k, v in dict2save.items() if k not in omit_cols}
        if os.path.exists(self.filename):
            new_file = False
        else:
            logger.info('New file  :%s', self.filename)
            new_file = True
        try:
            with open(self.filename, 'a+', newline='') as csvfile:
                colnames = list(savedict.keys())
                writer = csv.DictWriter(csvfile, fieldnames=colnames,
                                        dialect='excel',
                                        delimiter=';')
                if new_file:
                    writer.writeheader()
                writer.writerow(savedict)
        except (PermissionError, Exception) as err:
            ftext = f'Could not save data: {err}'
            logger.warning(ftext, exc_info=True)
            self.send_status(ftext)

    def check_internet(self, sleeptime=1, www='https://www.google.com'):
        '''
        Wait until internet is available.

        - True if internet availabe
        - False if timeout exceeded
        - self.check_internet_timeout: from pvdataclasses.ChargeDefaults
        '''
        for i in range(self.check_internet_timeout):
            try:
                response = urllib.request.urlopen(www)
                assert response.code != 200
            except (AssertionError):
                logger.warning(
                    'Internet connection established after %.0f sec', i)
                return True
            except (urllib.error.URLError, urllib.error.HTTPError):
                logger.debug('Connection Error after %.0f seconds', i)
            except Exception:
                logger.error('Unexpected Exception after %.0f seconds', i)
            time.sleep(sleeptime)
        raise KeyboardInterrupt('No internet connection after %.0f sec' % i)

    def run(self):
        '''
        Start application and loop until Interrupt

        Checking state of photovoltaic system.
        Initiates start/stop charging if conditions are met.
        '''
        logger.info('Start running')
        Conditions = namedtuple('Conditions',
                                ['Netz', 'Housebattery_SOC', 'PV_State'])
        try:
            while True:
                self._update_default_values()
                self.state = self.get_new_values()
                ftxt = f'%s charging_state:{self.car.charging_state!r}'
                logger.info(ftxt, str(self.state))
                print(ftxt % str(self.state))
                if self.state.ok:
                    netz = self._netz()
                    housebattery_ok = self._housebattery_soc_ok()
                    pvstate_ok = self._pvstateok()
                    conditions = Conditions(netz, housebattery_ok, pvstate_ok)
                    infotxt = (' -> %s, car.charging:%s, charging_flag:%s' %
                               (str(conditions), self.car.charging,
                                self.car.charging_flag))
                    resp = False
                    if all(conditions):
                        resp = self.car.start_charging()
                        finfotxt = ('car.start_charging response=%s, %s' %
                                    (resp, infotxt))
                    else:
                        resp = self.car.stop_charging()
                        finfotxt = ('car.stop_charging response=%s, %s' %
                                    (resp, infotxt))
                    logger.info(finfotxt)
                sleep_time = self._sleep_time()
                ftext = f' Sleeping {sleep_time:5.1f} sec,   '
                ftext += f'car.battery_level: {self.car.battery_level:3.0f} '
                ftext = ftext.center(120, '-')
                # logger.info(ftext)
                print(f'{time.strftime("%Y-%m-%d %H:%M")}|{ftext}')
                time.sleep(sleep_time)
        except (KeyboardInterrupt, IndexError) as err:
            print(f'User abort - normal break : {err}')
            logger.error('User abort - normal break %s', err)
        except Exception as err:
            print(f'ERROR break {err!r}')
            logger.critical(err, exc_info=True)
        finally:
            self.car.stop_charging()


if __name__ == '__main__':
    ev = ChargeEV()
