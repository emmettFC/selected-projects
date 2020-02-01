# Tagbase server deployment 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/logos.png)

### Progress and Notes

### I: Ingest timeseries eTUFF files

#### ia: Cleaning data & handling argosLC string variables
The timeseries data files we are working with often have 'argosLC' values. These values are important because they can be associated with empirically derived error parameters to interperet positional accuracy. There is no place in the tagbase schema at present to deal with these values, and this causes ingestion of eTUFF files with raw argosLC values to fail. While developers at OIIP are working to build functionality into the tagbase schema to accomodate this value and others like it, we have built a work-around in the meantime. 

To demonstrate this workaround this repo mimics the directory structure used in this process. The code currently assumes that you have in your working directory set up as follows: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tagbase-utilities/assets/directory-initial.png)



