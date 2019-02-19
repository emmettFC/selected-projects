# fish_vision

## Building underwater cameras to take pictures of fish remotely & training an image classifer on the data

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/carp-title-panel-final.png)

### Project Overview: 

The Wissahickon Creek in Philadelphia is home to ton of fish. There are two adjacent sections of the creek that have different populations of fish. One has a family / multiple families of White Suckerfish (Catostomus commersonii), and the other has a family of Common Carp (Cyprinus carpio). I know this because I spend a lot of time in the water in both sections and this is/was a pretty stable dynamic, but promted the idea that maybe I could build some hardware / train a classifier to reproduce this observation without any assumptions on the distribution of fish in the two sections. This is a write-up of the attempt at doing that, with a discussion of the cameras and the classification model.


### Hardware: 
In order to do this project, two underwater camera sensors were made using Raspberry Pi's (pictured below). The complete set of materials used is as follows: 
  * 2x Raspberry Pi SCB 
  * 2x Logitech C905 USB webcams
  * 2x 16G USB storage devices
  * 2x 5200 mAh lithium ion battery packs
  * 2x SPOR PCB with USB and Micro-USB 
  * 2x Micro-USB to USB cables
  * 2x plastic 7.5 x 3.5 x 2 inch plastic boxes 

Each of the devices was booted on a Raspbian linux image via micro-sd cards. Code for motion detection and subprocess for writing out labeled frames was implemented in python via openCV (which can be tricky to install on the pi's). The boxes were sealed with Smarter Adhesive Solutions 16 fast-set medium bodied solvent cement, and mounted to submerged trees in the regions of interest. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/cams-fnal.png)


### Motion Detection:
The process for detecting and classying the observed fish begins with a light-weight / real time motion detection functionality implemented in openCv on the cameras. The figure below, which is an example frame from a test deployment of the sensor in my fishtank, shows the output of the motion detection process. From left to right, the images show: the mask, and improved delta and the resulting video frame with bounding rectangle drawn on screen. Detection is simple in principle: openCv is told what the 'empty' tank looks like, and then a pixel matrix is created for the unoccupied space. Then, any deviations from this structure are marked as occupations, and motion is detected. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/delta-mask-monitor.png)


### Application of regular SVD to initialize empty frame: 
The next step in the process is to build out functionality to initialize the 'empty' frame for object detection. For this I applied an implementation of regular SVD found in a solution proposed for one of the standardized videos from the 'Background Models Challenge Dataset'. The solution was presented as part of a Numerical Linear Algebra course originally taught in the University of San Francisco MS in Analytics graduate program, and can be found here: https://nbviewer.jupyter.org/github/fastai/numerical-linear-algebra/blob/master/nbs/3.%20Background%20Removal%20with%20Robust%20PCA.ipynb . The method itself is efficient and relies on the scikitlearn decomposition utility. The image below shows the actual empty tank taken a a frame from the video --on the left -- and the tank background after the application of SVD. The video quality is relatively poor, so the still frame is actually less clear than the one produced by the decomposition, which has smoothed out this variability. This method is sensitive to changes in lighting, and so if there is vairable cloud cover, one inititalization will fail once the cloud cover changes significanlty. To solve this I included functionality to periodically recalculate the background frame. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/svd-fnal.png)


### Process for saving valid images to memory and annotating training data: 
When motion is detected, the camera then transfers each occupied frame to the USB storage device. Given the number of frames per second that the device sees, and the large number of potentially spurious objects (such as leaves), I had to specify a large threshold value for what was considered to be a detected object. Further, these images are ultimately meant to be used to train a model, so images with many bounding rectangles and objects at multiple depths are difficult to annotate and to use. For this reason I also specified that a frame would only be written to memory if 1) it was of a large enough size and 2) if there was only one detected object in the frame. This may seem like a severe limitation but the camera sees so many objects that it turned out to be an effective method. This process also makes it pretty simple to use the data for training a classification network, because the dimension of the bounding rectangles from the detection output can be used to 1) produce and label xml annotations (below) and 2) crop out the minimal bounding rectangle to feed the model which helps to mitigate the effect of spurious frame-based learning. The latter issue is addressed in the next section. The figure below shows the output of this process for an adequatey sized frame. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/annot-fnal.png)


