import yaml
import os
from pathlib import Path
from constants import *

class MyConfig:

    def __init__(self, CfgFile = CONFIG_FILE) -> None:
        
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
