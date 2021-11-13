import os
import platform
from pathlib import Path
from configparser import ConfigParser
from kdblite.internals.const import TAB_EXT, KDBL_EXT, KFG_EXT, KDBASE, KDCONFIG, KDBDIR

SYSTEM = platform.system()
DBDIR = ""


class StoreManager:
    """
    Manages the access of the stores 
    """

    def __init__(self):
        if (KDBDIR in os.environ):
            self.db_dir = os.environ[KDBDIR]
        elif (SYSTEM == "Windows"):
            self.db_dir = os.environ["LOCALAPPDATA"]
        else:
            raise Exception("Set database directory before proceeding.")
        self.loaded_stores = list()
        self.loaded_store_inst = dict()

    def get_store(self,name):
        if name in self.loaded_stores:
            raise Exception(f"store {name} has already been loaded")
        return Store(self,load = name)

    def create_store(self,name):
        if name in self.loaded_stores:
            raise Exception(f"store {name} has already been created")
        return Store(self,create = name)

    

class Store:
    """
    Handles storage of database in memory
    """
    def __init__(self,storemanager,*,create = None,load = None):
        self._storemanager = storemanager
        self._name = str()
        self._tab_file = None
        self._kdbl_file = None
        self._kfg_file = None
        self.tab_repr = str()          # string representation of the table parameters
        self.kdbl_repr = str()         # string representatin of the table
        self.konfig = ConfigParser()
        self.loaded = False
        self.store_path = Path(storemanager.db_dir)
        if create:
            self.create(create)
        elif load:
            self.load(load)


    def load(self,name = None):
        sp = self.store_path/name                   #sp:store path
        if sp.is_dir():
            print("dir exists...")
            tab = sp/(name + TAB_EXT)                  #tab file
            kdbl = sp/(name + KDBL_EXT)                #kdbl file
            kfg = sp/(name + KFG_EXT)                  #kfg file
            if (tab.exists() and kdbl.exists() and kfg.exists()):
                self._tab_file = tab
                self._kdbl_file = kdbl
                self._kfg_file = kfg
                print("files exists...")
                
                #Migrate this code section to parenthesized context managers in python 310
                with kfg.open() as k:
                    config = ConfigParser()
                    config.read(k)
                    self.konfig = config
                with tab.open() as tb:
                    self.tab_repr = tb.read()
                with kdbl.open() as kdb:
                    self.kdbl_repr = kdb.read()

                self.store_path = sp
                self.loaded = True
                self._storemanager.loaded_stores.append(name)
                self._storemanager.loaded_store_inst[name] = self
                self._name = name
        else:
            raise Exception("No database to load, create store")

    def create(self,name):
        if self.loaded:
            raise Exception("store has already been loaded")
        sp = self.store_path/name                      #sp:store path
        sp.mkdir()                                     #will raise FileExistsError if directory exists
        
        # below is a hack I used to implement file creation
        tab = sp/(name + TAB_EXT)
        self._tab_file = tab
        tab.open(mode = "w").close()
        
        kdbl = sp/(name + KDBL_EXT)
        self._kdbl_file = kdbl
        kdbl.open(mode = "w").close()
        
        kfg = sp/(name + KFG_EXT)
        self._kfg_file = kfg
        kfg.open(mode = "w").close()

        self.store_path = sp
        self.loaded = True
        self._storemanager.loaded_stores.append(name)
        self._storemanager.loaded_store_inst[name] = self
        self._name = name

    def delete(self):
        if self.loaded:
            os.remove(str(self._tab_file))
            os.remove(str(self._kdbl_file))
            os.remove(str(self._kfg_file))
            self.store_path.rmdir()

            #restore to original setting
            self.loaded = False
            self.store_path = Path(DBDIR)
            self._tab_file = None
            self._kdbl_file = None
            self._kfg_file = None
            self._storemanager.loaded_stores.remove(self._name)
            del self._storemanager.loaded_store_inst[self._name]
            return
        raise Exception("Store not loaded or store does not exist")

    def save(self,table):
        #add an update trigger so that
        #saving only occurs when
        #the representation strings
        #have been modified

        #Migrate this code section to parenthesized context managers in python 310
        param,kdbl = table.encode()
        self.tab_repr = param
        self.kdbl_repr = kdbl
        with self._tab_file.open(mode = "w") as tb:
            tb.write(self.tab_repr)
        with self._kdbl_file.open(mode = "w") as kdb:
            kdb.write(self.kdbl_repr)
        with self._kfg_file.open(mode = "w") as k:
            self.konfig.write(k)
            
