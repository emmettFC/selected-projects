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


![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/label-and-image.png)

### Use of motion detection to automate annotations: 
When motion is detected, the camera then transfers each occupied frame to the USB storage device. Given the number of frames per second that the device sees, and the large number of potentially spurious objects (such as leaves), I had to specify a large threshold value for what was considered to be a detected object. Further, these images are ultimately meant to be used to train a model, so images with many bounding rectangles and objects at multiple depths are difficult to annotate and to use. For this reason I also specified that a frame would only be written to memory if 1) it was of a large enough size and 2) if there was only one detected object in the frame. This may seem like a severe limitation but the camera sees so many objects that it turned out to be an effective method. Moreover, this set of constraints allowed for a very helpful adaptation of the model training process. Instead of using a GUI or command line utility to move through the frames and draw / label each rectangle, I was able to use the dimensions of the bounding rectangles to produce labeled xml annotations that could be used to train the object detection model. The above figure shows the output of this process for an adequatey sized frame. 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/loss-graph.png)


### Object detection & training the SSD mobilenet CNN for recognition: 
Once labels and images have been generated via motion detection, and exctracted from the USB storage after sensor retreival, the object recognition model had to be trained so that fish classification could be accomplished. For this I used the tensorflow object detection API, which can be challenging to stand up. The process is as follows: 
  * Divide images into training and testing sets
  * Convert xml labels to csv
  * Create tf records file that can be read by tensorflow to train the model
  * Train the model and wait for enough steps to get adequate convergence (process illustrated in the above figure) 
  * Export the frozen inference graph to be used in objet detection
  * Run object detection script and observe results

I am running the CPU version of tensorflow, which is tedious and inefficient. For this reason I have not yet been able to train for enough steps to produce a high performant model. That being said, even the CPU version with inadequate convergence produces a workable model for recognition. The model was run on the testing subset of images and was able in most cases to find the large carp in the video frames.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/mobilenet-applied-carp.png)

### To do / Expanding on current state: 
Moving forward, it the model must be made more robust and applied to both the White Sucker and the Carp. The ultimate goal is differentiation, which has not yet been accomplished. To do this it will be necessary to train a model on multiple classes, correct for depth, and orientation -- perhaps via application of siamese neural network. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/arduino-temperature-sensor.png)

In the hardware department, there is a lot to be done. The first two cameras -- as evidenced by the destruction of one of them -- were not designed optimally. Work is needed to secure the cameras and insure that they are sealed properly. I have also built two temperature / humidity sensors that I have not yet deployed (one pictured above). For these, some more work on the Arduino sketch used to measure the temperature is required. 

### Thanks for reading!! 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fishViz/assets/me-with-sucker.png)


