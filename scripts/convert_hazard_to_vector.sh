return_periods=(00002 00005 00025 00050 00100 00250 00500 01000)

# Convert EUWATCH observations
for return in ${return_periods[@]}
do
echo "EUWATCH_${return}"

gdal_calc.py \
    -A data/tanzania_flood/EUWATCH/inun_dynRout_RP_${return}_Tanzania/inun_dynRout_RP_${return}_contour_Tanzania.tif  \
    --outfile=data/tanzania_flood/EUWATCH_${return}_mask-0.25.tif \
    --calc="(A>0.25)" \
    --type=Byte --NoDataValue=0 \
    --co="SPARSE_OK=YES" \
    --co="NBITS=1" \
    --quiet
    # Could enable compression
    # --co="COMPRESS=LZW"

gdal_polygonize.py \
    data/tanzania_flood/EUWATCH_${return}_mask-0.25.tif \
    -q \
    -f "ESRI Shapefile" \
    data/tanzania_flood/EUWATCH_${return}_vector_mask.shp

ogr2ogr \
    -a_srs "EPSG:4326" \
    data/tanzania_flood/EUWATCH_${return}_mask-0.25.shp \
    data/tanzania_flood/EUWATCH_${return}_vector_mask.shp

rm data/tanzania_flood/EUWATCH_${return}_vector_mask.*
done

# Convert models
models=(GFDL-ESM2M HadGEM2-ES IPSL-CM5A-LR MIROC-ESM-CHEM NorESM1-M)

for model in ${models[@]}
do
for return in ${return_periods[@]}
do
echo ${model}_${return}

gdal_calc.py \
    -A data/tanzania_flood/${model}/rcp6p0/2030-2069/inun_dynRout_RP_${return}_bias_corr_masked_Tanzania/inun_dynRout_RP_${return}_bias_corr_contour_Tanzania.tif  \
    --outfile=data/tanzania_flood/${model}_${return}_mask-0.25.tif \
    --calc="(A>0.25)" \
    --type=Byte --NoDataValue=0 \
    --co="SPARSE_OK=YES" \
    --co="NBITS=1" \
    --quiet
    # Could enable compression
    # --co="COMPRESS=LZW"

gdal_polygonize.py \
    data/tanzania_flood/${model}_${return}_mask-0.25.tif \
    -q \
    -f "ESRI Shapefile" \
    data/tanzania_flood/${model}_${return}_vector_mask.shp

ogr2ogr \
    -a_srs "EPSG:4326" \
    data/tanzania_flood/${model}_${return}_mask-0.25.shp \
    data/tanzania_flood/${model}_${return}_vector_mask.shp

rm data/tanzania_flood/${model}_${return}_vector_mask.*

done
done

# Convert SSBN models
ssbn_return_periods=(5 10 20 50 75 100 200 250 500 1000)

declare -A models
models=(
    ["TZ_fluvial_defended"]="FD"
    ["TZ_fluvial_undefended"]="FU"
    ["TZ_pluvial_defended"]="PD"
    ["TZ_pluvial_undefended"]="PU"
    ["TZ_urban_defended"]="UD"
    ["TZ_urban_undefended"]="UU"
)

for model in ${!models[@]}
do
for return in ${ssbn_return_periods[@]}
do
abbr=${models[${model}]}
echo "SSBN_${abbr}_${return}"

gdal_calc.py \
    -A data/tanzania_flood/SSBN_flood_data/${model}/TZ-${abbr}-${return}-1.tif \
    --outfile=data/tanzania_flood/SSBN_${abbr}_${return}_mask-0.25.tif \
    --calc="(A>0.25)" \
    --type=Byte --NoDataValue=0 \
    --co="SPARSE_OK=YES" \
    --co="NBITS=1" \
    --quiet
    # Could enable compression
    # --co="COMPRESS=LZW"

gdal_polygonize.py \
    -8 \  # use 8-connectedness
    data/tanzania_flood/SSBN_${abbr}_${return}_mask-0.25.tif \
    -q \
    -f "ESRI Shapefile" \
    data/tanzania_flood/SSBN_${abbr}_${return}_vector_mask.shp

ogr2ogr \
    -a_srs "EPSG:4326" \
    data/tanzania_flood/SSBN_${abbr}_${return}_mask-0.25.shp \
    data/tanzania_flood/SSBN_${abbr}_${return}_vector_mask.shp

rm data/tanzania_flood/SSBN_${abbr}_${return}_vector_mask.*

done
done
