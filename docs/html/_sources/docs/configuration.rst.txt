.. Introduction of Solar explaining backgrund and
   working principles of the application

.. _settings:

Configuration
=============

Access data
----------------

Create a file in the folder solar/solar/definitions

.. code-block:: python
    :caption: access_data.py

    # -*- coding: utf-8 -*-
    #  Mandatory access data for E3DC and Tesla Car

    #  Access data for E3DC
    E3DC_IP = '111.111.111.111'  # IP Address of E3DC S10 system in local network

    #  Access data for Tesla API
    EMAIL = 'mymail@mymail.ch'
    PW = 'mymailpassword'
    VIN = '4VISF2E11UI123456'
    HOME = (39.537498, -119.4339107,2486)  # latitude, longitude of home location




E3DC data collection
--------------------

.. warning::

    Set correct IP address of E3DC system. Without correct IP address data
    collection from E3DC is not possible. If access is not possible a notification is
    sent via email.

:ref:`home`

_______________________________________________________________________________

TeslaAPI settings
-----------------

.. warning::

     Set correct access data in *solar.definitions.access_data.py*.
     Wrong credentials are notified via email if set in send_status.

:ref:`home`

_______________________________________________________________________________

Email notification
------------------

.. note::

    If you would like to receive notification emails a file
    **solar/definitions/send_status_access.py** must be created with the following content.
    No email notifications are sent if settings are incorrect or file is missing.
    For "from_addr" it is recommended to create a free email address just for sending notification mails.

.. code-block:: python
    :caption: send_status_access.py

    # -*- coding: utf-8 -*-
    #  Access data for Email notification

    # defaults for sending status mails

    from_addr = 'carnotification@mymail.com'
    from_name = 'Raspberry'
    from_password = 'notificationpassword'
    to_addrs = 'user@domain.com'
    signature = 'Mail from Raspberry'

    # other values depending on mail server (for Gmail)

    port = 587
    smtp_server = 'smtp.gmail.com'










.. automodule:: solar.send_status
    :noindex:
.. autofunction:: send_status
    :noindex:

:ref:`home`

_______________________________________________________________________________

Other settings
--------------

.. automodule:: solar.definitions.pvdataclasses
    :members: CarDefaults, ChargeDefaults
    :exclude-members: defaults_update_values
    :noindex:

_______________________________________________________________________________

:ref:`home`

:ref:`genindex`

:ref:`modindex`

:ref:`search`
