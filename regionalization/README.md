# Analytical regionalization & land use classification:
## Using social media data to map land use in homogenous urban centers

### Introduction

Analysis of remote sensing data, specifically multi-spectral satellite imagery, can be used to generate high-resolution land cover classifications. To an extent, these land cover classifications can be used to approximate land use, especially when the underlying scene has a large degree of heterogeneity. Alternatively, for scenes where land cover is uniform, it is more difficult to approximate land use through the analysis of remote sensing data. This problem is exemplified by the analysis of land use in high-density urban centers, where the uniformity of land cover does not represent the diversity of land use within the city. 

Social media check-in data can be used to classify land use over scenes with homogenous land cover (Frias Martinez 2015). Even in the absence of semantic analysis, geo-tagged social media check-ins provide insight into where people are within the city at a given point in time. This repository contains code and results from an effort to perform land use classification using social media geo-point data. The intention is to develop a model that takes discrete point data and outputs polygons which can be classified by thier land use. There are three major components to this analysis: 

#### 1) Build polygons from discrete geo-points (analytical regionalization)
	
#### 2) Classify polygons by aggregate activity vectors 

#### 3) Develop reliable annotations to evaluate model performance 

The purpose of this repository is to compare the performance of different methodological strategies, and ultimately optimize a land use classification model for Beijing. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/weibo-scatter.png)

### Replication of Frias Martinez (2012):

#### Data Preparation: 

The data used for this analysis comprises 1.7 million Sina Weibo check-in points with timestamps and geo-tags (pictured below in red). These data were collected over the full 2012 calendar year (01-01-2012 → 12-31-2012). The annotations for the underlying region of interest are built from specific landmarks pulled from the Google Earth API (pictured below in blue). The Sina Weibo point data were restricted to the annotated region in order to build polygons that would describe the region in adequate granularity (ROI polygon pictured below).  After restricting the input data to the region of interest, 152K of the 1.7 million data points remain for clustering analysis.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/boundary-labels-weibos-snip.png)

#### Clustering & Review of Algorithms:

Clustering geospatial data is a well-studied problem, and there are several algorithms that have been used with good performance. This paper will explore 4 different clustering algorithms: 

	1)	K-Means (Haversine distance) (Done, not run through end to end)
	2)	DBSCAN / GDBSCAN (Done, not run through end to end) 
	3)	OPTICS (Not done) 
	4)	SOM / Kohonen Algorithm (Done and documented)





### Summary of Data & Comparison to Previous Study: 

This study will replicate the methodology section of an existing paper that sought to do a demographic analysis of individuals on public sex offender registries (citation below). From a methods standpoint, the contibution of our project will be towards the generalization of methods for gathering SOF data from the public registries.  

```
Who are the people in your neighborhood? A descriptive analysis of individuals on publix sex offender registries.
Alissa Ackerman, Andrew Harris, Jill Levenson, Kristen Zgoba
International Journal of Law and Psychiatry 34 (2011) 149-159
```

While the analytical goals of this project are different from those of the existing paper, the database we seek to build is nearly identical. This is helpful in that it provides an explicit point of comparison to sanity check the results from each individual scraping process. The two high-level aggregate summaires provided in the existing paper will provide the reference point going forward (pictured below)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/VAproject/admin/assets/summary-tables-study-git.png)


