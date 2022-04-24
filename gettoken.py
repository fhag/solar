# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 15:12:29 2022
Get credentials for tesla api and store access token to cache.json

in development
@author: annet
"""

import teslapy
# import args

__version__ = '0.0.1'

email = 'gerard.fischer@gmx.ch'

if __name__ == '__main__':
    print('run')
    with teslapy.Tesla(email, cache_file='test.json') as tesla:
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        # vehicles[0].command('ACTUATE_TRUNK', which_trunk='front')
        vdata = vehicles[0].get_vehicle_data()
        print(vdata['vehicle_state']['car_version'])

