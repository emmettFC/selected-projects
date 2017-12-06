# sharkTrack
## Scrape white shark telemetry from OCEARCH Global Shark Tracker & build visualizations against NOAA CoRTAD SST and ETOPO1 bathymetry

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/data-source-logo-map.png)

### Topics included in this repository: 
1. Data scraping: 
  * Implementation of robust scraping proceedure to ingest & update database of White Shark geolocation

2. Data Integration: 
  * Integrating external data sources with White Shark geolocation data
  * Work with mutliple GIS data protocol through open source libraries in python (NCDF4; OpenDAP; Gridfile) 

3. Data Visualization: 
  * Production of high quality GIS visualizations by integration of OCEARCH White Shark data, ETOPO1 bathymetric tiles and Sea Surface Temperature from NOAA Coral Reef Temperature Anomaly Database
  * Implement kernel density estimate to smooth sparse point data 
 


![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/bathy-and-sst-fall-spring.png)

### Project Overview: 
This past summer I saw an article in the New Haven Register that reported the sensational fact of a White Shark having been tracked into the Long Island Sound. I typically spend a few weeks each summer at my family cottage in Madison CT, which is less than a mile from Guilford -- the reported location of the White Shark (Montauk, migration pattern pictured below). The article referenced the OCEARCH Global Shark Tracker, a web-based application that tracks the location of tagged sharks and plots them on a map. While I liked their interface, I thought it could be improved upon through the integration of external data sources and the addition of a dynamic component to enable season-specific visualization. I subsequently wrote a scraping process in python and pulled down the geopoint data from the tracker so that I could build out this functionality. This project repository presents some of that initial discovery work.  

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/Montauk-Migration.png)


### Data ingestion & backend structure
I wrote a scraping proceedure in python to extract all of the geopoint data used to populate the map on the OCEARCH shark tracker home page. This process employs basic post-request structure, with all variables determined via the inspect element functionality in the Google Chrome browser. Data is then loaded into an elasticsearch index where it can be queried at the specified port (in my case localhost:5601) and Kibana Plugin. It is then simple to load and transform accordingly.

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/both-backend-images.png)


### Data visualization: Kernel Density 
For the first pass at visualization, I wanted to segment the data according to season and see how the population moved. Scatter plots were a bit confusing to look at, and the concentration of sharks near the coast obscured the density given how close they were to one another. To navigate this I applied a bivariate kernel density estimate, using the havershine distance metric, in an attempt to get a better sense of the concentration (pictured below). 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/kernel-density-plots-whiteShaks-seasonal.png)


### Data visualization: Sea Surface Temperature 
The density plot illustrates clear seasonal migration. The most basic next step seemed then to plot the corresponding change in water temperature as a point of reference. The pings are only sent to the satellite when the shark fins--or when the submerged device breaches / nearly breaches the surface of the water. I found a helpful resource that detailed the application of the NOAA CoRTAD SST layer to basemap projections (can be accessed here http://www.trondkristiansen.com/), which I implemented for the region of interest in the Atlantic (pictured below). 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/fall-map-temp-only.png)


### Data visualization: Adding the bathymetric model
As sharks move out past the shelf they pass into deep water. That said there are isolated points of lower depth far out in the Atlantic. As a final component of this initial mapping effort, I thought it would be useful to integrate a bathymetric model into to the plot to see if any observable concentration around these points of lower depth existed. The post detailing the SST application also made referece to the ETOPO1 global relief model, which I then integrated (as shown below): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/spring-actual-big.png)


### To do / Moving forward: 
I did some research into shark migration in the North Atlantic, and discovered that there were two semi-distinct migration patterns for White Sharks: Coastal -- sharks that migrate approximately from Florida to Cape Cod -- and Oceanic -- sharks that during late winter and early spring move out way into the open Atlantic ocean. While the costal migration pattern was generally understood, there was no consensus on the factors driving those sharks to make the jouney far into the Atlantic. Given the available geolocation data, I think a reasonable next step would be to featurize the migration patterns of the individual sharks and use it to classify them into one of the two migration cohorts. In addition to the geolocation data, OCEARCH hosts a set of other metrics associated with each shark (ex age, sex, weight..). If the migration clustering is successful, it would be interesting to see if any of these other available datapoints had any predictive power on the migration behavior, and therefore provide some insight into the factors that drive the Oceanic sharks out into the Atlantic. 

### Thanks for reading!

