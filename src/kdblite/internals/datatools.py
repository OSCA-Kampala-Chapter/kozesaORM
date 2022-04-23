from __future__ import annotations
from kdblite.internals.errors import ParamDoesnotExist,InvalidError
from json import JSONDecoder,JSONEncoder
from typing import Union,Callable,Any,Optional
from inspect import isclass,ismethod,isfunction

__all__ = ('DataField','DataRow','DataTable')

class TableJsonEncoder(JSONEncoder):
    def __init__(self,**kwargs):
        super(TableJsonEncoder,self).__init__(**kwargs)

    def default(self,obj:Union[DataField,DataRow]) -> Union[int,dict]:
        if isinstance(obj,DataField):
            return obj.value
        elif isinstance(obj,DataRow):
            return obj.row()
        super(TableJsonEncoder,self).default(obj)

class ParamJsonEncoder(JSONEncoder):
    def __init__(self,**kwargs):
        super(ParamJsonEncoder,self).__init__(**kwargs)

    def default(self,obj):
        if isclass(obj):
            if obj is int:
                return 0
            elif obj is str:
                return ""
            elif obj is float:
                return 0.0
        super(ParamJsonEncoder,self).default(obj)

        
class DataField:

    def __init__(self,row:DataRow,
                 table:DataTable,
                 parameter:str,
                 data_type:Union[int,str,float]):
        self._row = row
        self._table = table
        self._parameter = parameter
        self._data_type = data_type
        self._value = None

    def __eq__(self,other):
        if isinstance(self, other.__class__):
            return self._parameter == other._parameter


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,new_value):
        if isinstance(new_value,self._data_type):
            if self._table.has_modifier(self._parameter):
                self._value = self._table.modifiers[self._parameter](new_value)
                return
            self._value = new_value
            return
        raise TypeError("Value is of wrong data type")

    @value.deleter
    def value(self):
        if self._value:
            self._value = None
        return

    def field_info(self):
        return (self._row,self._table,self._parameter,self._data_type)



class DataRow:

    def __init__(self,table:DataTable,
                 parameters:dict[str,Union[int,str,float]]):
        self._table = table
        self._parameters = parameters
        self._row = dict()
        for param,data_type in self._parameters.items():
            field = DataField(self,self._table,param,data_type)
            self._row[param] = field

    def get_field(self,parameter):
        try:
            field = self._row[parameter]
        except KeyError:
            raise ParamDoesnotExist("The given parameter does not exist")
        else:
            return field

    def fields(self):
        for param,field in self._row.items():
            yield param,field

    def __iter__(self):
        return self.fields()

    def extend_row(self,parameter,data_type):        #This function is meant to be called by table operations during expansion
        self._parameters[parameter] = data_type
        field = DataField(self,self._table,parameter,data_type)
        self._row[parameter] = field

    def row(self):
        return self._row


