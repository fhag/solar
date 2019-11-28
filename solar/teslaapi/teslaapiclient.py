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
from datetime import datetime, timedelta
import requests
from solar.teslaapi.teslavehicle import Vehicle

__version__ = '0.0.10'
print(f'teslaapi.py v{__version__}')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TESLA_API_BASE_URL = 'https://owner-api.teslamotors.com/'
TOKEN_URL = TESLA_API_BASE_URL + 'oauth/token'
API_URL = TESLA_API_BASE_URL + 'api/1'
OAUTH_CLIENT_ID = '81527cff06843c8634fdc09e8ac0abef' + \
        'b46ac849f38fe1e431c2ef2106796384'
OAUTH_CLIENT_SECRET = 'c7257eb71a564034f9419ee651c7d0e5' + \
    'f7aa6bfbd18bafb5c5c033b093bb2fa3'


class TeslaApiClient:
    '''
    Class TeslaApiClient with authentification, get and post
    methods for access to Tesla API
    '''
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._token = None
        logger.info('TeslaApiClient for %s initialised', email)

    def _get_new_token(self) -> dict:
        '''Return all tokens as dict based on email and password
        Exception: AuthenticationError, JSONDecodeError ...'''
        request_data = {'grant_type': 'password',
                        'client_id': OAUTH_CLIENT_ID,
                        'client_secret': OAUTH_CLIENT_SECRET,
                        'email': self._email,
                        'password': self._password
                        }
        response = requests.post(TOKEN_URL, data=request_data)
        response_json = response.json()
        if 'response' in response_json:
            logger.error('Authentification not possible!')
            raise AuthenticationError(response_json['response'])
        return response_json

    def _refresh_token(self, refresh_token) -> dict:
        '''Return refreshed tokens as dict based on refresh_token
        Exception: AuthenticationError, JSONDecodeError ...'''
        request_data = {'grant_type': 'refresh_token',
                        'client_id': OAUTH_CLIENT_ID,
                        'client_secret': OAUTH_CLIENT_SECRET,
                        'refresh_token': refresh_token,
                        }
        response = requests.post(TOKEN_URL, data=request_data)
        response_json = response.json()
        if 'response' in response_json:
            logger.error('Authentification not possible!')
            raise AuthenticationError(response_json['response'])
        return response_json

    def authenticate(self):
        '''
        Get new tokens if missing or refresh_token if 90%
        of expires_in already elapsed
        '''
        if not self._token:
            self._token = self._get_new_token()
        expiry_time = timedelta(seconds=0.9 * self._token['expires_in'])
        expiration_date = datetime.fromtimestamp(
            self._token['created_at']) + expiry_time
        if datetime.utcnow() >= expiration_date:
            self._token = self._refresh_token(self._token['refresh_token'])

    def _get_headers(self):
        '''Return header for get or post commands'''
        return {'Authorization': 'Bearer {}'.format(
            self._token["access_token"])}

    def get(self, endpoint) -> dict:
        '''get commands returns dict'''
        self.authenticate()
        response = requests.get('{}/{}'.format(API_URL, endpoint),
                                headers=self._get_headers())
        response_json = response.json()
        if 'error' in response_json:
            logger.error('APIError from Tesla')
            raise ApiError(response_json['error'])
        return response_json['response']

    def post(self, endpoint, data=dict()) -> dict:
        '''post commands returns dict'''
        self.authenticate()
        response = requests.post('{}/{}'.format(API_URL, endpoint),
                                 headers=self._get_headers(), data=data)
        response_json = response.json()
        if 'error' in response_json:
            logger.error('APIError from Tesla')
            raise ApiError(response_json['error'])
        return response_json['response']

    def list_vehicles(self):
        '''Return a list of valid Vehicle instances'''
        return [Vehicle(self, vehicle) for vehicle in self.get('vehicles')]


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
