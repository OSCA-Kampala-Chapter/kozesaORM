#constants used through out the program

TAB_EXT = ".tab"           #extension for the tab file
KDBL_EXT = ".kdbl"         #extension for the kdbl file 
KFG_EXT = ".kfg"           #extension for the kfg file
KDCONFIG = "kdbase.kfg"    #name of the kfg file used in the database directory
KDBASE = "kdbase"          #name of the database directory

class Comparison(object):
    __slots__ = ("IN","LT","LTE","GT","GTE")
    def __init__(self):
       self.IN = 1
       self.LT = 2
       self.LTE = 3
       self.GT = 4
       self.GTE = 5

class Types(object):
    __slots__ = ("String","Integer","Float")
    def __init__(self):
        self.String = str()
        self.Interger = int()
        self.Float = float()

comparison = Comparison()
