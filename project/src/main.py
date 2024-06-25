

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
import signal

from my_config import MyConfig

DEBUG_LVL_KEY = "-d" # debug/info

if(DEBUG_LVL_KEY in sys.argv):
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO 

controllerId = store.get_controller_id()
ddg_states = store.get_ddg_states()
idd_states = store.get_idd_states()

ddg_list = []
idd_list = []

logging.basicConfig(level=loglevel)

logging.info("\n\n\n ***DDG & IDD Driver Started***\n")
logging.info('DDG devices: ' + str(list(ddg_states.keys())))
logging.info('IDD devices: ' + str(list(idd_states.keys())))

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    client.disconnect()
    sys.exit()

verbose = False

def debug(msg):
    if verbose:
        print (msg + "\n")

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
            logging.debug("New DDG device detected on Broker: " + device_name)
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


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    Cfg = MyConfig()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(Cfg.host, Cfg.port)
    client.loop_start()

    while True:
        time.sleep(1800)
        logging.debug("Connected to MQTT "+str(client.is_connected()))
        store.save_ddg_state(ddg_states)
        store.save_idd_state(idd_states)
