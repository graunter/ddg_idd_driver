import logging
import paho.mqtt.client
from threading import Timer         
import datetime
import json
import yaml
from threading import Thread
import time
import params
from pathlib import Path

IDD_SEND_STATE_TIME = 7200 # 120min
IDD_COUNTER_PING_TIME = 60 # 1min

class IDDDevice:

    def __init__(self, mqtt_client, controllerId, device_name, device_state):
        self.mqtt_client = mqtt_client
        self.device_name = device_name
        self.controllerId = controllerId
        self.device_state = device_state
        self.ping_counter = 0

    def on_message(self, client, userdata, msg):
        logging.debug("IDD-driver Received message: "+ msg.topic+" "+str(msg.payload))

        save = False

        if msg.topic.startswith("/devices/"+ self.device_name):

            self.ping_counter = 0
            
            try:
                value = float(msg.payload)
                if msg.topic.endswith(params.CURRENT_L1_NAME): self.device_state[params.CURRENT_L1_NAME] = value
                elif msg.topic.endswith(params.CURRENT_L2_NAME): self.device_state[params.CURRENT_L2_NAME] = value
                elif msg.topic.endswith(params.CURRENT_L3_NAME): self.device_state[params.CURRENT_L3_NAME] = value
                elif msg.topic.endswith(params.VOLTAGE_L1_NAME): self.device_state[params.VOLTAGE_L1_NAME] = value
                elif msg.topic.endswith(params.VOLTAGE_L2_NAME): self.device_state[params.VOLTAGE_L2_NAME] = value
                elif msg.topic.endswith(params.VOLTAGE_L3_NAME): self.device_state[params.VOLTAGE_L3_NAME] = value
            except Exception as e:
                logging.debug("wrong topic value.")
                return save
                
            if self.device_state[params.VOLTAGE_L1_NAME] == None or self.device_state[params.VOLTAGE_L2_NAME] == None or self.device_state[params.VOLTAGE_L3_NAME] == None:
                logging.debug("IDD-driver ERROR Not enough voltage data")
                return save
            
            if self.device_state[params.CURRENT_L1_NAME] == None or self.device_state[params.CURRENT_L2_NAME] == None or self.device_state[params.CURRENT_L3_NAME] == None:
                logging.debug("IDD-driver ERROR Not enough current data")
                return save
            
            #logic:

            if self.device_state["state"] == "offline":
                save = True

            if self.device_state[params.VOLTAGE_L1_NAME] < self.config['VThreshold'] or self.device_state[params.VOLTAGE_L2_NAME] < self.config['VThreshold'] or self.device_state[params.VOLTAGE_L3_NAME] < self.config['VThreshold']:
                voltage = 0
            else:
                voltage = 1

            if self.device_state["voltage"] != voltage:
                logging.debug("IDD-driver. CHANGED VOLTAGE" + str(voltage))
                save = True

            self.device_state["voltage"] = voltage


            if self.device_state[params.CURRENT_L1_NAME] < self.config['IThreshold'] and self.device_state[params.CURRENT_L2_NAME] < self.config['IThreshold'] and self.device_state[params.CURRENT_L3_NAME] < self.config['IThreshold']:
                in_work = 0
            else:
                in_work = 1

            if self.device_state["in_work"] != in_work:
                logging.debug("IDD-driver. CHANGED CURRENT" + str(in_work))
                save = True

            self.device_state["in_work"] = in_work

            if save:
                #any changes happened

                now_time = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

                if self.device_state["voltage"] == 0:

                    self.device_state["state"] = "no_voltage"
                    self.device_state["changed_time"] = now_time

                else:

                    if self.device_state["in_work"] == 1:   

                        self.device_state["state"] = "working"
                        self.device_state["changed_time"] = now_time

                    else:

                        self.device_state["state"] = "reserved"
                        self.device_state["changed_time"] = now_time

                msgState = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/state", "time":now_time, "value":str(self.device_state["state"])}}, "status": "UPDATE"}    
                msgChanged = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/changed", "time":now_time, "value":str(self.device_state["changed_time"])}}, "status": "UPDATE"}  

                self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgState)), qos=0, retain=False)
                self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgChanged)), qos=0, retain=False)   
        
        return save
    

    def start(self):

        ConfigLocation = Path(__file__).with_name('config.yaml')
        with ConfigLocation.open('r') as cfg_file:
            self.config = yaml.safe_load(cfg_file)

        send_state_th = Thread(target=self.send_state_th_make)
        send_state_th.daemon = True
        send_state_th.start()

        counter_ping_th = Thread(target=self.increment_counter_ping)
        counter_ping_th.daemon = True
        counter_ping_th.start()

    def send_state_th_make(self):
        while True:

            logging.debug("Sending idd state")
            self.send_idd_state()
            time.sleep(IDD_SEND_STATE_TIME)

    def increment_counter_ping(self):
        while True:
            time.sleep(1)

            if self.ping_counter >= IDD_COUNTER_PING_TIME:
                #counter offline
                
                if self.device_state["state"] != "offline":
                    logging.debug("IDD" + self.device_name + " OFFLINE")

                    self.device_state["state"] = "offline"

                    now_time = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

                    msgState = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/state", "time":now_time, "value":str(self.device_state["state"])}}, "status": "UPDATE"}
                    self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgState)), qos=0, retain=False)
            else:
                self.ping_counter = self.ping_counter + 1

    def send_idd_state(self):

        logging.debug("IDD-driver Try to send states...")
        if self.device_state[params.VOLTAGE_L1_NAME] == None or self.device_state[params.VOLTAGE_L2_NAME] == None or self.device_state[params.VOLTAGE_L3_NAME] == None:
            logging.debug("IDD-driver ERROR Not enough voltage data")
            return

        if self.device_state[params.CURRENT_L1_NAME] == None or self.device_state[params.CURRENT_L2_NAME] == None or self.device_state[params.CURRENT_L3_NAME] == None:
            logging.debug("IDD-driver ERROR Not enough current data")
            return

        now_time = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

        #prepare messages:
        msgState = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/state", "time":now_time, "value":str(self.device_state["state"])}}, "status": "UPDATE"}
        msgChanged = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/changed", "time":now_time, "value":str(self.device_state["changed_time"])}}, "status": "UPDATE"}

        #sending messages:
        if self.device_state["state"] != "unknown":
            self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgState)), qos=0, retain=False)

        if self.device_state["changed_time"] != None:
            self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgChanged)), qos=0, retain=False)

        logging.debug(str(json.dumps(msgState)))
        logging.debug(str(json.dumps(msgChanged)))