# Analytical regionalization & land use classification:
## Using social media data to map land use in homogenous urban centers

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/yale-datadriven-logo.png)

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

Self Organizing Maps is an artificial neural network with a variety of applications. Among these are clustering / dimensionality reduction and space approximation. This analysis does not rely on SOM for dimensionality reduction, and has to this point only used the algorithm to do a spatial approximation for the two-dimensional set of latitude and longitude coordinates for the check-ins. Moving forward we hope to explore the performance of SOM for unsupervised clustering of the full 3 dimensional dataset (LAT, LON, TIMESTAMP).  

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/SOM-cluster-centroids-scatter.png)

#### Optimizing SOM initialization: 

There are a number of parameters that have to be specified for SOM initialization. The most critical parameters for this analysis are the learning radius for nuerons, the initializing grid size N [p,q] and the distance metric used to evaluate nueron distance. This iteration of the anaysis uses a learning radius of 2 and haversine distance formula as the distance metric. Frias-Martinez optimized the grid size by minimizing the Davies Bouldin index for different initializing grid sizes. This analysis follows the same process, and we ultimately selected a 9 * 11 = [p,q]. Plotting the DBI index against the total grid size N, and over the ratio of the sides p/q, illustrates some interesting properties about the SOM algorithm. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/combined-dbi-plots.png)

The lefthand graph shows the DBI index on Y axis and grid size on the X axis, and suggests that as the grid size N increases the DBI performance gets better. This is consistent with the space aproximation functionality of the SOM, and as the number of nuerons increse the coverage of the underlying data improves. The righthand graph was made to illustrate the periodicity of the lefthand graph, and suggests that the periodicity of the graph relates the the similarity between the ratio of the sides of the initializing grid, and the ratio of the sides of the underlying region of interest. In this case both are maximized simultaneously with N = 99, [p,q] = [9, 11]. 

#### Tessellation (Voronoi Polygons): 

The centroids output by the SOM were then used to perform tessellation over the scene and generate polygons. This analysis used the scipy voronoi tessellation module, and has not yet explored other algorithms. The voronoi tessellation algorithm generates some polygons that are not finite, and those were ultimately excluded from the subsequent analysis. This is a hacky solution, because the polygons on the perimeter could be cropped to the ROI polygon, this will be solved in version 2. The process produces the following segmentation of the ROI: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/finite-polygons-centroids-scatter-snip.png)

#### Classifying Activity Vectors for Polygons: 

The polygons generated by tessellation are then used to group the Sina Weibo check-ins and build aggregate activity vectors to use for classification. Frias-Martinez (2012) aggregated the data by splitting each day into 20 minute segments, and counting the number of points in each polygon during each segment. This data is then split by weekend and weekday, and the average vector for weekday activity and weekend activity is calculated. These vectors are then concatenated and normalized as a proportion of total average activity (this produces a n-polygon by 144 component matrix). In this analysis we employed the same method but used 60 minute segments instead of 20. Further, we also tried aggregating by day of the week, given the arbitrariness of the weekend / weekday split (ex. Friday night). 

One major obstacle to this analysis is the amount of data that we have to look at. There are just 152k records for the entire year, so there are cells of the average frequency matrix described above that are 0. This means that in some polygons, there were no check-ins during that 60 minute time period at any point during the full year (binary coverage matrix pictured below for both iterations). 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/coverage-matrix-combined.png)

The second plot, which is from the version of the analysis that follows the weekend / weekday procedure used in Frias-Martinez (2012), seems intuitively strange given that you would expect more activity in the weekend than in the week. This plot doesn’t necessarily speak to the density of the activity in the cells, but may be because in areas of similar weekend / weekday activity, there are too few weekend observations to produce any records. The histograms of weekend and weeday activity are more instructive, and illustrate this point. The graphs are pictured below with the weekend historgam on the left and weekday histogram on the right. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/weekend-weekday-histogram.png)

#### PCA and Kmeans Classification of Activity Vectors: 

To classify the vectors we used 2 dimentional PCA and kmeans as a baseline process. Frias-Martinez use spectral clustering, which will be implemented going forward to compare. We began with k=3 clusters for this initial run. The polygons plot with cluster assignment is pictured below for both sets of vectors (48 hour vector weekend (left) / weekday; 168 hour 7-day (right)): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/combined-pca-kmeans-vector-plots.png)

The spectral graphs corresponding to the kmeans classification are picture below. The next step is to produce / evaluate a set of annotations from the discrete labeled points. Once this has been reviewed and determined to be a sound method to groundtruth the model, we will explore predictive accuracy and add qualitative labels to the spectral clusters. 

	48 dim spectral graph weekend / weekday aggregation
![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/48-dim-spectral-graph-3k-red.png)
 
	168 dim spectral graph 7-day aggregation
![alt text](https://github.com/emmettFC/selected-projects/blob/master/regionalization/assets/168-dim-spectral-graph-3k-snip.png)


#### Building Annotations & Evaluating Model Performance: 
