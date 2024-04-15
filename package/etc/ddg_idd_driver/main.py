

import logging
import paho.mqtt.client as mqtt
import sys, traceback
from threading import Thread

import json
import time
from ddg import DDGDevice
from idd import IDDDevice
import params

import datetime
import store

DEBUG_LVL_KEY = "-d" # debug/info

if(DEBUG_LVL_KEY in sys.argv):
    loglevel = sys.argv[sys.argv.index(DEBUG_LVL_KEY) + 1]
else:
    loglevel = "info"

controllerId = store.get_controller_id()
ddg_states = store.get_ddg_states()
idd_states = store.get_idd_states()

ddg_list = []
idd_list = []

if(loglevel == "debug"):
    loglevel = logging.DEBUG
elif (loglevel == "info"):
    loglevel = logging.INFO
else:
   loglevel = logging.INFO 

logging.basicConfig(level=loglevel)

logging.info("\n\n\n ***DDG & IDD Driver Started***\n")
logging.info('DDG devices: ' + str(list(ddg_states.keys())))
logging.info('IDD devices: ' + str(list(idd_states.keys())))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT with result code "+str(rc))

    for ddg_name in ddg_states:
        global ddg_list
        ddg_device = DDGDevice(client, controllerId, ddg_name, ddg_states[ddg_name])
        ddg_list.append(ddg_device)
        ddg_device.start()

    for idd_name in idd_states:
        global idd_list
        idd_device = IDDDevice(client, controllerId, idd_name, idd_states[idd_name])
        idd_list.append(idd_device)
        idd_device.start()

    client.subscribe("/devices/+/controls/" + params.VOLTAGE_L1_NAME)
    client.subscribe("/devices/+/controls/" + params.VOLTAGE_L2_NAME)
    client.subscribe("/devices/+/controls/" + params.VOLTAGE_L3_NAME)
    client.subscribe("/devices/+/controls/" + params.CURRENT_L1_NAME)
    client.subscribe("/devices/+/controls/" + params.CURRENT_L2_NAME)
    client.subscribe("/devices/+/controls/" + params.CURRENT_L3_NAME)
    
     
def on_message(client, userdata, msg):

    global ddg_list
    global ddg_states  

    global idd_list
    global idd_states 

    device_name = msg.topic.split("/")[2]

    if device_name.startswith("b") and device_name.endswith("_DDG"):
        if device_name not in ddg_states:

            store.create_new_ddg(device_name)        
            ddg_device = DDGDevice(client, controllerId, device_name, ddg_states[device_name])
            ddg_list.append(ddg_device)
            ddg_device.start()

        for ddg in ddg_list:
            save = ddg.on_message(client, userdata, msg)
            if save:
                store.save_ddg_state(ddg_states)


    if device_name.startswith("b") and device_name.endswith("_IDD"):
        if device_name not in idd_states:

            store.create_new_idd(device_name)        
            idd_device = IDDDevice(client, controllerId, device_name, idd_states[device_name])
            idd_list.append(idd_device)
            idd_device.start()

        for idd in idd_list:
            save = idd.on_message(client, userdata, msg)
            if save:
                store.save_idd_state(idd_states)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_start()

while True:
    time.sleep(1800)
    logging.debug("Connected to MQTT "+str(client.is_connected()))
    store.save_ddg_state(ddg_states)
    store.save_idd_state(idd_states)
