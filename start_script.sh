#!/bin/sh
rm -f /home/pi/dotslash/client/JoinedDevices
rm -f /home/pi/dotslash/client/client.log
sleep 5 #to wait until files are deleted
until /sbin/ifconfig wlan0; do sleep 2; done #Wait until interfaces are up
/usr/bin/python /home/pi/dotslash/client/dev_client.py
