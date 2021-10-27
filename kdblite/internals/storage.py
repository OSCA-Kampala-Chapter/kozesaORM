import os
import shutil
import io
import platform
from pathlib import Path
from configparser import ConfigParser
from const import TAB_EXT, KDBL_EXT, KFG_EXT, KDBASE, KDCONFIG

# target os currently is windows
# some few modifications can be made
# to run on other platforms

SYSTEM = platform.system()
DATA_DIR = ""

if (SYSTEM == "Windows"):
    DATA_DIR = os.environ["LOCALAPPDATA"]

class StoreManager(object):
    def __init__(self):
        self.db_dir = str()
        self.config_file = str()
        self.config = ConfigParser()
        self.path_cache = list()      #store recently searched directories
                                      #for fast subsequent searches
        self._load_db()

    def _load_db(self):
        if (DATA_DIR == ""):
            raise FileNotFoundError("Data directory not found")

        self.db_dir = DATA_DIR
        path = Path(self.db_dir)
        kdbase = path / KDBASE
        
        if kdbase.exists():
            kdconfig = kdbase / KDCONFIG
            if kdconfig.exists():
                self.config_file = kdconfig
                with open(self.config_file,"r") as kfg:
                    self.config.read_file(kfg)
        else:
            kdbase.mkdir()
            os.chdir(kdbase)
            open(KDCONFIG,"w").close()     #create config file
            self.config_file = KDCONFIG

        self.db_dir = path

    def get_database(self,name):
        if name in self.path_cache:
            return name
        else:
            for i in self.db_dir.iterdir():
                db_name = i.name
                self.path_cache.append(db_name)
                if (db_name == name):
                    return db_name
                



class Store(object):
    pass