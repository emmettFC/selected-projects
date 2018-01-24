# VAProject: 
## Working to build a consolidated national sex offender database from state-level registries

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/jan24-states-progress-map.png)

### Project Overview: 
I am working as an independent contractor & leading the data science component to a project involving the National Center for Homelessness Among Veterans (VA) and the University of Pennsylvania. The project seeks to build a consolidated national database of all registered sex offenders in order to perform demographic analysis and records linkage. The individual state level registires have inconsistent formats, and the national aggregator run by the DOJ is essentially just an index of the state level sites. Therefore, the development of a set of scraping utilities is required in order to work with the data in any comprehensive way. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/project-partners-git.png)

### Methodolody & Contribution: 
Scraping proceedures will be written in python and R. Typically it is preferable to use post/get requests to make calls and ingest data, though finding the correct parameters/headers can be painful with municipal govenment sites like these. With captcha requirements, javascript interfaces and poorly maintained html, the use of selenium is a helpful workaround. To this point the variable structure of the sites prevents the development of a class or module to make the process generic, though it is possible that a creative generallization through the use of selenium is possible. 

### Summary of Data & Comparison to Previous Study: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/summary-tables-study-git.png)