class DataTable:

    def __init__(self,**parameters):
        self._table = list()
        self._modifiers = dict()
        self._checkers = dict()
        self._index = 0
        self._parameters = dict()
        if parameters:
            self.add_parameter(**parameters)
            
    def add_parameter(self,**parameters):
        for datatype in parameters.values():
            if (not datatype in [int,str,float]):
                raise ValueError("parameters must be of type int, str or float")
        else:
            self._parameters = parameters

    @property
    def modifiers(self):
        return self._modifiers

    def new_row(self):
        try:
            if (len(self._parameters) == 0):
                raise InvalidError
        except InvalidError as ie:
            raise ie("cannot create row with empty parameters")
        else:
            row = DataRow(self,self._parameters)
            self._table.append(row)
            temp_index = self._index
            self._index += 1
            return temp_index,row
        
    def rows(self) -> DataRow:
        for row in self._table:
            yield row

    def delete(self,item:Union[int,DataRow]) -> bool:
        if isinstance(item,int):
            del self._table[item]
        elif isinstance(item,DataRow):
            self._table.remove(item)
        return True

    def get_row(self,index):
        return self._table[index]

    def _encode_table(self):
        encoder = TableJsonEncoder()
        encoded = encoder.encode(self._table)
        return encoded
    
    def _encode_parameters(self):
        encoder = ParamJsonEncoder()
        encoded = encoder.encode(self._parameters)
        return encoded

    def encode(self) -> tuple:
        p_encode = self._encode_parameters()
        t_encode = self._encode_table()
        return p_encode,t_encode
    
    def _table_decoder(self,obj):
        row = DataRow(self,self._parameters)
        for param,val in obj.items():
            for p,f in row.fields():
                if (p == param):
                    f.value = val
        return row

    def _param_decoder(self,obj):
        params = dict()
        for param,datatype in obj.items():
            params[param] = type(datatype)
        return params

    def _decode_table(self,table_string):
        decoder = JSONDecoder(object_hook = self._table_decoder)
        decoded = decoder.decode(table_string)
        return decoded

    def _decode_params(self,param_string):
        decoder = JSONDecoder(object_hook = self._param_decoder)
        decoded = decoder.decode(param_string)
        return decoded

    def initialize(self,params:str,table:str) -> None:
        self._parameters = self._decode_params(params)
        self._table = self._decode_table(table)

    def has_modifier(self,param):
        if param in self._modifiers:
            return True
        return False
    
    def add_modifier(self,param:str,modifier:Callable[...,Any]) -> None:
        if param in self._parameters:
            self._modifiers[param] = modifier
            return
        raise ParamDoesnotExist("The given parameter does not exist")

    def add_checker(self,param:str,checker:Callable[Union[str,int,float],Union[str,int,float]]) -> None:
        if param in self._parameters:
            self._checkers[param] = checker
            return
        raise ParamDoesnotExist("The given parameter does not exist")

    def get_column(self,param,checker:Callable[Union[str,int,float],Union[str,int,float]] = None) -> list:
        """ Use: Return a list of items in a column. If checker is provided, then checker should be a function that takes in a single value
                which is the item found in the column, and then perform some validation tests on it.
        """
        
        if (isfunction(checker) or ismethod(checker)):
            column = [checker(row.get_field(param).value) for row in self.rows()]
            return column
        elif checker is None:
            try:
                checker = self._checkers[param]
            except KeyError:
                column = [row.get_field(param).value for row in self.rows()]
                return column
            else:
                column = [checker(row.get_field(param).value) for row in self.rows()]
                return column
        else:
            raise ValueError("checker is supposed to be a function or method")       
    
    def validate_column(self, column_name) -> bool:
        """
        Use:    Makes a check on a given column to determine its datatype integrity and whether it exists as a parameter. leaves a table with only valid columns
        Why:    Since the rows.row() is a dictionary, it can be updated with other keys and items with different datatypes. the
                keys in this case however do not appear in the self._parameters and the datatypes of items can be mixed or even not be str or int datatypes 
        """
        if column_name in self._parameters:#checks if column_name added to self._parameters
            valid_datatypes = [datatype for datatype in self._parameters.values()]
            column = self.get_column(column_name)
            column_datatype = type(column[0])
            column_length = len(column)
            
            if column_datatype in valid_datatypes:#checks if datatype is of str of int type
                count = 0
                for i in column:
                    if isinstance(i, column_datatype):#checks every instance of the list to determine if they are all the same datatype
                        count += 1
            else:
                print("Invalid datatype in '{}'. deleting {}".format(column_name, column_name))
                deleted_values = [row.row().pop('{}'.format(column_name)) for row in self.rows()]#creates a list of deleted values
                return False 
            
            if count == column_length:
                return True

            else:#runs if list has more than one datatype
                print("Invalid datatype in '{}'. deleting {}".format(column_name, column_name))
                deleted_values = [row.row().pop('{}'.format(column_name)) for row in self.rows()]#creates a list of deleted values
                return False
        else:
            print("parameter '{}' instantiated abnormally. deleting...".format(column_name))
            deleted_values = [row.row().pop('{}'.format(column_name)) for row in self.rows()]#creates a list of deleted values
            return False
        return column

        
