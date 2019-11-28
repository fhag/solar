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
Function to send emails about the status or errors to user.

- from_addr = 'carnotification@mymail.com'
- from_name = 'Raspberry'
- from_password = 'notificationpassword'
- to_addrs = 'user@domain.com'
- signature = 'Mail from Raspberry'

# other values depending on mail server

- port = 587
- smtp_server = 'smtp.gmail.com'

"""
import smtplib
import time
import logging
import socket
from email.mime.text import MIMEText

try:
    import solar.definitions.send_status_access as access
except ModuleNotFoundError:
    class AccessDummy():
        '''Empty class with no access data'''
        def __init__(self):
            self.from_addr = ''
            self.from_password = ''
            self.from_name = ''
            self.to_addrs = ''
            self.smtp_server = ''
            self.port = 0
            self.from_password = ''

    access = AccessDummy()

__version__ = '0.1.14'
print(f'send_status v{__version__}')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def send_status(msgstr: str, subject: str = None) -> str:
    '''
    send **msgstr** (with **subject**) to **to_addrs**
    '''
    if not access.smtp_server:
        return ''
    try:
        hname = socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ipadr = s.getsockname()[0]
    except (OSError) as err:
        logger.error('Network Error : %s', err)
        return ''
    except Exception as err:
        logger.error(err, exc_info=True)
        return ''
    else:
        msgtxts = list()
        msgtxts.append(f'Mail from {hname} with IP {ipadr}\n')
        msgtxts.append(f'{time.strftime("%A, %d. %B %Y")}\n')
        msgtxts.append(f'{msgstr}')
        msgtxts.append(f'\n{access.signature}')
        msgtxt = '\n'.join(msgtxts)
        if subject is None:
            subject = f'Solar-Car-Charger : {time.ctime()}'
        with smtplib.SMTP(access.smtp_server, access.port) as server:
            server.ehlo()
            server.starttls()
            server.login(access.from_addr, access.from_password)
            msg = MIMEText(msgtxt, 'plain')
            msg['Subject'] = subject
            msg['From'] = access.from_name
            msg['To'] = access.to_addrs
            resp = server.send_message(msg)
            assert resp == dict()
            print('Mail successfully sent')
            logger.info("Msg: '%s' successfully transmitted",
                        '|'.join(msgtxts).replace('\n', ''))
            return msgtxt


if __name__ == '__main__':
    MSGTXT = '''Dies ist eine Testnachricht.'''
    response = send_status(MSGTXT)
    print(response)
