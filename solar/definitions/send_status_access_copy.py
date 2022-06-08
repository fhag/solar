# -*- coding: utf-8 -*-
"""
Access data for Email notification
"""
__version__ = '1.1.41'

# defaults for sending status mails
from dataclasses import dataclass


@dataclass
class Access():
    from_addr: str = 'mycar@gmail.com'
    from_name: str = 'Raspberry'
    from_password: str = 'mycarpassword'
    to_addrs: str = 'myprivatemail@gmail.com'
    signature: str = 'Mail from Raspberry running car.py and charge.py'
    # port and servername depending on mail server
    port: int = 587
    smtp_server: str = 'smtp.gmail.com'


access = Access()

# from_addr = 'mycar@gmail.com'
# from_name = 'Raspberry'
# from_password = 'mycarpassword'
# to_addrs = 'myprivatemail@gmail.com'
# signature = 'Mail from Raspberry running car.py and charge.py'

# # port and servername depending on mail server

# port = 587
# smtp_server = 'smtp.gmail.com'

if __name__ == '__main__':
    print(f'send_status_access.py v{__version__} is ok')
