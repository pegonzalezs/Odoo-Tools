# Performance Script -Work in progress-
## Command-Line Arguments
### --help, -h
Tool help

### -m, --multithread
Each user operations will be executed in a different thread, do not hesitate to do a top in the odoo server and analyse results with or without multithreading

### -s, --save
The result of the execution will be storaged in history/output_<time_date> 

### -i, --inputfile,
Provide a CSV file with login, password in 1st, 2nd column of the users involved in the performance test 

## Output file
Measure time execution per user

## TODO
* Customize and extend the functionality you would like to measure
* Do output (Excel with performance measure from last execution in percentage and in color red/green)
