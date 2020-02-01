# Tagbase server remote deployment 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/logos.png)

### Progress and Notes

### I: Clean eTUFF timeseries files

#### i: Cleaning data & handling argosLC string variables
The timeseries data files we are working with often have 'argosLC' values. These values are important because they can be associated with empirically derived error parameters to interperet positional accuracy. There is no place in the tagbase schema at present to deal with these values, and this causes ingestion of eTUFF files with raw argosLC values to fail. Developers at OIIP are working to build functionality into the tagbase schema to accomodate this value and others like it, and we have built a work-around in the meantime. 

To demonstrate this workaround this repo mimics the directory structure used in development. The code currently assumes that you have in your working directory set up as follows: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/directory-initial.png)

In the working directory, raw eTUFF files should be placed in ./raw/ directory in either the ./profile/ or ./timeseries/ subdirectory depending on if they are positional files or depth & profile files. The script clean-timeseries-eTUFF.py can be run from the command line as is, and will do the following things: 

    * read and clean all eTUFF files in the ./data/raw/timeseries/ directory
    * replace the string values for argosLC with an integer unique identifier 
    * store the argosLC string value and unique id in a metadata file called lc-log-info.csv
    * if the file doesnt exist it will build it, and if it does exists it will update it with any not yet seen argosLC 
    * log the ingestion in a metadata file called ingest-log.csv with number of records, data, unique id and original file name
    * move cleaned files into the ./ingested/timeseries/ directory
    * write all files ready to be sent to tagbase in the ./data/clean_timeseries/ directory
   
The script is run from the working directory with the standard execution command: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/run-cleaning-script.png)

After running the script, the directory structure will have changed to the following: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/directory-after-clean.png)

### II: Ingest cleaned files into tagbase and query the database

#### i: 

    

