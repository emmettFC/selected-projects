# Simple physical plankton model
## Describing coastal plankton density with a one dimensional diffusion-sedimentation model with spatially variable diffusion coefficient and sinusoidal excitation

### Introduction

This aim of this project is to develop a model that describes the variability of plankton density in-phase with the tidal current cycle of ~6 hours and 12 minutes. The model is intended to describe a short-duration localized periodicity of near-surface (top 1m) plankton density in terms of variable tidal current velocity. The behavior of the model will be compared to empirical data provided by 

   * a SMartBuoy deployed in the Warp station estuary in the North Sea by the Center for Environment Fisheries and Aquaculture Science          (CEFAS) and 
   * tidal gauge data from the nearby Sheerness station collected by the British Oceanographic Data Center (BODC)(8)(17)(18) 

The Warp station in the North Sea is located in a shallow tidal inlet, with stable depth of 15 meters and tidal range of 4.3 meters (8)(17). The water column is well mixed due to its shallow depth and turbulent mixing as a result of tidal current. The proposed model will make several simplifying assumptions, which follow from the short-duration temporal scale of the research question and the characteristics of the empirical context that is being explored. The model will assume the following: 

   * there will be no loss of plankton due to grazing or death; 
   * there will be no growth of plankton due to photosynthesis; 
   * at any time (t) the horizontal (x, y) distribution of plankton density will be assumed to be uniform in the inlet; 
   * there will be no consideration of changes in density corresponding to the change in volume due to rise and fall of the water              level; 
   * tidal current velocity will be treated as a laminar force perpendicular to the mouth of the inlet (10)
  
The model then seeks only to describe variability in the vertical (z) distribution of plankton density in the water column as a consequence of periodic laminar flow velocity. 

The chlorophyll fluorescence readings used to validate the model are taken at a discrete point in the (x, y) space at a depth of 1 meter from the surface (17). The assumption of uniformity in the (x, y) plane parallel to the surface is made to eliminate the impact of horizontal transport / advection of plankton during the tidal cycle. This assumption follows from the empirical observation that changes in salinity and temperature are dominated by the 12 hour semidiurnal tidal cycle, though remain relatively stable through the 6 hour tidal current cycle (8). This observation comes from the paper below:

```
Dancing with the Tides: Fluctuations of Coastal Phytoplankton Orchestrated by Different Oscillatory Modes of the Tidal Cycle.
Blauw AN, Beninca` E, Laane RWPM, Greenwood N, Huisman J (2012)
PLoS ONE 7(11): e49319. doi:10.1371/journal.pone.0049319
```

Further the assumption of (x,y) planar uniformity allows for the proposition of a specific discrete state space in the (z) direction, which will make a solution by finite difference methods possible. The model will describe the change in plankton density at 1m spatial steps in the (z) direction, and at 1-second time steps through the tidal-current period of ~6 hours. The three dimensional distribution (x, y, z) of plankton within each 1m section of the water column at any time (t) will be assumed to be uniform. The concentration P(z, t) of plankton at depth (z) and time (t) will be the output of the model at each step in time, though it is the concentration P(t(n), zmax) in the top 1 meter of the water column that is of specific interest given the availability of empirical data. 


### Model derivation

#### Simple one dimensional diffusion over infinite domain (no boundary conditions)

The base of the model is a one dimensional diffusion equation—Fickian diffusion or the heat equation—which describes the random motion of particles in a Newtonian fluid caused by unresolved turbulence or agitation (19). The equation is expressed as the following partial differential equation: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_eq_1.png)

This equation is not solvable analytically, though it can be solved numerically for the variable concentration P(z, t) given known parameters for D and sufficient boundary conditions (3)(19)(20). The left-hand expression is of order 1 in time, and therefore requires a single boundary condition for t=0 at each interval in z. The right-hand expression is a second order spatial derivative, and therefore requires two boundary conditions at either edge of the domain {x=0, x=dx(n)(19). Boundary conditions and initialization of parameters will be discussed bellow. The simplest and most intuitive method of solving this equation numerically is to use a forward in time centered in space (FTCS) finite difference method(19). This method allows you to discretize the problem in space and time by representing the right and left side as finite differences using Taylor expansion. The left-hand temporal derivative is thus restated and rearranged for P’(x, t): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_2_eq2.png)
![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_3_eq3.png)

This is the forward difference approximation of the temporal derivative using the Taylor expansion(19). In my implementation of the FTCS scheme I have not considered the error term O(dt) and have disregarded the higher order terms. The central difference approximation for the right hand second order spatial derivative can be derived as follows: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_4_eq_4.png)
![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_5_eq_5.png)

From the first expression you can get the forward difference approximation as above for the time step t + dt but instead for z + dz, and the second yields the backwards difference approximation. Subtracting the backward difference approximation from the forward approximation, you get the central difference approximation for the first order spatial term(19). When you then add the backward and forward difference approximations you get an expression for the second order spatial term: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_6_eq_6.png)
![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_7_eq_7.png)
![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_8_eq8.png)

The terms on the end are truncation errors resulting from the discretization of the continuous diffusion equation. This error can become cumulatively significant in long-term model simulations. A more formal consideration of truncation error is something that would benefit the model proposed here given more time. These errors will not be considered in the remainder of this analysis. Substituting in the forward difference expression for the first order temporal derivative on the left, and the central difference approximation of the second order spatial term on the right, gives the FTCS approximation of the one dimensional diffusion equation(20)(19): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_9_eq9.png)
![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_10_eq_10.png)

This is the baseline equation that is used to build the model for this project, and can be used to describe the sequential change of concentration of particles specified by P(z, t +dt) at each step in time dt. This FTCS approximation of the diffusion equation specified above was easily transcribed into pure python and simulated for different time increments with the following function: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_1.png)

The results that are produced by this method are dependent on the initialization of parameters (P(zn, t) vector for t=0 and z in (0, ndz)), and the selection of the diffusion coefficient D. Often this solution is demonstrated with a single punctuated release, meaning that the initial concentration vector at t=0 is a zero vector with one component not equal to zero from which the concentration spreads (v0 = [0,0,0,40,0,0,0]) (19)(3). The situation I am trying to model takes in some distribution of plankton density P0 at t=0, which is then redistributed throughout the water column in (z) through the 6 hour tidal current cycle. This redistribution occurs with no loss of plankton mass, which is the effect of the assumption of uniform distribution of plankton density in the (x, y) plane (meaning that horizontal advection through the tidal cycle does not change the vertical gradient since it is the same throughout the inlet).  I mention this because an initialization with a single punctuated release is not representative of this variable initial density distribution P0. For this reason I experimented with multiple punctuated release points of varying magnitudes and spacing. The following is a plot of the model when initialized with two symmetric concentrations (in magnitude and space) at t=0: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_2.png)



### Hardware: 
In order to do this project, two underwater camera sensors were made using Raspberry Pi's (pictured below). The complete set of materials used is as follows: 
  * 2x Raspberry Pi SCB 
  * 2x Logitech C905 USB webcams
  * 2x 16G USB storage devices
  * 2x 5200 mAh lithium ion battery packs
  * 2x SPOR PCB with USB and Micro-USB 
  * 2x Micro-USB to USB cables
  * 2x plastic 7.5 x 3.5 x 2 inch plastic boxes 

Each of the devices was booted on a Raspbian linux image via micro-sd cards. Code for motion detection and subprocess for writing out labeled frames was implemented in python via openCV. Instllation was a bit trying, though this is generally the case with openCv given its significant associated requirements and space contraints of the SCB's. The boxes were sealed with Smarter Adhesive Solutions 16 fast-set medium bodied solvent cement, and mounted to submerged trees in the regions of interest. NB: the seams were insufficient, and on the second deployment one of the boxes leaked and the Pi was destroyed. I have since purchased another Pi and am working towards an improved housing design. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/camera-sensors.png)


### Motion Detection:
The process for detecting and classying the observed fish begins with a light-weight / real time motion detection functionality implemented in openCv. Motion detection is much less computationaly heavy than object-detection & classficiation, which requires the use of deep learning methodology. The classification component of this project is implemented only after image data has been collected by the submerged cameras, with the models being trained locally on labeled images from the stoage devices attatched to the Raspberry Pi's. The figure below, which is an example frame from a test deployment of the sensor in my fishtank, shows the output of the motion detection process. From left to right, the images show: the mask, and improved delta and the resulting video frame with bounding rectangle drawn on screen. Detection is simple in principle: openCv is told what the 'empty' tank looks like, and then a pixel matrix is created for the unoccupied space. Then, any deviations from this structure are marked as occupations, and motion is detected. The contraint here is that the model must therefore be told what the 'empty' frame is so that it can measure disruptions. Since the intent was to built a geneirc sensor, I had to design a process to identify the 'empty' frame without manually providing it. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/delta-mask-monitor.png)


### Application of regular SVD to initialize empty frame: 
For this I applied an implementation of regular SVD found in a solution proposed for one of the standardized videos from the 'Background Models Challenge Dataset'. The solution was presented as part of a Numerical Linear Algebra course originally taught in the University of San Francisco MS in Analytics graduate program, and can be found here: https://nbviewer.jupyter.org/github/fastai/numerical-linear-algebra/blob/master/nbs/3.%20Background%20Removal%20with%20Robust%20PCA.ipynb . The method itself is efficient and relies on the scikitlearn decomposition utility. The image below shows the actual empty tank taken a a frame from the video --on the left -- and the tank background after the application of SVD. The video quality is relatively poor, so the still frame is actually less clear than the one produced by the decomposition, which is awesome. This method is sensitive to changes in lighting, and so if there is vairable cloud cover, one inititalization will fail once the cloud cover changes significanlty. To solve this I included functionality to periodically recalculate the background frame. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/real-tank-vs-svd-tank.png)


### Use of motion detection to automate annotations: 
When motion is detected, the camera then transfers each occupied frame to the USB storage device. Given the number of frames per second that the device sees, and the large number of potentially spurious objects (such as leaves), I had to specify a large threshold value for what was considered to be a detected object. Further, these images are ultimately meant to be used to train a model, so images with many bounding rectangles and objects at multiple depths are difficult to annotate and to use. For this reason I also specified that a frame would only be written to memory if 1) it was of a large enough size and 2) if there was only one detected object in the frame. This may seem like a severe limitation but the camera sees so many objects that it turned out to be an effective method. Moreover, this set of constraints allowed for a very helpful adaptation of the model training process. Instead of using a GUI or command line utility to move through the frames and draw / label each rectangle, I was able to use the dimensions of the bounding rectangles to produce labeled xml annotations that could be used to train models for detection and classification. The figure below shows the output of this process for an adequatey sized frame. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/label-and-image.png)


### Fish classification: 
While efforts at motion detection were successful, classification of the fish images for population analysis proved to be a more stubborn problem. I initially beleived that object-detection was a required step in this process, though after using the motion detection process to generate automatic annotations, I realized it could be leveraged then to crop out regions of interest from the frame. This recognition could provide substantial contribution to this post, detailing a submission to a kaggle competition which asked participants to classify boated-fish from commercial fishing boat cameras (https://flyyufelix.github.io/2017/04/16/kaggle-nature-conservancy.html), on which I based my classification analysis. This paper creates an ensemble method in which the fist layer is object-detection, for which I now think deep learning is not nessecary. Even though they cant put any software on the boat cameras --unlike in my case -- there is enough stationary camera data to apply the same SVD process and reduce the complexity of the problem. For classification I attempted two general methods: 

  * Classify fish into 1) carp 2) sucker 3) other
  * Classify fish into 1) rock bass 2) sunfish 3) smallmouth bass 4) white sucker 5) carp

Domain of classifier: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/domain-fish-images.png)

Both methods were tested using ResNet-152 (Keras implementation with ImageNet pre-trained weights: https://gist.github.com/flyyufelix/7e2eafb149f72f4d38dd661882c554a6) recommended / written up as part of the solution to the very similar problem outlined in the solution referenced above-- indeed the author is the same, and has based his work on a paper: 
```
Deep Residual Learning for Image Recognition.
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
arXiv:1512.03385
```
As expected, the 3 level classification yeilded much better results than the 5 level classification. This is because both the carp and sucker fish are so much larger than the other fish, that the distinction was simplified. Keeping in mind the known discrepancy in population across the two regions, the classification model ultimately learns to assign predictive weight to aspects of the stationary frame in each of the two scenarios (despite much of this context being eliminated by the bounding rectangles). It is very likely that a white sucker, if observed by the camera deployed in the downstream section, would be mislabeled as a carp or vise versa. Though this has not yet been observed, larger rock bass and small mouth bass have been mislabeled as carp in the region with many carp, while they have been labeled as white sucker fish in the region with many white suckers. An example of the problem of spurious frame based learning is pictued in the image below, which was taken from the solution write up linked in the above passage: heatmap shows regions of model focus for a given input image.  

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/spurious-features.png)

### To do / Expanding on current state: 
Moving forward, the model must be made more robust. Classification, while modestly effective in the 3 level implementation, was impacted significantly by the background features of the two locations as mentioned above. Some potential solutions to this have been proposedon the forum for the Nature Conservancy Fisheries Monitoring competition. Going forward I intend to test some of these methods for my project.  

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/arduino-temperature-sensor.png)

In the hardware department, there is a lot to be done. The first two cameras -- as evidenced by the destruction of one of them -- were not designed optimally. Work is needed to secure the cameras and insure that they are sealed properly. I have also built two temperature / humidity sensors that I have not yet deployed (one pictured above). For these, some more work on the Arduino sketch used to measure the temperature is required. 

## Appendix: Initital attempt at object-detection

### Object detection & training the SSD (single-shot-detection) mobilenet CNN: 
Before implementing the automated annotation functionality, I thought that an object detection model had to be trained so that fish classification could be accomplished. For this I used the tensorflow object detection API, which can be challenging to stand up. The process is as follows: 
  * Divide images into training and testing sets
  * Convert xml labels to csv
  * Create tf records file that can be read by tensorflow to train the model
  * Train the model and wait for enough steps to get adequate convergence (process illustrated in the figure below) 
  * Export the frozen inference graph to be used in objet detection
  * Run object detection script and observe results

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/loss-graph.png)

I am running the CPU version of tensorflow, which is tedious and inefficient. For this reason I have not yet been able to train for enough steps to produce a high performant model. That being said, even the CPU version with inadequate convergence produces an ok model. The model was run on the testing subset of images and was able in most cases to find the large carp in the video frames.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/mobilenet-applied-carp.png)

### Thanks for reading!! 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/me-with-sucker.png)



