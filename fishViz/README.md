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



