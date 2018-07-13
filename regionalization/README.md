# Analytical regionalization & land use classification:
## Using social media data to map land use in homogenous urban centers


Analytical regionalization & land use classification: 
Using social media data to map land use in homogenous urban centers


Analysis of remote sensing data, specifically multi-spectral satellite imagery, can be used to generate high-resolution land cover classifications. To an extent, these land cover classifications can be used to approximate land use, especially when the underlying scene has a large degree of heterogeneity. Alternatively, for scenes where land cover is uniform, it is more difficult to approximate land use through the analysis of remote sensing data. This problem is exemplified by the analysis of land use in high-density urban centers, where the uniformity of land cover does not represent the diversity of land use within the city. 
	
Social media check-in data can be used to classify land use over scenes with homogenous land cover (Frias Martinez 2015). Even in the absence of semantic analysis, geo-tagged social media check-ins provide insight into where people are within the city at a given point in time. This paper seeks to explore the viability of social media check-ins as the input for land use classification models. These models take discrete geo-point data (Sina Weibo check-ins) as their input, and output a set of polygons (sub-regions), each associated with a given land use. This process is twofold: 
1) Build polygons from discrete geo-points (analytical regionalization)
	2) Classify polygons by aggregate activity vectors 
Both hemispheres of this analysis are generic, and can be approached in a variety of ways. It is the hope of this analysis to compare the performance of different methodological strategies, and ultimately optimize a land use classification model for Beijing. 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/jan24-states-progress-map.png)

### Project Overview: 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/project-partners-git.png)

### Methodolody & Contribution: 




### Summary of Data & Comparison to Previous Study: 

This study will replicate the methodology section of an existing paper that sought to do a demographic analysis of individuals on public sex offender registries (citation below). From a methods standpoint, the contibution of our project will be towards the generalization of methods for gathering SOF data from the public registries.  

```
Who are the people in your neighborhood? A descriptive analysis of individuals on publix sex offender registries.
Alissa Ackerman, Andrew Harris, Jill Levenson, Kristen Zgoba
International Journal of Law and Psychiatry 34 (2011) 149-159
```

While the analytical goals of this project are different from those of the existing paper, the database we seek to build is nearly identical. This is helpful in that it provides an explicit point of comparison to sanity check the results from each individual scraping process. The two high-level aggregate summaires provided in the existing paper will provide the reference point going forward (pictured below)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/summary-tables-study-git.png)


