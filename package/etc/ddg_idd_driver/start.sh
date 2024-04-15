#!/bin/bash

/usr/bin/python3 /etc/ddg_idd_driver/main.py -d info &>> /etc/ddg_idd_driver/ddg_idd_driver.log & #> /dev/null 2>&1
echo $! > /var/run/ddg-idd-driver.pid
