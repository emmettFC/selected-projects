#!/bin/sh
curl -O https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/ice_surface/grid_registered/netcdf/ETOPO1_Ice_g_gmt4.grd.gz
gunzip -k ETOPO1_Ice_g_gmt4.grd.gz