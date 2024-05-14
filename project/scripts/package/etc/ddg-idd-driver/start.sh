#!/bin/bash

#/usr/bin/python3 /etc/ddg-idd-driver/main.py -d info &>> /etc/ddg-idd-driver/ddg-idd-driver.log & #> /dev/null 2>&1
./opt/ddg-idd-driver/ddg-idd-driver -d info &>> /var/log/ddg-idd-driver/ddg-idd-driver.log & #> /dev/null 2>&1

echo $! > /var/run/ddg-idd-driver.pid
