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

## Use case
### a) Analyse multithreading execution

Lets set up a simple configuration file with many users. Per each user it will be executed one search operation of
two hundred records and one read operation over those two hundred record of the field 'name'.


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
 
[users]
1116=password1
1395=password2
1190=password3
1191=password4
1188=password5
1183=password6
1197=password7
.............
```

Then execute the analyser with the option to save the result in the history

```shell
./performance --save
```

The result is:
```
USER LOGIN   CURRENT TIME(s)
07-465-164 =>1.07
1116 =>4.47
1142 =>1.31
1143 =>1.33
1146 =>1.39
1147 =>1.30
1149 =>1.40
1150 =>1.32
1151 =>1.30
1153 =>1.37
1183 =>1.36
1188 =>1.34
1190 =>1.34
1191 =>1.30
1197 =>1.26
1230 =>1.36
1326 =>1.27
1395 =>4.15
1406 =>1.30
1439 =>1.54
1453 =>1.38
1528 =>1.35
1558 =>1.39
99-706-822 =>1.00
TOTAL =>41.29
```

First interesting thing looking at the results is that users 1116, 1395 execution take much more time than the rest of users doing exactly the same operations (to search and read on res_partner). 
So it is obvious that was found a weak point to be improved in our Odoo instance

As it's not the goal of the present use case, lets continue focusing in the multithread execution option  

So the analyser must be runned with the -m option and comparing it with the previous result already saved in the history folder
```shell
./performance.py -m --compare-with history/output_20042017-220326.xlsx
``` 

| USER LOGIN 	| PREVIOUS TIME(s) 	| CURRENT TIME(s) 	| IMPROVEMENT(%) 	|
|------------	|------------------	|-----------------	|----------------	|
| 07-465-164 	| 1.07 	| 4.12 	| 285.05% 	|
| 1116 	| 4.47 	| 6.78 	| 51.68% 	|
| 1142 	| 1.31 	| 4.53 	| 245.80% 	|
| 1143 	| 1.33 	| 1.98 	| 48.87% 	|
| 1146 	| 1.39 	| 1.66 	| 19.42% 	|
| 1147 	| 1.3 	| 1.91 	| 46.92% 	|
| 1149 	| 1.4 	| 1.71 	| 22.14% 	|
| 1150 	| 1.32 	| 4.82 	| 265.15% 	|
| 1151 	| 1.3 	| 4.60 	| 253.85% 	|
| 1153 	| 1.37 	| 4.59 	| 235.04% 	|
| 1183 	| 1.36 	| 4.65 	| 241.91% 	|
| 1188 	| 1.34 	| 4.71 	| 251.49% 	|
| 1190 	| 1.34 	| 1.66 	| 23.88% 	|
| 1191 	| 1.3 	| 4.78 	| 267.69% 	|
| 1197 	| 1.26 	| 4.73 	| 275.40% 	|
| 1230 	| 1.36 	| 4.50 	| 230.88% 	|
| 1326 	| 1.27 	| 4.63 	| 264.57% 	|
| 1395 	| 4.15 	| 7.31 	| 76.14% 	|
| 1406 	| 1.3 	| 4.50 	| 246.15% 	|
| 1439 	| 1.54 	| 4.61 	| 199.35% 	|
| 1453 	| 1.38 	| 4.77 	| 245.65% 	|
| 1528 	| 1.35 	| 4.66 	| 245.19% 	|
| 1558 	| 1.39 	| 4.68 	| 236.69% 	|
| 99-706-822 	| 1 	| 4.18 	| 318.00% 	|
| TOTAL 	| 41.29 	| 7.55 	| -81.71% 	|


The conclusions are:
* All users expend more time. Not true!. The execution threads runs the code line that measure the time later.
* With the same amount of users and the same operation the multithread option makes Odoo server run in parallel the operations
* As you see, this execution took IN TOTAL almost 6 times less han the previous one with the same amount of users and the same operations



