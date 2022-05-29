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
import os
from datetime import datetime
from pathlib import Path
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

__version__ = '1.1.54'
print(f'{__name__:40s} v{__version__}')

logger = logging.getLogger(__name__)

BUFFERPATH = './logs'


def send_status(msgstr: str,
                subject: str = None,
                bufferid: str = 'dummy',
                bufferpath: Path = Path('.'),
                bufferminutes: int = 0) -> str:
    '''
    send **msgstr** (with **subject**) to **to_addrs**
    '''
    if not access.smtp_server:
        return ''
    # first check for internet connection and abort if no internet
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
    # prepare subject and msgtxt
    date = time.strftime(
        "%a, -%d. %B %Y %X").replace('-0', ' ').replace('-', '')
    msgtxts = list()
    msgtxts.append(f'Mail from {hname!r}: IP{ipadr!r}')
    msgtxts.append(f'{date}')
    msgtxts.append(f'{msgstr}')
    msgtxts.append(f'{access.signature}')
    msgtxt = ' |'.join(msgtxts)
    if subject is None:
        subject = f'Solar-Car-Charger : {time.ctime()}'
    msg = MIMEText(msgtxt, 'plain')
    msg['Subject'] = subject
    msg['From'] = access.from_name
    msg['To'] = access.to_addrs
    fname = '---'
    if bufferminutes > 0:
        try:
            os.listdir(bufferpath)
        except FileNotFoundError:
            print('no buffer path')
        else:
            fname = bufferpath.joinpath(f'Buffer-{bufferid}.txt')
            print(f'{fname=} {bufferid=}')
            buffertxt = msgtxt
            # buffertxt = msgtxt.split('\n')
            # buffertxt = ' |'.join([txt for txt in buffertxt if txt])
            try:
                with open(fname, 'r') as file:
                    msgtxt = file.read()
            except FileNotFoundError:
                msgtxt = datetime.now().isoformat()
            msgtxt += f'\n{buffertxt}'
            startline = msgtxt.split('\n')[0]
            starttime = datetime.fromisoformat(startline)
            age = (datetime.now() - starttime).seconds
            print(f'{age=:.4f}  {bufferminutes * 60=}')
            if age > bufferminutes * 60:
                # os.remove(fname)
                with open(fname, 'w') as file:
                    file.write(datetime.now().isoformat())
            else:
                with open(fname, 'w') as file:
                    file.write(msgtxt)
                return ''
            print('*' * 100)
    print('send_mail')
    print(msgtxt)
    print('-' * 100)
    # send_mail(access, subject, msgtxt)
    """
    ------------------------------------------------------------------------
    """
    # return fname
    return fname
    # return msg, access, subject, msgtxt, fname


def send_mail(access, subject, msgtxt):
    '''Send mail via SMTP'''
    if not access.smtp_server:
        return ''
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
        print(f'{time.asctime()!r} - Mail successfully sent {msgtxt!r}')
        msgtxt = msgtxt.replace('\n', ' |')
        logger.info("Msg: '%s' successfully transmitted", msgtxt)
        return msgtxt


if __name__ == '__main__':
    MSGTXT = '''Dies ist eine Testnachricht.'''
    print(MSGTXT)
    # resp1 = send_status(MSGTXT)
    response = send_status(MSGTXT,
                           bufferid='112',
                           bufferpath=Path('./logs'),
                           bufferminutes=0.2)
    print(response)
