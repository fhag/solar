# -*- coding: utf-8 -*-
#  This program and data is free software; you can redistribute it and/or modify
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
Internal mapping data for E3DC modbus based on:
    'Modbus/TCP-Schnittstelle der E3/DC GmbH, Kurzanleitung'
    © 2017 E3/DC GmbH. Alle Rechte vorbehalten.
    E3DC_Kurzanleitung | 2017-04-10-V1.6

"""

__version__ = '0.0.5'

config = [
        {
            'address': 40001,
            'length': 1,
            'type': 'Hex',
            'name': 'S10 ModBus ID 0xE3DC',
            'sname': 'S10 ModBus ID'
        },
        {
            'address': 40002,
            'length': 1,
            'type': 'Int8x2',
            'name': 'S10 ModBus Firmware-Version',
            'unit': 'v'
        },
        {
            'address': 40003,
            'length': 1,
            'type': 'Int32',
            'name': 'Anzahl Register'
        },
        {
            'address': 40004,
            'length': 16,
            'type': 'String',
            'name': 'Hersteller'
        },
        {
            'address': 40020,
            'length': 16,
            'type': 'String',
            'name': 'Modell'
        },
        {
            'address': 40036,
            'length': 16,
            'type': 'String',
            'name': 'Seriennummer',
            'cname': 'SNr'
        },
        {
            'address': 40052,
            'length': 16,
            'type': 'String',
            'name': 'S10 Firmware Release',
            'cname': 'S10 FW'
        },
    {
        'address': 40068,
        'length': 2,
        'type': 'Int32',
        'name': 'Photovoltaik-Leistung',
        'sname': 'Solarstrom 1',
        'cname': 'PV1',
        'unit': 'W',
    },
    {
        'address': 40070,
        'length': 2,
        'type': 'Int32',
        'name': 'Batterie-Leistung',
        'sname': 'Batterie Entladen/Laden',
        'cname': 'Akku',
        'factor': -1,
        'unit': 'W',
    },
    {
        'address': 40072,
        'length': 2,
        'type': 'Int32',
        'name': 'Hausverbrauchs-Leistung',
        'sname': 'Hausverbrauch',
        'cname': 'Haus',
        'factor': -1,
        'unit': 'W',
    },
    {
        'address': 40074,
        'length': 2,
        'type': 'Int32',
        'name': 'Leistung Netzübergabepunkt',
        'sname': 'Netzbezug/-einspeisung',
        'cname': 'Netz',
        'unit': 'W',
    },
    {
        'address': 40076,
        'length': 2,
        'type': 'Int32',
        'name': 'Leistung zusätzlicher Einspeiser',
        'sname': 'Solarstrom 2',
        'cname': 'PV2',
        'unit': 'W',
        'factor': -1
    },
    {
        'address': 40078,
        'length': 2,
        'type': 'Int32',
        'name': 'Leistung Wallbox',
        'unit': 'W',
    },
    {
        'address': 40080,
        'length': 2,
        'type': 'Int32',
        'name': 'Von Wallbox genutzte Solarleistung',
        'sname': 'Wallbox-Solarleistung',
        'unit': 'W',
    },
    {
        'address': 40082,
        'length': 1,
        'type': 'Int8x2',
        'name': 'Autarkie und Eigenverbrauch',
        'sname': 'Autarkie/Eigenverbrauch',
        'cname': 'Aut_EigV',
        'unit': '%',
    },
    {
        'address': 40083,
        'length': 1,
        'type': 'Int32',
        'name': 'Batterie SOC',
        'cname': 'SOC',
        'unit': '%',
    },
    {
        'address': 40084,
        'length': 1,
        'type': 'EMS',
        'name': 'Emergency Power Status',
        'sname': 'EPowerS',
        'cname': 'EPS',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40085,
        'length': 1,
        'type': 'Int32',
        'name': 'EMS-Status',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40086,
        'length': 1,
        'type': 'Int32',
        'name': 'EMS Remote Control',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40087,
        'length': 1,
        'type': 'Int32',
        'name': 'EMS-CTRL',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40089,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_1_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40090,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_2_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40091,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_3_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40092,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_4_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40093,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_5_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40094,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_6_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40095,
        'length': 1,
        'type': 'Int32',
        'name': 'Wallbox_7_Ctrl',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40096,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_1_Voltage',
        'unit': 'V',
        'last': ''
    },
    {
        'address': 40097,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_2_Voltage',
        'unit': 'V',
        'last': ''
    },
    {
        'address': 40098,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_3_Voltage',
        'unit': 'V',
        'last': ''
    },
    {
        'address': 40099,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_1_Current',
        'unit': 'A',
        'last': ''
    },
    {
        'address': 40100,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_2_Current',
        'unit': 'A',
        'last': ''
    },
    {
        'address': 40101,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_3_Current',
        'unit': 'A',
        'last': ''
    },
    {
        'address': 40102,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_1_Power',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40103,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_2_Power',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 40104,
        'length': 1,
        'type': 'Int32',
        'name': 'DC_String_3_Power',
        'unit': 'W',
        'last': ''
    },
    {
        'address': 5001,
        'length': 1,
        'type': 'Int32',
        'name': 'Betriebszustand',
        'unit': '',
        'last': ''
    },


]

conf = {d['address'] : d for d in config if 'address' in d.keys()}

if __name__ == '__main__':
    print(f'e3dc_register.py v{__version__}\n')
    for key in conf.keys():
        sname = conf[key].get('sname', conf[key]['name'])
        print(key, conf[key]['length'], sname, conf[key]['name'], conf[key]['type'])

