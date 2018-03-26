#!/bin/bash
# Assign crs of EPSG:4326 in-place to each raster
# for much more convenient processing afterwards!

return_periods=(00002 00005 00025 00050 00100 00250 00500 01000)

# EUWATCH observations
for return in ${return_periods[@]}
do

gdal_edit.py \
    -a_srs EPSG:4326 \
    data/tanzania_flood/EUWATCH/inun_dynRout_RP_${return}_Tanzania/inun_dynRout_RP_${return}_contour_Tanzania.tif

done # return_periods

# GLOFRIS models
models=(GFDL-ESM2M HadGEM2-ES IPSL-CM5A-LR MIROC-ESM-CHEM NorESM1-M)

for model in ${models[@]}
do
for return in ${return_periods[@]}
do

gdal_edit.py \
    -a_srs EPSG:4326 \
    data/tanzania_flood/${model}/rcp6p0/2030-2069/inun_dynRout_RP_${return}_bias_corr_masked_Tanzania/inun_dynRout_RP_${return}_bias_corr_contour_Tanzania.tif

done # return_periods
done # models

# SSBN
ssbn_return_periods=(5 10 20 50 75 100 200 250 500 1000)

declare -A ssbnmodels
ssbnmodels=(
    ["TZ_fluvial_defended"]="FD"
    ["TZ_fluvial_undefended"]="FU"
    ["TZ_pluvial_defended"]="PD"
    ["TZ_pluvial_undefended"]="PU"
    ["TZ_urban_defended"]="UD"
    ["TZ_urban_undefended"]="UU"
)

for model in ${!ssbnmodels[@]}
do
for return in ${ssbn_return_periods[@]}
do
abbr=${ssbnmodels[${model}]}

gdal_edit.py \
    -a_srs EPSG:4326 \
    data/tanzania_flood/SSBN_flood_data/${model}/TZ-${abbr}-${return}-1.tif

done # return_periods
done # models
