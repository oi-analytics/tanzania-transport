# return_periods=(00002 00005 00025 00050 00100 00250 00500 01000)

# # Convert EUWATCH observations
# for return in ${return_periods[@]}
# do
# echo "EUWATCH_${return}"

# gdal_polygonize.py \
#     data/tanzania_flood/EUWATCH/inun_dynRout_RP_${return}_Tanzania/inun_dynRout_RP_${return}_contour_Tanzania.tif \
#     -f "ESRI Shapefile" \
#     data/tanzania_flood/EUWATCH_${return}_vector.shp

# ogr2ogr \
#     -a_srs "EPSG:4326" \
#     -where "DN > 0" \
#     data/tanzania_flood/EUWATCH_${return}_filtered.shp \
#     data/tanzania_flood/EUWATCH_${return}_vector.shp

# rm data/tanzania_flood/EUWATCH_${return}_vector.shp
# done

# # Convert models
# models=(GFDL-ESM2M HadGEM2-ES IPSL-CM5A-LR MIROC-ESM-CHEM NorESM1-M)

# for model in ${models[@]}
# do
# for return in ${return_periods[@]}
# do
# echo ${model}_${return}

# gdal_polygonize.py \
#     data/tanzania_flood/${model}/rcp6p0/2030-2069/inun_dynRout_RP_${return}_bias_corr_masked_Tanzania/inun_dynRout_RP_${return}_bias_corr_contour_Tanzania.tif \
#     -f "ESRI Shapefile" \
#     data/tanzania_flood/${model}_${return}_vector.shp

# ogr2ogr \
#     -a_srs "EPSG:4326" \
#     -where "DN > 0" \
#     data/tanzania_flood/${model}_${return}_filtered.shp \
#     data/tanzania_flood/${model}_${return}_vector.shp

# rm data/tanzania_flood/${model}_${return}_vector.shp

# done
# done

# Convert SSBN models
ssbn_return_periods=(5 10 20 50 75 100 200 250 500 1000)

for return in ${ssbn_return_periods[@]}
do
echo "SSBN_${return}"

gdal_polygonize.py \
    data/tanzania_flood/SSBN_flood_data/TZ_fluvial_defended/TZ-FD-${return}-1.tif \
    -f "ESRI Shapefile" \
    data/tanzania_flood/SSBN_${return}_vector.shp

ogr2ogr \
    -a_srs "EPSG:4326" \
    -where "DN > 0" \
    data/tanzania_flood/SSBN_${return}_filtered.shp \
    data/tanzania_flood/SSBN_${return}_vector.shp

rm data/tanzania_flood/SSBN_${return}_vector.shp

done