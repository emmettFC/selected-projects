![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets/yale-datadriven-logo.png)

# Analytical regionalization & land use classification:
## Using social media and remote sensing data to map land use in homogenous urban centers

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-8-nl-poly.png)

### Introduction
Analysis of remote sensing data, specifically multi-spectral satellite imagery, can be used to generate high-resolution land cover classifications. To an extent, these land cover classifications can be used to approximate land use, especially when the underlying scene has a large degree of heterogeneity. Alternatively, for scenes where land cover is uniform, it is more difficult to approximate land use through the analysis of remote sensing data. This problem is exemplified by the analysis of land use in high-density urban centers, where the uniformity of land cover does not represent the diversity of land use within the city. 

Social media check-in data can be used to classify land use over scenes with homogenous land cover (Frias Martinez 2015). Even in the absence of semantic analysis, geo-tagged social media check-ins provide insight into where people are within the city at a given point in time. This repository contains code and results from an effort to perform land use classification using social media geo-point data. The intention is to develop a model that takes discrete point data and outputs polygons which can be classified by thier land use. Classification is then performed based on a combinaton of features from 1) the social media geopoints 2) remote sensing indices 3) baidu and google map property labels. There are three major components to this analysis: 

#### 1) Build polygons from discrete geo-points (analytical regionalization)
	
#### 2) Classify polygons by aggregate activity vectors, remote sensing layers and property/business labels from baidu 

#### 3) Develop reliable annotations to evaluate model performance (beijing city labs data on land use)
The purpose of this repository is to compare the performance of different methodological strategies, and ultimately optimize a land use classification model for Beijing. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-2-roi-labels-sm-scatter.png)

### Replication of Frias Martinez (2012):

#### Data preparation: 
The data used for this analysis comprises 1.7 million Sina Weibo check-in points with timestamps and geo-tags (pictured above in red). These data were collected over the full 2012 calendar year (01-01-2012 → 12-31-2012). Property data for the underlying region of interest are a set of specific landmarks pulled from the Google Earth API (pictured above in blue). The Sina Weibo point data were restricted to the annotated region in order to build polygons that would describe the region in adequate granularity (ROI polygon pictured above).  After restricting the input data to the region of interest, 152K of the 1.7 million data points remain for clustering analysis.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-1-sm-data.png)

#### Building subregional polygons for classification
The first step in a land use classification process is builing polygons over the study region that can be used to aggregate input data and classify land use types. This has been done in a variety of ways in the liteature, with one of the most common strategies being the use of road networks and other infrastructure boundaries to delineate regions. The purpose of our analysis is to look at changing land use parcels over time, and use this change as a way to forecast the pace and direction of urban expansion. For this reason, it is desireable to use a method that generates non-physical and flexible regions (ie. not delineated by infrastructure) so we can observe fluctuation in the boundaries of land use parcels. Frias-Martinez (2015) use spatial clustering of social media data to generate centroids that can then be used as inputs for tesselation (or triangulation or convex hull approximation). Our analysis follows the methods outlined in Frias-Martinez, and also seeks to asses the comparative performance of other classification algorithms and spatial clustering techniques. 

#### Clustering & review of algorithms:
Clustering geospatial data is a well-studied problem, and there are several algorithms that have been used with good performance. Our analysis will ultimately explore 4 different clustering algorithms: 

	1)	K-Means (Haversine distance) (Not complete)
	2)	DBSCAN / GDBSCAN (Not complete) 
	3)	OPTICS (Not complete) 
	4)	SOM / Kohonen Algorithm (Done and documented)

Self Organizing Maps is an artificial neural network with a variety of applications. Among these are clustering / dimensionality reduction and space approximation. This analysis does not rely on SOM for dimensionality reduction, and has to this point only used the algorithm to do a spatial approximation for the two-dimensional set of latitude and longitude coordinates for the check-ins. The SOM ann ultimately does a pretty good job of clustering the social media data.  

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-3-som-centroids.png)

