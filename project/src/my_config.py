import yaml
import os
from pathlib import Path
from constants import *
from threading import Lock, Thread
import logging

class MySingletone(type):

    _instances = {}
    _lock: Lock = Lock()
  
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class MyConfig(metaclass=MySingletone):

    def __init__(self, CfgFile = CONFIG_FILE) -> None:

        self.CfgData = {}
        self.host = "localhost"
        self.port = 1883
        self.CfgData["VThreshold"] = 100
        self.CfgData["IThreshold"] = 1.0
        self.CfgData["IsPanel"] = False
        self.CfgData["def_model_name"] = "Def name"
        
        logging.debug("Load of configuration" )
        
        golden_p = Path(__file__).with_name(CfgFile)
        system_p = Path( SYSTEM_PATH + COMMON_PATH )/CfgFile
        user_p = Path.home()/COMMON_PATH/CfgFile

        logging.debug('golden file: ' + str(golden_p))
        logging.debug('system file: ' + str(system_p))
        logging.debug('user file: ' + str(user_p))

        cfg_files = [golden_p, system_p, user_p]

        for u_file in cfg_files:
            try:
                with u_file.open("r") as user_f:
                    u_CfgData = yaml.safe_load(user_f)
                    self.extract_config(u_CfgData)
            except Exception as e:
                    logging.error("YAML file " + str(u_file) + " is incorrect and will be skipped: " + ': Message: ' + format(e) )
                    pass     


    def extract_config(self, CfgData: list):
                
        Broker = CfgData.get("broker", {})

        if Broker is not None:
            self.host = Broker.get("host", self.host)
            self.port = Broker.get("port", self.port)                 


        self.CfgData["VThreshold"] = CfgData.get("VThreshold", self.CfgData["VThreshold"])
        self.CfgData["IThreshold"] = CfgData.get("IThreshold", self.CfgData["IThreshold"])
        self.CfgData["IsPanel"] = CfgData.get("IsPanel", self.CfgData["IsPanel"] )
        self.CfgData["def_model_name"] = CfgData.get("def_model_name", self.CfgData["IsPanel"] )


if __name__ == "__main__":
        Cfg = MyConfig()