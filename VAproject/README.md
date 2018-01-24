# VAProject: 
## Working to build a consolidated national sex offender database from state-level registries

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/jan24-states-progress-map.png)

### Project Overview: 
I am working as an independent contractor & leading the data science component to a project run by the School of Social Policy and Practice at the University of Pennsylvania. The project seeks to build a consolidated national database of all registered sex offenders in order to perform demographic analysis and records linkage. The individual state level registires have inconsistent formats, and the national aggregator run by the DOJ is essentially just an index of the state level sites. Therefore, the development of a set of scraping utilities is required in order to work with the data in any comprehensive way. NB: I will not be disclosing full code for this project given that priority access to this database is valuable to the sponsoring organizations. That said, this repository will host code that contributes to the development of a generic solution (in the form of a module) for interating with municipal govenment sites. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/project-partners-git.png)

### Methodolody & Contribution: 
Scraping proceedures will be written in python and R. Typically it is preferable to use post/get requests to make calls and ingest data, though finding the correct parameters/headers can be painful with municipal govenment sites like these. With captcha requirements, javascript interfaces and poorly maintained html, the use of selenium is a helpful workaround. To this point the variable structure of the sites prevents the development of a class or module to make the process generic, though we beleive that it is possible to abstract the browser automation process (via selenium) for scraping these sites in such a way that a standard set of variables can be determined, and bespoke code will not be required.

### Summary of Data & Comparison to Previous Study: 

This study will replicate the methodology section of an existing paper that sought to do a demographic analysis of individuals on public sex offender registries (citation below). From a methods standpoint, the contibution of our project will be towards the generalization of methods for gathering SOF data from the public registries.  

```
Who are the people in your neighborhood? A descriptive analysis of individuals on publix sex offender registries.
Alissa Ackerman, Andrew Harris, Jill Levenson, Kristen Zgoba
International Journal of Law and Psychiatry 34 (2011) 149-159
```

While the analytical goals of this project are different from those of the existing paper, the database we seek to build is nearly identical. This is helpful in that it provides an explicit point of comparison to sanity check the results from each individual scraping process. The two high-level aggregate summaires provided in the existing paper will provide the reference point going forward (pictured below)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/summary-tables-study-git.png)


