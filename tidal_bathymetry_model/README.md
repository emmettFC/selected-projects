# Tidal bathymetry model & review of applied methods 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/bathy_12.png)

 ## Part I: Review of applied methods for WV2 images of South Water Cay Marine Preserve, Belize 

### Introduction 

Methods for bathymetric modeling of oceanic and fluvial sites is a well studied probelm with an extensive literature. That said, with the energence of UAV technology and improvements in satelite remote sensing imagery, this is an area of research that is fertile for the development of new methods from computer science and specifically the use of deep networks. The intent of this project was to leverage low cost UAV imagery, with flights at regular intervals through the tidal cycle, to try and train a model to do high resolution bathymetric modeling of a coastal tidal inlet in the long island sound. Ultimately, weather and the slow pace of feild work trial and error prevented this experiment from being completed at this time. This repositiory will therefore have two components: 1) breif review of trial application of known bathymetric methods to a set of WV2 imagery covering the South Cay Marine Preserve in Belze, and 2) a discussion of the experimental design and initial feild experiments, the proposed model, and preliminary analysis from the first pass at UAV bathymetric modeling of a the intended coastal scene on the long island sound. 

### The South Cay Marine Preserve, Belize

I worked with a doctoral student at UCSB on a project seeking to build a high resolution bathymetric model of the South Cay Marine Preserve in Belize. The purpose of this project was to use passive depth sounding data as labels to train the Stumpf and Lyzenga equations for bathymetric estimates. This is a meaningful effort because while LiDAR bathymetry is highly accurate, it is prohibitively expensive in many applications and a significant proportion of large and ecologically important coastal regions have yet to be mapped with this technology. If we could show that passive low cost depth sounding data could be used to effectively calibrate bathymetric models, then we could provide good topographic maps of these unmapped regions. The spectral data for the region of interest are a set of images from the WV2 digital globe satelite. The image below (left) shows the coverage of the WV2 imagery in red, and the minimal bounding box for the passive depth sounding labels in blue. The lefthand figure is a true color map from the WV2 image of the entire South Cay preserve, with the red showing the enitre region and the green boundary indicating a no-take zone: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/coverage-area-final.png)

The labeled region is quite small compared to the overall scene, though the real challenge comes from the sparse coverage of labeled points within the smaller region. These labels are passively generated from a hand held depth sounding device onboard a research ship studying the patch reef ecosystem of the South Cay. The coverage within the region is pictured below: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/centered_depth-label.png)

To generate bathymetric estimates based on these data, the depth sounding labels have to be intersected with the satellite raster data, such that the spectral values for each band at a given pixel are associated with the depth measurement at that point. Once the spectral data are corrected for atmospheric effects and sun glint, according to the specifications of the satelittle product, then the model coeficients can be calibrated using regression analysis. 

### Stumpf and Lyzenga bathymetric estimation models

In this iteration of the analysis we chose to employ two well known methods for using multispectral data to estimate bathymetric models: Stumpf (2003) and Lyzenga (1978). The general for of these equations is given below for Lyzenga (equation 1) and Stumpf (equation 2): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/stumpf-lyzenga-1.png)

Both of these techniques take advantage of the physical nature of light’s attenuation in the water column, namely that shorter wavelength bands attenuate faster than longer wavelength bands. This relationship is therefore correlated with depth. The first equation, the Lyzenga method, is more labor intesive from a annotation standpoint, given that it makes predictions based not only on the relationship bewtween band ratios and depth, but also the reflectance properties of different types of substrate (ex sand, seagrass, rock etc). In equation 1 above, Li is the TOA radiance value for band i, Lj is the TOA radiance value for band j, Ki/Kj are the light attenuation coeficients for band i and j respectively. 

We applied the Stumpf ratio method for bathymetric estimation according to Ehes & Rooney (2015). Before running the regressions to generate calibration coeficients, we had to convert the raw digital numbers to top of atomosphere spectral radiance values. In order to do this, you need the bandwidth and absolute clibaration factors from the imaging product speficiations for each band. The equation for the radiometric calibaration process is given below: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/toa-final.png)


After the digital numbers are converted to TOA values, you can apply the Stumpf method given in equation 2 above to generate coeficients and asses model performance. Linear models were trained and run for two subsets of the raw data: 

    1)	For all data <= 30 meters 
    2)	For all data <= 15 meters

For the 30-meter subset, we found an absolute mean difference between the predicted and actual values of 4.15 meters, with R2 of .5411 and RMSE of 3.655 meters. For the 15-meter subset, we found an absolute mean difference of .98 meters, with R2 of .5859 and RMSE of 1.91 meters. The graph below shows the OLS best-fit lines for each implementation: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/stumpf-regression-out.png)