### Fish classification: 
I based my classification model on this  paper -- https://flyyufelix.github.io/2017/04/16/kaggle-nature-conservancy.html -- which applies Faster R-CNN (Region based convolutional nueral network) to classify boated fish from camera images taken on commercial fishing vessels. This paper creates an ensemble method in which the fist layer is object-detection, for which I now think deep learning is not nessecary--given the output of the motion detection process. Even though they cant put any software on the boat cameras --unlike in my case -- there is enough stationary camera data to apply the same SVD process and reduce the complexity of the problem. For classification I attempted two general methods: 

  * Classify fish into 1) carp 2) sucker 3) other
  * Classify fish into 1) rock bass 2) sunfish 3) smallmouth bass 4) white sucker 5) carp

Domain of classifier: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/fish-class-fnal.png)


Both methods were tested using ResNet-152 (Keras implementation with ImageNet pre-trained weights: https://gist.github.com/flyyufelix/7e2eafb149f72f4d38dd661882c554a6) recommended / written up as part of the solution to the very similar problem outlined in the solution referenced above-- indeed the author is the same, and has based his work on a paper: 
```
Deep Residual Learning for Image Recognition.
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
arXiv:1512.03385
```
The confusion matricies for the different classifiers are shown below, with the three level classification outperforming the 5 level classification. Carp were correctly classified around 70% of the time in either model. On the other hand, the suckerfish classification in the 5 level model is only 27%, while it is 70% in the 3 level model.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/final-confusion.png)


One interesting observation is that when the models are used to predict testing data which is taken all from one of the section, the mislabeling of fish in the 'other' category are more often misclassified as suckerfish in the region with more suckerfish, whereas they are mislabeled as Carp on the section with more Carp. As adressed in the paper above, the classification model ultimately learns to assign predictive weight to aspects of the stationary frame in each of the two scenarios (despite much of this context being eliminated by the bounding rectangles). An example of the problem of spurious frame based learning is pictued in the image below, which was taken from the solution write up linked in the above passage: heatmap shows regions of model focus for a given input image.  


![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/spurious-features.png)

### To do / Expanding on current state: 
Moving forward, the model must be made more robust. Classification, while modestly effective in the 3 level implementation, was impacted significantly by the background features of the two locations as mentioned above. Some potential solutions to this have been proposed on the forum for the Nature Conservancy Fisheries Monitoring competition. Going forward I intend to test some of these methods for my project.  

In the hardware department, there is a lot to be done. The seals on one of the cameras broke and it destroyed the board, so the housing for the cameras needs to be improved. I have also built two temperature / humidity sensors that I have not yet deployed (one pictured below). For these, some more work on the Arduino sketch used to measure the temperature is required. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/ard-fnal.png)

## Appendix: Initital attempt at object-detection

### Object detection & training the SSD (single-shot-detection) mobilenet CNN: 
Before implementing the automated annotation functionality, I thought that an object detection model had to be trained so that fish classification could be accomplished. For this I used the tensorflow object detection API. The process is as follows: 
  * Divide images into training and testing sets
  * Convert xml labels to csv
  * Create tf records file that can be read by tensorflow to train the model
  * Train the model and wait for enough steps to get adequate convergence (process illustrated in the figure below) 
  * Export the frozen inference graph to be used in objet detection
  * Run object detection script and observe results

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/loss-graph.png)

I am running the CPU version of tensorflow, which takes up a lot of space and has very long run times for models to converge. For this reason I have not yet been able to train for enough steps to produce a high performant model. That being said, even the CPU version with inadequate convergence produces an ok model. The model was run on the testing subset of images and was able in most cases to find the large carp in the video frames.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/fish_vision/assets_README/carp-ob-fnal.png.png)

### Thanks for reading!! 
