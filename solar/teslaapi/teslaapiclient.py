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
Class TeslaApiClient with methods for authentification and get and post
methods for access to Tesla API
"""

import logging
import requests
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
import teslapy
from .teslavehicle import Vehicle

__version__ = '1.0.1'
print(f'teslaapi.py v{__version__}')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TeslaApiClient(teslapy.Tesla):
    '''
    Class TeslaApiClient with authentification, get and post
    methods for access to Tesla API
    '''
    def __init__(self, email, password):
        super().__init__(email, password)
        try:
            self.fetch_token()
        except HTTPError:
            raise AuthenticationError('Check credentials')
        logger.info('TeslaApiClient for %s initialised', email)

    # def _get_headers(self):
    #     '''Return header for get or post commands'''
    #     return {'Authorization': 'Bearer {}'.format(
    #         self._token["access_token"])}

    # def get(self, endpoint) -> dict:
    #     '''get commands returns dict'''
    #     self.authenticate()
    #     response = requests.get('{}/{}'.format(API_URL, endpoint),
    #                             headers=self._get_headers())
    #     response_json = response.json()
    #     if 'error' in response_json:
    #         logger.error('APIError from Tesla')
    #         raise ApiError(response_json['error'])
    #     return response_json['response']

    # def post(self, endpoint, data=dict()) -> dict:
    #     '''post commands returns dict'''
    #     self.authenticate()
    #     response = requests.post('{}/{}'.format(API_URL, endpoint),
    #                              headers=self._get_headers(), data=data)
    #     response_json = response.json()
    #     if 'error' in response_json:
    #         logger.error('APIError from Tesla')
    #         raise ApiError(response_json['error'])
    #     return response_json['response']

    def list_vehicles(self):
        '''Return a list of valid Vehicle instances'''
        return [Vehicle(v, self) for v in self.api('VEHICLE_LIST')['response']]

class AuthenticationError(Exception):
    '''Critical error due to wrong credentials'''
    def __init__(self, error):
        logger.critical('AuthentificationError raised')
        super().__init__(
            'Authentication to the Tesla API failed: {}'.format(error))

class ApiError(Exception):
    '''Error due to communication failure'''
    def __init__(self, error):
        logger.error('APIError raised')
        super().__init__('Tesla API call failed: {}'.format(error))
