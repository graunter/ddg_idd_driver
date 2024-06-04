import os
import json
import yaml
import logging
import datetime
from pathlib import Path
from my_config import MyConfig
from collections import defaultdict
from constants import *

controllerId = ""
ddg_states = {}
idd_states = {}

def get_ddg_states():
        
    global ddg_states 
    
    InFileNameUser = Path.home() / DDG_STATE_FILE
    InFileNameSys = Path("/etc/") / DDG_STATE_FILE

    ddg_states_user = defaultdict(dict)
    try:
        if os.path.isfile(InFileNameUser):
            with open(InFileNameUser) as f:
                ddg_states_user = json.load(f)
    except Exception as e:
        logging.info("wrong user file with DDG states")

    ddg_states_sys = defaultdict(dict)
    try:
        if os.path.isfile(InFileNameSys):
            with open(InFileNameSys) as f:
                ddg_states_sys = json.load(f)  
    except Exception as e:
        logging.info("threre is some problem with system state file")                

    ddg_states_total = ddg_states_user | ddg_states_sys

    for dev in ddg_states_total:
        device_name = dev
        value_usr = ddg_states_user[device_name]

        ddg_states_total[device_name]["model"] = value_usr.get("model", ddg_states_total[device_name]["model"])
        ddg_states_total[device_name]["is_panel"] = value_usr.get("is_panel", ddg_states_total[device_name]["is_panel"]) 

    ddg_states = ddg_states_total

    return ddg_states


def create_new_ddg(device_name):
    global ddg_states
    if device_name in ddg_states:
        logging.error("Error. Try to create DDG copy")
        return

    Cfg = MyConfig()

    ddg_states[device_name] = {
            "last_start":"None",
            "last_stop":"None",
            "active":0,
            "model":"place DDG model here",
            "is_panel":Cfg.CfgData['IsPanel'],
    }
    
    save_ddg_state(ddg_states)
    logging.info("Creating new Device:" + device_name)
    
    return ddg_states[device_name]


def save_ddg_state(list):   
    logging.debug("Saving ddg state")

    OutFileNameUsr = Path.home() / DDG_STATE_FILE
    os.makedirs(os.path.dirname(OutFileNameUsr), exist_ok=True)

    OutFileNameSys = Path("/etc/") / DDG_STATE_FILE
    os.makedirs(os.path.dirname(OutFileNameSys), exist_ok=True)

    with open(OutFileNameUsr, 'w+') as outfile:
        json.dump(list, outfile, indent=4)
    
    with open(OutFileNameSys, 'w+') as outfile:
        json.dump(list, outfile, indent=4)
    
    logging.debug(str(list))


def reset_idd(device_name):

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

    return idd_states[device_name]


def create_new_idd(device_name):
    global idd_states
    if device_name in idd_states:
        logging.error("Error. Try to create DDG copy")
        return

    reset_idd(device_name)

    save_idd_state(idd_states)
    logging.info("Creating new Device:" + device_name)
    
    return idd_states[device_name]


def get_idd_states():

    global idd_states 

    # на данный момент - пользовательских данных в конфигурации вводного устройства нету
    '''
    InFileNameUsr = Path.home() / IDD_STATE_FILE

    idd_states_usr = {}
    if os.path.isfile(InFileNameUsr):
        with open(InFileNameUsr) as f:            
            idd_states_usr = json.load(f)
    '''

    InFileNameSys = Path("/etc/") / IDD_STATE_FILE
    
    idd_states_sys = {}
    if os.path.isfile(InFileNameSys):
        with open(InFileNameSys) as f:            
            idd_states_sys = json.load(f)   

    idd_states = idd_states_sys

    return idd_states

    
def save_idd_state(list):
    logging.debug("Saving idd state : " + str(list))
    
    OutFileNameUsr = Path.home() / IDD_STATE_FILE
    os.makedirs(os.path.dirname(OutFileNameUsr), exist_ok=True)

    OutFileNameSys = Path("/etc/") / IDD_STATE_FILE
    os.makedirs(os.path.dirname(OutFileNameSys), exist_ok=True)

    # текущее состояние сохраняется в пользовательскую папку для информации только - как раньше
    with open(OutFileNameUsr, 'w+') as outfile:
        json.dump(list, outfile, indent=4)

    # все настройки сохраняются в системную папку без прореживания
    '''    
    for dev in list:
        device_name = dev
        value = list[device_name]
        sys_list = defaultdict(dict)
        sys_list[device_name]["changed_time"] = value["changed_time"]
        sys_list[device_name]["in_work"] = value["in_work"]
        sys_list[device_name]["state"] = value["state"]
    '''

    sys_list = list
    with open(OutFileNameSys, 'w+') as outfile:
        json.dump(sys_list, outfile, indent=4)


def get_controller_id():
    global controllerId

    with open(INDEX_FILE_FULL_NAME, 'r') as controllerId:
        controllerId = controllerId.read().replace("\n","")
    
    return controllerId