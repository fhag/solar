# -*- coding: utf-8 -*-
"""
Access data for Email notification
"""
__version__ = '0.0.2'

# defaults for sending status mails

from_addr = 'mycar@gmail.com'
from_name = 'Raspberry'
from_password = 'mycarpassword'
to_addrs = 'myprivatemail@gmail.com'
signature = 'Mail from Raspberry running car.py and charge.py'

# port and servername depending on mail server

port = 587
smtp_server = 'smtp.gmail.com'

if __name__ == '__main__':
    print(f'send_status_access.py v{__version__} is ok')
