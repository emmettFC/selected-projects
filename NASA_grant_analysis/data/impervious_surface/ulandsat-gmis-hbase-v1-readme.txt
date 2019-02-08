December 2017

Global Man-made Impervious Surface (GMIS) and Global Human Built-up And Settlement Extent (HBASE) data products

The GMIS and HBASE data products have four components, each corresponding to one band of the GeoTIFF files gridded according to UTM zones 

A map of the UTM grids is available at: https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system#/media/File:Utm-zones.jpg


The components/bands include:

1. Percent imperviousness

Value:	
0-100	Percent impervious.
200	Areas masked as non-HBASE by the HBASE mask. Users may choose to fill these pixels as 0% impervious.	
255	NoData, including unmapped areas, pixels with SLC (Scan Line Corrector)-off gaps, pixels covered by cloud/shadow.

2. Standard Error of percent imperviousness

Value:
0-100	Standard Error of percent  impervious. Please note that the standard error is estimated from the RMSE (Root-Mean-Square Error) of the node of the decision tree model used to predict percent imperviousness, not from independent accuracy assessment.	
255	NoData, including unmapped areas, pixels with SLC-off gaps, pixels covered by cloud/shadow.

3. HBASE mask

Value:		
200	Non-HBASE		
201	HBASE		
202	Road pixels rasterized from OpenStreetMap. Note that only major roads are included and road pixels within the HBASE mask are labeled as 201.	
255	NoData, including unmapped areas, pixels with SLC-off gaps, pixels covered by cloud/shadow.

4. Probability of HBASE

Value:		
0-100	Probability of HBASE. The probability value is estimated using the Random Forest algorithm.	
255	NoData, including unmapped areas, pixels with SLC-off gaps, pixels covered by cloud/shadow.
