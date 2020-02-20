#!/bin/bash
echo Start logging
cd /home/pi/Projects/solar
/usr/lib/Python-3.7.3/python /home/pi/Projects/solar/main.py &
echo "Solar PID" $!
