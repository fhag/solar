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
Class ChargeModbus with methods to collect and prepare data
from E3DC modbus interface

"""
import logging
from datetime import datetime
import pymodbus.exceptions as Modbus_exceptions
from pymodbus.client.sync import ModbusTcpClient
from solar.definitions.e3dc_register import conf
from solar.definitions.pvdataclasses import PVStatus, ModbusDefaults

__version__ = '0.0.15'
print(f'chargemodbus.py v{__version__}')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ChargeModbus(ModbusDefaults):
    '''
    Read E3DC system status data from modbus interface
    '''
    def __init__(self):
        assert self._tcp_ip
        super().__post_init__()
        self.client = ModbusTcpClient(self._tcp_ip)
        self.client.connect()
        self.conf = conf
        self._functions = {'String': self._to_str, 'Int32': self._to_int32,
                           'Int8x2': self._to_int8x2, 'Hex': self._to_hex,
                           'EMS': self._to_EMS}
        logger.warning('ChargeModbus initialised and active')

    @staticmethod
    def _to_str(regs: list, _key: int) -> (str, str):
        '''list of hex codes to str'''
        reg_str = ''.join([f'{reg:04x}' for reg in regs if reg > 0])
        return_string = bytes.fromhex(reg_str).decode()
        return return_string, return_string

    def _to_int32(self, regs: list, _key: int) -> (int, str):
        '''list of hex codes to uint32 or int'''
        integer = int(hex(regs[0]), 16)
        if len(regs) > 1:
            integer -= int(hex(regs[1]), 16)
        integer *= self.conf[_key].get('factor', 1)
        unit = self.conf[_key].get('unit', '')
        sname = self.conf[_key].get('sname', self.conf[_key]['name'])
        integers = f'{sname}: {integer:,.0f}{unit}'.replace(",", "'")
        return integer, integers

    def _to_int8x2(self, regs: list, _key: int) -> (int, str):
        '''list of hex codes to int and %'''
        regh = f'{regs[0]:04x}'
        int1, int2 = int(regh[:2], 16), int(regh[-2:], 16)
        unit = self.conf[_key].get('unit', '')
        sname = self.conf[_key].get('sname', self.conf[_key]['name'])
        ints = f'{sname}: {int1:.0f}{unit} {int2:.0f}{unit}'
        return (int1, int2), ints

    def _to_hex(self, regs: list, _key: int) -> (int, str):
        '''list of hex codes to int and Hex-String'''
        integer = int(hex(regs[0]), 16)
        unit = self.conf[_key].get('unit', '')
        sname = self.conf[_key].get('sname', self.conf[_key]['name'])
        integers = f'{sname}: {integer:04X}{unit}'.replace(",", "'")
        return integer, integers

    def _to_EMS(self, regs: list, _key: int) -> (int, str):
        '''list of int to int and text'''
        reg = min(4, regs[0])
        texts = ['Notstrom nicht unterstützt', 'Notstrom aktiv',
                 'Notstrom nicht aktiv', 'Notstrom nicht verfügbar',
                 'S10 E-Motorschalter in falscher Position']
        status = texts[reg]
        sname = self.conf[_key].get('sname', self.conf[_key]['name'])
        statuss = f'{sname}: {status}'
        return reg, statuss

    def run_collect(self) -> PVStatus:
        '''Return collected data'''
        try:
            data = self.data2pvstate(self.collect())
#            collected_data = self.collect()
            logger.warning('run_collect collected data: %s', data)
            return data
#            return self.data2pvstate(collected_data)
        except Modbus_exceptions.ConnectionException:
            ftext = f' No connection to E3DC at {datetime.now()} '
            logger.error(ftext)
            return PVStatus()

    def data2pvstate(self, orgdata):
        '''Return pvstate dataclass'''
        ddata = self.data2dict(orgdata)
        tdata = {k.lower(): v for k, v in ddata.items()}
        fields = PVStatus.__annotations__.keys()
        return PVStatus(**{k: v for k, v in tdata.items() if k in fields},
                        ok=True)

    def collect(self):
        '''Collect raw data and return dict with data'''
        collect_data = dict()
        for key in self.keys:
            address = key - 1
            count = self.conf[key]['length']
            request = self.client.read_holding_registers(address, count=count)
            regs = [request.getRegister(i) for i in range(count)]
            collect_data[key] = regs
        timestamp = int(datetime.now().timestamp())
        timestamp = timestamp - (timestamp % 60)  # round to minutes
        collected = {datetime.fromtimestamp(timestamp): collect_data}
        self.client.close()
        return collected

    def data2dict(self, time_data):
        '''
        Add timestamp, data labels and formatted string data
        '''
        timestamp = list(time_data.keys())[0]
        data = time_data[timestamp]
        ndata = dict(dtime=timestamp)
        for key in data.keys():
            regs = data[key]
            key_type = self.conf[key]['type']
            if key_type in self._functions.keys():
                resp, respt = self._functions[key_type](regs, key)
                sname = self.conf[key].get('cname', self.conf[key]['name'])
                dkey = sname.replace(' ', '_')
                ndata[dkey] = resp
                ndata[dkey + '_t'] = respt
            else:
                print(self.conf[key]['name'].center(80, '-'))
                for reg in regs:
                    reg_str = f'{reg:04x}'
                    reg_chr = (chr(int(reg_str[:2], 16)) +
                               chr(int(reg_str[2:], 16)))
                    ftext = [f'{key}| {reg:7.0f} {hex(reg):>10s}',
                             f' {bin(reg):>20s} {reg_str} {reg_chr}']
                    print(''.join(ftext))
        return ndata


if __name__ == '__main__':
    ch = ChargeModbus()
    daten = ch.run_collect()
    print(daten)
    print(ch.data2dict(ch.collect()))
    print(ch.data2dict(ch.collect()))