#### Optimizing SOM initialization: 
There are a number of hyperparameters that have to be specified for SOM initialization. The most critical parameters for this analysis are the learning radius for nuerons, the initializing grid size N [p,q] and the distance metric used to evaluate nueron distance. This iteration of the anaysis uses a learning radius of 2 and haversine distance formula as the distance metric. Frias-Martinez optimized the grid size by minimizing the Davies Bouldin index for different initializing grid sizes. This analysis follows the same process, and we ultimately selected a 8 * 22 = [p,q]. Plotting the DBI index against the total grid size N, and over the ratio of the sides p/q, illustrates some interesting properties about the SOM algorithm. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/combined-dbi-plots.png)

The lefthand graph shows the DBI index on Y axis and grid size on the X axis, and suggests that as the grid size N increases the DBI performance gets better. This is consistent with the space aproximation functionality of the SOM, and as the number of nuerons increse the coverage of the underlying data improves. The righthand graph was made to illustrate the periodicity of the lefthand graph, and suggests that the periodicity of the graph relates the the similarity between the ratio of the sides of the initializing grid, and the ratio of the sides of the underlying region of interest. In this case both are maximized simultaneously with N = 396, [p,q] = [18, 22]. The insight here is clear, and suggests somewhat intuitively that in terms of DBI clustering performance, SOM initializations improve acording to 1) the number of nuerons and 2) the similarity of the initializing rectangle and the shape of the region of interest.

#### Tessellation (Voronoi Polygons): 
The centroids output by the SOM were then used to perform tessellation over the scene and generate polygons. This analysis used the scipy voronoi tessellation module, and has not yet explored other algorithms. The voronoi tessellation algorithm generates some polygons that are not finite, and those were ultimately excluded from the subsequent analysis. This is a sub-optimal solution, because the polygons on the perimeter could be cropped to the ROI polygon, this will be solved in version 2. The process produces the following segmentation of the ROI: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-4-tesselation.png)

#### Evaluating the stability of SOM spatial approximation methods
The SOM algorithm used to build the polygons pictured above is trained for 100 epochs, and shows relatively good convergence. Like all ANNs, convergence is defined in terms of a cost function minimization through some stochastic gradient descent process. Stability then refers to the minimal value of this function, and not the actual geometric output of centroids. If there were no meaningful clusters in the data, a stable solution in terms of minimal cost would not nessecarily correspond to a stable set of output clusters. Frias-Martinez (2015) do not address this issue of geometric stability in thier analysis. Given that we are interested in producing meaningful and stable regions, we consider SOM performance in terms of a normalized mutual information score through the NMI scipy implementation. Consider the following two sets of centroids ( green and red) produced by two SOM initializations with identical hyperparamters and nueron intializations:

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-13-nmi-cents-only.png)

While it is clear that there is some good correspondance between the two sets of clusters--which may improve given more training steps--there is definitely some difference. Ultimately though, the important aspect of this difference is the different segmentations of the region of interest that result from tesselation. This is not clear just from the centroid locations, and can be better observed when the polygons are drawn over the ROI: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-12-nmi-som-cent.png)

These sets of polygons are actually very simmilar, which is a qualitative endorsement of the SOM ann approach. To quantify thier similarity, we then observe the normalized mutual information score of the pairwise assigment of social media data to one or another subregion (polygon). The score is quite good, and shows the method has some desireable stability: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-14-nmi-score.png)

There were some cardinality issues in joining the two sets of social media data that we have not yet had time to debug, though with a larger proportion of coverge we have seen the NMI scores get as high as 90%. 

#### Comparison with rectangular grid for baseline performance 
An alternative method for creating subregions is just to overlay a rectangular grid over the study region. Frias-Martinez (2015) do not discuss this alternative, which we feel is a nessecary aspect of evaluating the regionalization methodology. For this reason we have done a paralell analysis that uses a regular grid for classification. The most straighforward approach to this follows from the initializing grid of nuerons from the SOM clustering. We use the same 18 height by 22 width rectangular orientation of corner points, which generates the same number of polygons with the same average area as the irregular set of polygons from tesselation. The figure below shows the grid on its own over the region of interest.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-4-rectangular-grid.png)

