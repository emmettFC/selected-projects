# sharkTrack
## Scrape white shark telemetry from OCEARCH Global Shark Tracker & build visualizations against NOAA CoRTAD SST and ETOPO1 bathymetry

![alt text](https://github.com/emmettFC/selected-projects/blob/master/sharkTrack/assets/data-source-logo-map.png)

### Topics included in this repository: 
1. Data scraping: 
  * Implementation of robust scraping proceedure to ingest & update database of White Shark geolocation

2. Data Integration: 
  * Integrating external data sources with White Shark geolocation data
  * Work with mutliple GIS data protocol through open source libraries in python (NCDF4; Gridfile) 

3. Data Visualization: 
  * Production of high quality GIS visualizations by integration of OCEARCH White Shark data, ETOPO1 bathymetric tiles and Sea Surface Temperature from NOAA Coral Reef Temperature Anomaly Database
  * Implement kernel density via havershine distance metric to smooth sparse point data 
  
### Project Overview: 
This past summer I saw an article in the New Haven Register that reported the sensational fact of a White Shark having been tracked into the Long Island Sound. I typically spend a few weeks each summer at my family cottage in Madison CT, which is less than a mile from Guilford -- the reported location of the observed White Shark (Montauk). 
