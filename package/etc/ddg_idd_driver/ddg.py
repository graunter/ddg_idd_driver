import logging
import paho.mqtt.client
from threading import Timer         
import datetime
import json
from threading import Thread
import time
import params

DDG_SEND_STATE_TIME = 7200 # 120min
DDG_SEND_ALIVE_TIME = 300 # 5min

class DDGDevice:
    
    def __init__(self, mqtt_client, controllerId, device_name, device_state):
        self.mqtt_client = mqtt_client
        self.device_name = device_name
        self.controllerId = controllerId
        self.device_state = device_state

        print("self.device_name = " + self.device_name)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        logging.debug("DDG-driver Received message: "+ msg.topic+" "+str(msg.payload))

        
        if msg.topic.endswith(params.VOLTAGE_L1_NAME) and msg.topic.startswith("/devices/" + self.device_name):

            save = False

            try:
                U = float(msg.payload)
            except Exception as e:
                logging.debug("wrong topic value.")
                return save
            
            if U > 100.0:
                active = 1
            else:
                active = 0

            if self.device_state["active"] != active:

                save = True
                now_time = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

                #state changed
                if active == 1:
                    # ddg ON
                    logging.debug("DDG TURNED ON")
                    self.device_state["last_start"] = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

                    msgStartTime = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/last start time", "time":now_time, "value":str(self.device_state["last_start"])}}, "status": "UPDATE"}
                    self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgStartTime)), qos=0, retain=False)
                else:
                    # ddg OFF
                    logging.debug("DDG TURNED OFF")
                    self.device_state["last_stop"] = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

                    msgStopTime = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name+ "/controls/stop time", "time":now_time, "value":str(self.device_state["last_stop"])}}, "status": "UPDATE"}
                    self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgStopTime)), qos=0, retain=False)

                msgActive = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/active", "time":now_time, "value":str(active)}}, "status": "UPDATE"}
                self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgActive)), qos=0, retain=False)

            self.device_state["active"] = active
            return save
     
    def start(self):

        send_state_th = Thread(target=self.send_state_th_make)
        send_state_th.daemon = True
        send_state_th.start()

        send_alive_th = Thread(target=self.send_alive_th_make)
        send_alive_th.daemon = True
        send_alive_th.start()

    def send_state_th_make(self):
        while True:

            logging.debug("Sending ddg state")
            self.send_ddg_state()
            time.sleep(DDG_SEND_STATE_TIME)

    def send_alive_th_make(self):
        while True:

            logging.debug("Sending ddg alive")
            self.send_ddg_alive()
            time.sleep(DDG_SEND_ALIVE_TIME)

    def send_ddg_alive(self):
        now_time = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")
        msgAlive = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/alive", "time":now_time, "value":now_time}}, "status": "UPDATE"}
        self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgAlive)), qos=0, retain=False)
        logging.debug(str(json.dumps(msgAlive)))


    def send_ddg_state(self):
    # for ddg in ddg_list:

        now_time = str(datetime.datetime.now(tz=datetime.timezone.utc)).replace(" ", "T").replace("+00:00","")

        msgActive = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/active", "time":now_time, "value":str(self.device_state["active"])}}, "status": "UPDATE"}
        msgStopTime = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/stop time", "time":now_time, "value":str(self.device_state["last_stop"])}}, "status": "UPDATE"}
        msgStartTime = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/last start time", "time":now_time, "value":str(self.device_state["last_start"])}}, "status": "UPDATE"}
        msgModel = {"type":{"data":{"controllerId":self.controllerId, "topic":"/devices/" + self.device_name + "/controls/ddg model", "time":now_time, "value":self.device_state["model"]}}, "status": "UPDATE"}

        self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgActive)), qos=0, retain=False)
        if self.device_state["last_stop"] != "None":
            self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgStopTime)), qos=0, retain=False)

        if self.device_state["last_start"] != "None":
            self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgStartTime)), qos=0, retain=False)

        self.mqtt_client.publish("/Controller/Out/Value", payload=str(json.dumps(msgModel)), qos=0, retain=False)

        logging.debug(str(json.dumps(msgActive)))
        logging.debug(str(json.dumps(msgStopTime)))
        logging.debug(str(json.dumps(msgStartTime)))
        logging.debug(str(json.dumps(msgModel)))


