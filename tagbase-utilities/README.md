# Tagbase server remote deployment 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/logos.png)

### Progress and Notes

### I: Clean eTUFF timeseries files

#### i: Cleaning data & handling argosLC string variables
The timeseries data files we are working with often have 'argosLC' values. These values are important because they can be associated with empirically derived error parameters to interperet positional accuracy. There is no place in the tagbase schema at present to deal with these values, and this causes ingestion of eTUFF files with raw argosLC values to fail. Developers at OIIP are working to build functionality into the tagbase schema to accomodate this value and others like it, and we have built a work-around in the meantime. 

To demonstrate this workaround this repo mimics the directory structure used in development. The code currently assumes that you have in your working directory set up as follows: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/directory-initial.png)

In the working directory, raw eTUFF files should be placed in ./raw/ directory in either the ./profile/ or ./timeseries/ subdirectory depending on if they are positional files or depth & profile files. The script clean-timeseries-eTUFF.py can be run from the command line as is, and will do the following things: 

    * read all eTUFF files in the ./data/raw/timeseries/ directory
    * replace the string values for argosLC with an integer unique identifier 
    * store the argosLC string value and unique id in a metadata file called lc-log-info.csv
    * log the ingestion in a metadata file called ingest-log.csv 
    * move cleaned files into the ./ingested/timeseries/ directory
    * write all files ready to be sent to tagbase in the ./data/clean_timeseries/ directory
   
The script is run from the working directory with the standard execution command: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/run-cleaning-script.png)

After running the script, the directory structure will have changed to the following: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/directory-after-clean.png)

#### ii: Log files 
The script clean-timeseries-eTUFF.py will either generate or update two metadata files in the working directory. The first file is called ingest-log.csv, and contains the date the file was staged into the ingestion directory, the original file name, the number of records, a new unique identifier and the type of the file (timeseries or profile). The file will look as follows after running for the this repo: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/ingestlog.png)

The script also creates a second metadata file called lc-log-info.csv, which contains the original argosLC codes from each file and the new unique numeric id that is assigned to it so the files can be ingested. The script will check to see for each argos code if it is already in the reference file, and if it is not then it will generate a new id and update the file. This file will look as follows after the script is run in the directory: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/argos-log.png)


### II: Ingest cleaned files into tagbase and query the database

#### i: scp files from ./cleaned_timeseries or ./cleaned_profile directory to the remote server
The cleaned files are then all stored in the clean_timeseries directory, and can be sent with scp over to the remote server running the database. To send all cleaned files, you can run the scp command with * wildcards as shown here: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/scp-cmd.png)

Once the files are on the remote server, you can instantiate the database with docker in a screen on the remote machine (docker-compose build, docker-compose up). Then, using the curl syntaz proved by the Swagger API, and by generating a unique granule id for each file in the staging directory ./tagbase-server/data/timeseries/, you can build a set of curl commands to write the data to tagbase: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/curl-data.png)

The major to do item right now is to turn the process from scp --> ingestion into a set of bash scrtipts that are executable and can be run base on some trigger. This could be manually or setup through cronjobs once we have data coming in on a regular basis. This portion is done manually now, though automating it with bash is a simple next step. 

#### ii: Writing queries to access the newly ingested data
Once the curl commands are run, the data can be found on the sever and explored using the tagbase postgres interface though pgadmin. If you write a query to select all entries from the submissions table, you can see the two new submissions we just made at the bottom of the table: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/submissions-query.png)

Using the submission id, you can then query the data_position table to see the positional data loaded from the file: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/lat-lon-query.png)

Finally, the numeric unique id numbers that we used to replace the argos values have successfully been loaded into the database, and can be viewed by writing a query with the sumission id on the proc_observations table: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/argos-values-query.png)

This process is complete for the timeseries data, and the next steps are to 1) automate data transfer and ingestion with bash utilities, 2) write a program to clean, log, and write the profile eTUFF files. 

