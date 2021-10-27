from errors import ParamExists,ParamDoesnotExist,InvalidError

import json


class DataField:
    
    __slots__ = ("_row","_col","_val","_datatype")
    def __init__(self,row=0, col=0, val=0,datatype=None):
        self._row = row
        self._col = col
        self._val = val
        self._datatype = datatype

    def field(self):
        return self._row,self._col,self._val,self._datatype


class DataRow:
    
    __slots__ = ("_table","_params","_row")
    def __init__(self,table,params):
        self._table = table
        self._params = params
        self._row = dict()
        for key in self._params:
            self._row.setdefault(key)
        self._table.get_table(self).append(self._row)

    def _typecheck(self,param,val):
        param_type = self._params[param]
        if isinstance(val,param_type):
            return True
        print(param_type)
        return False

    def insert_value(self,param,val):
        if (param in self._row):
            if self._typecheck(param,val):
                if (self._row[param] != None):
                    raise ParamExists("the following parameter already has a value \n try using update_value")
                self._row[param] = val
                return
            raise TypeError("Wrong datatype")
        raise ParamDoesnotExist("Given parameter does not exist")


    def get_value(self,param):
        if (param in self._row):
            return self._row[param]
        raise ParamDoesnotExist("Given parameter does not exist")


    def update_value(self,param,val):
        if (param in self._row):
            if self._typecheck(param,val):
                self._row[param] = val
                return
            raise TypeError("Wrong datatype")
        raise ParamDoesnotExist("Given parameter does not exist")


    def remove_value(self,param):
        if (param in self._row):
            self._row[param] = None
            return
        raise ParamDoesnotExist("Given parameter does not exist")

    def get_row(self):
        return self._row




class DataTable:
    
    __slots__ = ("_table","_tab_file","_parameters","_kdbl_file","loaded")
    def __init__(self,kdbl_file = None,tab_file = None):
        self._table = list()
        self._tab_file = tab_file
        self._parameters = dict()
        self._kdbl_file = kdbl_file
        self.loaded = False
        if (kdbl_file and tab_file):
            self.loaded = self.load_table(tab_file,kdbl_file)


    def _load_kdbl_file(self,kdbl_file = None):
        if kdbl_file:
            self._kdbl_file = kdbl_file
            self._table = json.load(self._kdbl_file)
            return True
        return False

    def _load_tab_file(self,tab_file = None):
        if tab_file:
            self._tab_file = tab_file
            self._parameters = json.load(self._tab_file)
            return True
        return False


    def close(self):
        json.dump(self._parameters,self._tab_file)
        json.dump(self.table,self._kdbl_file)
        return

    def load_table(self,tab_file,kdbl_file):
        try:
            load = (self._load_tab_file(tab_file) and self._load_kdbl_file(kdbl_file))
        except:
            return False
        else:
            return load

    def get_table(self,row):
        # should mainly be used by the row object
        # to append its self to the Table list.
        # other form of usage should be prohibited
        
        if isinstance(row,DataRow):
            return self._table
        raise InvalidError("Invalid Access to Table")

    def create_table(self,**params): #params is a dictionary containing parameter:type pairs
        if (len(self._parameters) <= 0):
            self._parameters = params
        return self._parameters    # for debugging purposes, but return something else

    def create_row(self):
        if self._parameters:
            row = DataRow(self,self._parameters)
            return row
        return None

    def get_rows(self):
        rows = [row for row in self._table]
        return rows

    def get_columns(self,param):
        col = [row.get_value(param) for row in self._table]
        return col

        
    