It is helpful to see a direct comparison of the grid and tesselation, which gives a good demonstration of the relative size of polygons produced by the two methods. The figure below shows the rectangular grid in red, and the tesselation in black. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-5-grid-over-tess.png)

#### Intersecting polygons and remote sensing inputs 
Frias-Martinez use only the social media data to do both regionalization and classification, though other studies seeking to do land use classification use a host of other inputs such as remote sensing layers, semantic data and open data on infrastructure networks. Our analysis will include several remote sensing layers and property data from baidu and google maps. Some studies which report very high classification accuracy have used land cover classifications of remote sensing data to separate water, undeveloped land parcels, farmland and grass parks from adjacent regions. While this is a reasonable approach in one sense, if this separation is then interpreted as the endpoint of a classification model with levels such as 1) water, 2) recreation, 3) comercial, 4) undeveloped land, 5) grass park, then that model is a hybrid land cover land use classifier with an exaggerated predictive performance. For example, 'water' is not a land use, and it is relatively trivial to identify and separate water parcels from a larger region. To count each such exclusion as a correct classification then overstates the ability of the model to make the more subtle distinctions between commercial and residential parcels, for example, which is the purpose of a land use classification. In our analysis, we are going to include remote sensing layers as features in our analysis, while keeping them within the larger land use parcels. We used several remote sensing layers in the analysis to this point (pictured below for the study region and different sets of polygons): 

1) normalized difference built-up index (30m landsat 2010); 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-6-ndbi-poly.png)

2) percentage of impervious surface (30m landsat 2010 via http://sedac.ciesin.columbia.edu/ );

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-7-imp-poly.png)

3) saturation corrected annual mean nightlights (30m VIIRS 2013);

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-8-nl-poly.png)

#### Classifying Activity Vectors for Polygons: 
The polygons generated by tessellation are then used to group the Sina Weibo check-ins and build aggregate activity vectors to use for classification. Frias-Martinez (2012) aggregated the data by splitting each day into 20 minute segments, and counting the number of points in each polygon during each segment. This data is then split by weekend and weekday, and the average vector for weekday activity and weekend activity is calculated. These vectors are then concatenated and normalized as a proportion of total average activity (this produces a n-polygon by 144 component matrix). In this analysis we employed the same method but used 60 minute segments instead of 20. Further, we also tried aggregating by day of the week, given the arbitrariness of the weekend / weekday split (ex. Friday night). 

One major obstacle to this analysis is the amount of data that we have to look at. There are just 152k records for the entire year, so there are cells of the average frequency matrix described above that are 0. This means that in some polygons, there were no check-ins during that 60 minute time period at any point during the full year (binary coverage matrix pictured below for both iterations). 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/coverage-matrix-combined.png)

#### PCA and Kmeans Classification of Activity Vectors: 
To classify the vectors we used 2 dimentional PCA and kmeans as a baseline process. Frias-Martinez also use kmeans, and choose optimal k values on the basis of silouhette scores. We followed the same process in this analysis, and determined to use k=5 clusters for this initial run. The two plots below show a comparison of kmeans and principal components for the two different sets of polygons (tesselation left; grid right). Obviously the performance of this model leaves something to be desired. An explicit quantification of the difference between these two classification runs is forthcoming.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-9-cluster-polygons.png)

A major challenge to this process at the moment is the absense of any ground truth labels that can be used to evaluate the model performance. We have started to incorporate some land use approximation data from Beijing city labs, though this has not yet been incorporated into the analysis. While qualitative description of the classification levels has not yet been done, we can look at a quantitative comparision of the raw inputs based on the average distribution of values for each level in the respective classifications. 
The grid below shows the spectral graph of social media activity (left), a histogram of night lights layer pixels (center) and a color histogram of impervious surface pixels (right) for the tesselation. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-10-spectral-hist-tess.png)

There isnt yet any one to one comparison that can be made between the levels of the two classifications, it is still illustrative to look at the same aggregation of values for the analysis of the gridded region. The same values as depicted in the above figure are shown below for the regular grid classification. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/NASA_grant_analysis/assets_README/asset-11-spectral-hist-grid.png)


