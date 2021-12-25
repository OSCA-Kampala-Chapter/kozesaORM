![kozesalite logo](/docs/dblite2.png)
# kozesaDBLite
### Introduction
KozesaDBLite is a light weight table based database framework developed in Python.
The database was originally developed to power the Kozesa BMS(Business Management System)
software suite, a collection of frequently used business management software which
can be used for free.
The name Kozesa is a ganda word meaning "use". The symbolism is that the tools is for anyone
to use and customize freely.

### Features
* Stores relational data in form of a table
* Enforces type restriction, that is, all data in the table column is on the same data type
* Table can have modifiers, these are python functions which perform extra calculation on data before adding it to the table
* Table can also have checkers, these are python functions which filter data in a table column and retuen customized data during a query

To install kozesaDBLite, copy and paste the command below in your terminal
``` bash
pip install git+https://github.com/ht-thomas/kozesaDBLite.git 
```
### Architecture
kozesadblite implements a relational database represented as a table.
Three main classes are used to construct the table. These include the DataTable, which represents the entire table,
The DataRow which represents the table row and the DataField which represnts the specific location in the database
where the Column and Row intersect. The Columns of the table are of specific data types. Currently, the supported
data types are python strings and integers, but these are capable of represent a wide range of data.
![Table](/docs/table.png)

Storage of the database on disk is handled by the Store and StoreManager classes.
The Store handles the actual storage and loading of the database from disk, while StoreManager handles access to Stores

### Usage
In order to create a table, import Table from kdblite
```python
from kdblite import Table
table = Table(Name = str, Age = int)
```
the above code creates a Table with Name and Age as parameters with string and integer as data types respectively.
You can also create a Table instance and add parameters to the table using the add_parameter method.
```python
from kdblite import Table
table = Table()
table.add_parameter(Name = str,Age = int)
```
In to add a row to the table, use the new_row method of the Table class. This returns a tuple of index and DataRow object

```python
index,row = table.new_row()
```
The index represents the position of the row in the table. The row object returned is an instance of DataRow, and can be used to
aquire a field from the table. In order to get a field from DataRow, use the get_field method.

```python
field = row.get_field("Name")
```
pass the name of the parameter you want to access into the get_field method and you will be returned a field class from that parameter.
To add a value to the field, you can just assign any object of valid data type to the the value attribute of the field class.

```python
field.value = "Okello Stephen"
```
This will assign the name Okello Stephen as the field value and it will be placed in the table.
If the object added if not of the same data type as the column in which it's being added, an Excpetion is rise showing that
the value added is of wrong data type

```python
field.value = 25   # will raise an error
```
In order to see a string representation of the table, use the encode method of the table. It shall return a tuple of two strings
the first representing the parameters of the table and the second representing the actual table

```python
table.encode()    #param_string,table_string
```


To save the table on disk, we need the StoreManager.
Before importing the StoreManager however, for other operating systems other than the Windows operating system, you have to
set the path to the directory you want to save the database by creating an environment variable called "KDBDIR" and assigning it
the path to the directory you want. For Windows OS, if the "KDBDIR" environment variable is not defined, it shall use "LOCALAPPDATA"
as the default path. On other systems, an error shall be raised instead, telling you to set the environment variable before proceeding

```python
import os
os.environ["KDBDIR"] = os.getcwd() #this is not the ideal way of assigning environment variables
```
The above code assigns the current working directory as the database storage directory. This is meant to be an example and should not be
used in practice unless the developer knows what they are doing. The environment variables assigned this way are also temporary, and hence
shall be lost when the program ends. In order to set environment variables permanently, follow the instructions of your operating system
on how to do it.
Once the environment variable has been set, it's time to import the StoreManager.

```python
from kdblite import StoreManager # the actual class is actually StoreManager
sm = StoreManager()
s = sm.create_store("students")
```
Instantiate the StoreManager class and use the create_store method to create the store. A Store class is returned which we ca use to store
the database on disk. If students is already loaded, it will raise an exception instead. You shouldn't create and already created database.
"students" is the name of the database that is to be created.
In order to save the table, use the save method of the Store class and pass in the table as the argument

```python
s.save(table)
```
The table shall then be saved in the directory specified by the environment variable.
The database is however store in form of three files:
* the tab file which conatins information about the table parameters and data types
* the kdbl file which conatins the actual representation of the table, and finally,
* the kfg file which holds configuration data for the database
The kfg file has not yet been used however, but exists for future functinality extension

In order to load an already existing database, we have to use the load_store method of the StoreManager class.
assuming you've set a consisntent environment variable, the code snippet below shows how one can load a database.
```python
from kdblite import Table,StoreManager
sm = StoreManager()
s = sm.get_store("students")
table = Table()
table.initialize(s.tab_repr,s.kdbl_repr)
```
The Store class has attributes tab_repr and kdbl_repr which represent parameters and the table for the database respectively.
the tab_repr and kdbl_repr strings are passed to the table's initialize method in order to load the table.

One can also add checkers and modifiers to the table. A checker is a callback function added directly to the table or during column lookup
which applies a constraint on column lookup. A checker can ensure that the return values from a column lookup returns only the desired results.
For example:
``` python
def only_even(column_item):
    if (column_item % 2) == 0:
        return column_item
    return None
```
Now you can either add the checker on column lookup by passing the callback as an argument or by adding the callback on the column directly.
Adding the callback on the column directly shall make it be called on every subsequent lookup of the column. If you only wish to call the callback
once, it's better to pass it as a function argument to the column lookup function.

```python
#either
table.add_checker("Age",only_even)

#or
table.get_column("Age",only_even)
```
The return value will be a list containing ages that are even numbers only.

Modifiers are also callback functions just like checkers. However, their use is to modify a value as it's being inserted into a table field.
```python
def multiply(value):
    return value * 2
    
table.add_modifier("Age",multiply)
index,row = table.new_row()
field = row.get_field("Age")
field.value = 20

#the actual value stored on the database will be 40
```
### Conclusion
KozesaDBLite is still under rigorous development and test, and it's not yet ready for production use.
We need help for the community to make this the best and most intuitive database framework to use, with a very low learning curve.
