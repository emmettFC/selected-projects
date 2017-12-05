# fishViz
## Research and application of methods to video collection & analysis in variable low-light limnological contexts

### Topics included in this project repository: 
1. Computer vision:
  * Motion detection in openCv 
  * Background removal for 'empty' frame initialization via applied regular singular value decomposition
  * Object detection in tensorflow
  * Applied feature extraction and convolutional neural network via SSD Mobile Net algorithm 

2. Automated annotation: 
  * Implementing new method for automating annotations - generating xml labels via bounding rectangles

3. Remote sensing: 
  * Two underwater camera sensors built with Raspberry Pi's
  * Implementation of light-weight motion detection on Raspbian image
  * One humidity/temperature sensor built with Arduino Uno (not deployed) 
  * One humidity/temperature sensor built with Arduino Yun (not deployed) 
 
![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/wissahickon-creek.png)

### Project Overview: 
Philadelphia's Wissahickon Creek is one of its 7 major subwatersheds and drains into the Schuylkill river. The creek is known to be very dirty, swimming is prohibited but many do so despite the prohibition. It is also an attractive destination for anglers due to the variety and density of its fish population. The creek is stocked with adult trout twice each year. I am a frequent and somewhat zealous snorkler of the creek, which has dense pockets of fish with (occasionally) high visibility. I identified two adjacent sections of the creek, each less than 300 yards long, which -- with the exception of short periods following very heavy rainfall -- are separated by rockbeds where the water level is < 3 inches deep. The effect of this segmentation is that there is an observably distinct population of fish on either side of these spillways, though the sections are nearly touching one another. While Redbreasted Sunfish, Rockbass, Smallmouth Bass and Pumpkinseeds exist in aproximately equal number, one section has an abundance of very large (>20 lbs) Common Carp, and the other has almost none. In the section without these Carp, there is an abundance large (1-4 pounds) White Suckers, which I have seen only very rarely in the downstream section. Though this is likely an unsubstantial phenomenon from the ecological perspective, it presents an interesting opportunity for data analysis. Namely, I wondered if this population discrepancy could be reproduced by the deployment of remote sensors, without application of any prior assumptions on the distribution of fish across the two sections of the creek. This project is as of this writing incomplete, though significant progress has been made. The following sections provide a breif / high-level description of the methods applied to this point.


![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/camera-sensors.png)

### Hardware: 
In order to do this project, two underwater camera sensors were made using Raspberry Pi's. The complete set of materials used is as follows: 
  * 2x Raspberry Pi SCB 
  * 2x Logitech C905 USB webcams
  * 2x 16G USB storage devices
  * 2x 5200 mAh lithium ion battery packs
  * 2x SPOR PCB with USB and Micro-USB 
  * 2x Micro-USB to USB cables
  * 2x plastic 7.5 x 3.5 x 2 inch plastic boxes 

Each of the devices was booted on a Raspbian linux image via micro-sd cards. Code for motion detection and subprocess for writing out labeled frames was implemented in python via openCV. Instllation was a bit trying, though this is generally the case with openCv given its significant associated requirements and space contraints of the SCB's. The boxes were sealed with hot glue and electrical tape, and mounted to submerged trees in the regions of interest. NB: the hot glue seams were insufficient, and on the second deployment one of the boxes leaked and the Pi was destroyed. I have since purchased another Pi and am working towards an improved housing design. 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/delta-mask-monitor.png)

### Motion Detection:
The process for detecting and classying the observed fish begins with a light-weight / real time motion detection functionality implemented in openCv. Motion detection is much less computationaly heavy than object-detection, which requires the use of neural networks and tensorflow. The object-detection component of this project is implemented only after image data has been collected by the submerged cameras, with the mobilenet CNN being trained locally on labeled images from the stoage devices attatched to the Raspberry Pi's. The figure above, which is an example frame from a test deployment of the sensor in my fishtank, shows the output of the motion detection process. From left to right, the images show: the mask, and improved delta and the resulting video frame with bounding rectangle drawn on screen. Detection is simple in principle: openCv is told what the 'empty' tank looks like, and then a pixel matrix is created for the unoccupied space. Then, any deviations from this structure are marked as occupations, and motion is detected. The contraint here is that the model must therefore be told what the 'empty' frame is so that it can measure disruptions. Since the intent was to built a geneirc sensor, I had to design a process to identify the 'empty' frame without manually providing it. 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/real-tank-vs-svd-tank.png)

### Application of regular SVD to initialize empty frame: 
For this I applied an implementation of regular SVD proposed in a solution proposed for one of the standardized videos from the 'Background Models Challenge Dataset'. The solution was presented as part of a Numerical Linear Algebra course originally taught in the University of San Francisco MS in Analytics graduate program, and can be found here: https://nbviewer.jupyter.org/github/fastai/numerical-linear-algebra/blob/master/nbs/3.%20Background%20Removal%20with%20Robust%20PCA.ipynb . The method itself is efficient and relies on the scikitlearn decomposition utility. The image above shows the actual empty tank taken a a frame from the video --on the left -- and the tank background after the application of SVD. The video quality is relatively poor, so the still frame is actually less clear than the one produced by the decomposition, which is awesome. This method is sensitive to changes in lighting, and so if there is vairable cloud cover, one inititalization will fail once the cloud cover changes significanlty. To solve this I included functionality to periodically recalculate the background frame. 



### Use of motion detection to automate annotations: 


