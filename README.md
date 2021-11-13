![kozesalite logo](/docs/dblite2.png)
# kozesaDBLite
### Introduction
KozesaDBLite is a light weight table based database framework developed in Python.
The database was originally developed to power the Kozesa BMS(Business Management System)
software suite, a collection of six frequently used business management software which
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
