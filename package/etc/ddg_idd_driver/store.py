import os.path
import json
import logging
import datetime

controllerId = ""
ddg_states = {}
idd_states = {}

def get_ddg_states():
        
        global ddg_states 
        
        if os.path.isfile("/etc/ddg_idd_driver/ddg_states.json"):
            with open('/etc/ddg_idd_driver/ddg_states.json') as f:
                ddg_states = json.load(f)

        return ddg_states


def create_new_ddg(device_name):
    global ddg_states
    if device_name in ddg_states:
        logging.error("Error. Try to create DDG copy")
        return

    ddg_states[device_name] = {"last_start":"None", "last_stop":"None", "active":0, "model":"place DDG model here"}
    save_ddg_state(ddg_states)
    logging.info("Creating new Device:" + device_name)
    
    return ddg_states[device_name]




def save_ddg_state(list):   
    logging.debug("Saving ddg state")
    with open("/etc/ddg_idd_driver/ddg_states.json", "w") as outfile:
        json.dump(list, outfile, indent=4)

    logging.debug(str(list))



def create_new_idd(device_name):
    global idd_states
    if device_name in idd_states:
        logging.error("Error. Try to create DDG copy")
        return

    idd_states[device_name] = {}
    idd_states[device_name]["Urms L1"] = None
    idd_states[device_name]["Urms L2"] = None
    idd_states[device_name]["Urms L3"] = None
    idd_states[device_name]["Irms L1"] = None
    idd_states[device_name]["Irms L2"] = None
    idd_states[device_name]["Irms L3"] = None

    idd_states[device_name]["changed_time"] = None
    idd_states[device_name]["voltage"] = None
    idd_states[device_name]["in_work"] = None
    idd_states[device_name]["state"] = "unknown"

    save_idd_state(idd_states)
    logging.info("Creating new Device:" + device_name)
    
    return idd_states[device_name]


def get_idd_states():

    global idd_states 

    if os.path.isfile("/etc/ddg_idd_driver/idd_states.json"):
        with open('/etc/ddg_idd_driver/idd_states.json') as f:
            idd_states = json.load(f)

    return idd_states

    
def save_idd_state(list):
    logging.debug("Saving idd state : " + str(list))
    with open("/etc/ddg_idd_driver/idd_states.json", "w") as outfile:
        json.dump(list, outfile, indent=4)




def get_controller_id():
    global controllerId

    with open('/var/inspark/index', 'r') as controllerId:
        controllerId = controllerId.read().replace("\n","")
    
    return controllerId