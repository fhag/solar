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
from dataclasses import dataclass
from pathlib import Path
from email.message import EmailMessage

try:
    from solar.definitions.send_status_access import Access
    access = Access()
except ModuleNotFoundError:
    @dataclass
    class AccessDummy():
        '''Empty class with no access data'''
        from_addr: str = ''
        from_name: str = ''
        from_password: str = ''
        to_addrs: str = ''
        signature: str = ''
        # port and servername depending on mail server
        port: int = 0
        smtp_server: str = ''

    access = AccessDummy()

__version__ = '1.1.56'
print(f'{__name__:40s} v{__version__}')

logger = logging.getLogger(__name__)

BUFFERPATH = './logs'


def send_status(msgstr: str,
                subject: str = None,
                bufferid: str = 'dummy',
                bufferpath: Path = Path('.'),
                bufferminutes: int = 0,
                access: dataclass = None) -> str:
    '''
    send **msgstr** (with **subject**) to **to_addrs**
    '''
    if not hasattr(access, 'smtp_server'):
        logger.error('Missing access data for sending mails')
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
    if bufferminutes > 0:
        try:
            os.listdir(bufferpath)
        except FileNotFoundError:
            print('no buffer path')
        else:
            fname = bufferpath.joinpath(f'Buffer-{bufferid}.txt')
            # print(f'{fname=} {bufferid=}')
            buffertxt = msgtxt
            try:
                with open(fname, 'r') as file:
                    msgtxt = file.read()
            except FileNotFoundError:
                msgtxt = datetime.now().isoformat()
            msgtxt = f'{msgtxt}\n{buffertxt}'
            startline = msgtxt.split('\n')[0]
            starttime = datetime.fromisoformat(startline)
            age = (datetime.now() - starttime).seconds
            # print(f'{age=}  {starttime} {datetime.now()}')
            if age > bufferminutes * 60:
                with open(fname, 'w') as file:
                    file.write(datetime.now().isoformat())
            else:
                with open(fname, 'w') as file:
                    file.write(msgtxt)
                return ''
    return send_mail(access, subject, msgtxt)


def send_mail(access, subject, msgtxt):
    '''Send mail via SMTP'''
    if not hasattr(access, 'smtp_server'):
        return ''
    try:
        with smtplib.SMTP(access.smtp_server, access.port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(access.from_addr, access.from_password)
            msg = EmailMessage()
            msg.set_content(msgtxt)
            msg['Subject'] = subject
            msg['From'] = access.from_name
            msg['To'] = access.to_addrs
            resp = server.send_message(msg)
            assert resp == dict()
            print(f'{time.asctime()!r} - Mail successfully sent {msgtxt!r}')
            logger.info("Msg: '%s' successfully transmitted", msgtxt)
            return msgtxt
    except (AssertionError, Exception) as err:
        logger.error(f'Mail not sent: {str(err)!r}')
        return ''


if __name__ == '__main__':
    # test ohne buffer
    MSGTXT = '''Dies ist eine Testnachricht ohne Buffer.'''
    resp1 = send_status(MSGTXT, access=access)
    # test send_status with buffer
    b_path = Path('./logs')
    b_id = '112'
    fname = b_path.joinpath(f'Buffer-{b_id}.txt')
    try:
        os.remove(fname)
    except FileNotFoundError:
        print('No buffer file deletet')
    bufferminutes = 0.03
    MSGTXT = '{:3.0f}. Testnachricht mit Buffer {:4.3f} sec'
    stime = time.time()
    ntimes = 4
    for i in range(ntimes):
        msgtxt = MSGTXT.format(i, time.time() - stime)
        response = send_status(msgtxt,
                               access=access,
                               bufferid=b_id,
                               bufferpath=b_path,
                               bufferminutes=bufferminutes)
        time.sleep(bufferminutes * 60 / ntimes)
    time.sleep(bufferminutes * 60 / ntimes)
    msgtxt = MSGTXT.format(i + 1, time.time() - stime)
    response = send_status(msgtxt,
                           access=access,
                           bufferid=b_id,
                           bufferpath=b_path,
                           bufferminutes=0.025)

    # try:
    #     os.remove(fname)
    # except FileNotFoundError:
    #     print('No buffer file deletet')
