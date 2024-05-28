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
        
        logging.debug("Load of configuration" )

        golden_p = Path(__file__).with_name(CfgFile)

        with golden_p.open("r") as golden_f:
            self.CfgData = yaml.safe_load(golden_f)

        system_p = Path("/etc/ddg-idd-driver/")/CfgFile

        if os.path.isfile(system_p):
            with system_p.open("r") as system_f:
                s_CfgData = yaml.safe_load(system_f)
                self.CfgData = self.CfgData | s_CfgData

        user_p = Path.home()/"ddg-idd-driver"/CfgFile

        if os.path.isfile(user_p):
            with open( user_p ) as user_f:
                u_CfgData = yaml.safe_load(user_f)
                self.CfgData = self.CfgData | u_CfgData

        self.host = self.CfgData["broker"]["host"]
        self.port = self.CfgData["broker"]["port"]

        logging.debug( 'Broker :' + str(self.host) + ':' + str(self.port) )
