from attr import fields
import pytest
import json

from kdblite.internals.datatools import DataTable,DataField, DataRow, TableJsonEncoder, ParamJsonEncoder




def test_tablejsonencoder():
    table = DataTable(Name = str, Age = int)
    index,row =table.new_row()
    field = row.get_field("Name")
    field.value = "John"
    assert TableJsonEncoder().default(field) == "John"
    assert TableJsonEncoder().default(row) == row.row()
    #check if error is raised if wrong argument is passed
    with pytest.raises(TypeError):
        TableJsonEncoder().default(1)

def test_paramjsonencoder():
    params= {"Name":str, "Age":int} 
    encoded_params = json.dumps(params,cls=ParamJsonEncoder)
    assert encoded_params == '{"Name": "", "Age": 0}'
    #check if error is raised if wrong argument is passed
    with pytest.raises(TypeError):
        ParamJsonEncoder().default(1)


def test_datafield():
    table = DataTable(Name = str, Age = int)
    index,row =table.new_row()
    field = row.get_field("Name")
    field.value = "John"
    assert field.value == "John"
    #check if error is raised if wrong argument is passed
    with pytest.raises(TypeError):
        field.value = 1
    #test setter with modifiers
    table.add_modifier("Name",lambda x:x.upper())
    field.value = "John"
    assert field.value == "JOHN"
    #test deleter
    del field.value
    assert field.value == None


def test_get_field():
    table = DataTable(Name = str, Age = int)
    index,row =table.new_row()
    field = DataField(row,table,"Name",str)
    assert field == row.get_field("Name")

