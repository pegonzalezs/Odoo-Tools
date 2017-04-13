# Performance Analyser
This tool allows you to measure different scopes of your Odoo environment
* Measure how efficient is your Odoo infrastructure (with Multithreading)
* Measure how efficient can be a certain Role/User
* Measure how efficient can be a certain algorithm or portion of code  
 
## Dependencies
* pip install xlsxwriter (http://xlsxwriter.readthedocs.io/)
* pip install erppeek (http://erppeek.readthedocs.io/en/latest/api.html)
 
## Command-Line Arguments
### -h, --help, 
Tool help

### -m, --multithread
Each user operations will be executed in a different thread, do not hesitate to do a top in the odoo server and analyse results with or without multithreading

### -s, --save
The result of the execution will be saved in history/output_<time_date>.xlsx 

### -c, --config
configuration file 

## Output file
Measure time execution per user

## Configuration File

* Define the connection with your server 
* Include the login/password of the users that will run all the operations
* Configure your operations inside the config file
* It allows to quickly create functions that will call erppeek
* The input of one operation can be the result of a previous one
* Write your custom function in the python code and reference it in the configuration file. It will be directly executed without updating the motor of the script
It allows to create customized operations

Example of config file:
```shell
[connection]
host=http://my.odoo.com:8069
db=my_database
 
[operation1]
description = "Read two hundred Partners"
groups = Employee
model = res.partner
method = search
args = [[('active', '=', True)], 0 , 200]
 
[operation2]
description = "Read field name in the records given by operation1"
groups = Employee
model = res.partner
method = read
args = [operation1, ['name']]
 
[operation3]
description = "My super long function"
groups = Employee
model = self
method = my_super_long_function
args = []
 
[users]
admin=kumIgV
user_demo=32312
```

## TODO
* Do compare-with functionality (Excel with performance measure from last execution in percentage and in color red/green)