The 15 meter subset performs pretty well considering the simplicity of the model applied. It is apparent that some nonlinear function of the data would perform better given the output shown above. Utlimately though, the model trained on the labeled subset of data can be extrapolated to the entire region for depth < 15 meters and a bathymetric model can be generated. The model produced by this analysis is pictured below: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/bathymetric-map.png)

## Part II: Proposal for UAV method of bathymatric modeling with sequential tidal correction

### Introduction

Models based on empirically calibrated coefficients outperform theoretical models in the literature (5). This is because of the fact that the underlying coastal and fluvial scenes have very different optical properties. There are four main sources of heterogeneity that prevent physical models from making generically accurate predictions: 

    1) surface turbulence and white water
    2) optical properties of the water column / variability in diffusive attenuation 
    3) surface reflectance and sun-glint
    4) substrate reflectance / albedo 

In this section I propose a method of developing empirical coefficients to correct physical depth estimates by flying consecutive flights with a UAV at regular 1 hour intervals through the course of a semidiurnal tidal cycle. Given appropriately short flight durations, I hypothesize that the known changes in depth corresponding to the high-low tidal cycle can be compared with estimated depths in order to empirically calibrate a physical model without in situ depth labels. This hypothesis is supported by the fact that known functional relationships exist between the associated physical variables and spectral radiance: spectral radiance is an exponential function of depth and diffuse attenuation, and a linear function of substrate reflectance (17)(18). First, I will describe the experimental design and some of the problems encountered when conduting feild experiments. Second, I will address two ways in which successive tidal depth estimates can be used to parameterize and enrich physical bathymetric models. Finally I will discuss the function of unsupervised image processing in the estimation of depth from multispectral data. This will include a discussion of algorithmic properties and a comparative discussion of performance based on application to data collected in the field. 

### Experimental design and preliminary feild work

In order to collect the data for the model of tidal depth correction described above, I flew a drone over the region of interest at regular 1-hour intervals through the course of a tidal cycle. Flights were made with a DJI phantom pro drone with an RGB-NIR camera, and controlled using flight plans set in the Ground Station Pro App. The flights were made at an elevation of 270 feet, with an overhead angle of 0 degrees. Images were taken continuously through the flight duration, as opposed to a hover and shoot flight, given the battery restrictions on the DJI Phantom Pro (flight plan and drone pictured below): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/flight-plan-and-drone.png)

My first attempt at doing this experiment demonstrated that ground control points (GCPs) were needed in order to provide tie points for the generation of an image mosaic. This was clear from the fact that photoscan was only able to incorporate a third of the raw images into the image mosaic, and nearly all images with no un-submerged points were excluded. In order to produce a set of image data with sufficient over-water coverage for depth analysis, I decided to make GCPs for the region that mimicked the calibration targets typically used in Drone Photogrammetry experiments. Given that the GCPs were intended to provide physical context for the SIFT algorithm, they needed to be 1) completely stationary and 2) sufficiently far from shore. The GCPs could not be attached to buoys because slack in the mooring line due to falling tide would cause them to move substantially in the direction of the current. Therefore it was necessary to build large wooden steaks that could be driven into the sand / peat and attach the GCPs to the top (pictured bellow): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/lyzenga-equations-ii.png)

Flights will be made with a DJI phantom pro drone with an RGB-NIR camera, and controlled using flight plans set in the Ground Station Pro App. 

### Discussion of the physical model & potential for a sequential tidal correction 

The majority of physical models are based on approximations of the solution to the radiative transfer equations in water (3). In general, these physical models are used to propose a generic formal expression that can be empirically parameterized though regression analysis given known depth points. The tidal correction I am proposing is meant to help calibrate physical depth estimates by comparing the relationship between known and predicted changes in depth through periods of tidal change. Depth estimates will be made at regular one-hour intervals through the tidal cycle, starting at dead-low tide (t=0) and ending at dead-high tide (t=6), for a total of seven flights. 


For each flight, depth is then estimated using the physical model proposed by Lyzenga (2006) (17). For different intervals in the tidal cycle (t=i, t=i+n), the difference between estimated depths [Xe(i+n) – Xe(i)] will be compared to known change in depth based on tidal fluctuation (Xa = avg(tidal current velocity(t=i, t=i+n)) * dt). These known and estimated depths can be used directly to derive coefficients for the physical model specified by Lyzenga (2006). 

Lyzenga (2006) propose a simplification of an approximate solution to the radiative transfer equation in water. They begin with the approximate solution: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/lyzenga-equations-ii.png)






## Appendix: Patch reef grazing halos 

### Introduction



