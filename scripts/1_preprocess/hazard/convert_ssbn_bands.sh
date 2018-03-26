#!/bin/bash

# To run with GNU Parallel:
# cat args.txt | parallel ./convert_ssbn_bands.sh {} {} {} {} {}
# where args.txt has lines like "<lower> <upper> <model> <rp>"


if [ "$#" -eq 0 ];
then
    echo "Usage ./convert_ssbn_bands.sh <lower> <upper> <model> <abbr> <rp>"
    exit
fi

lower=$1
upper=$2
model=$3
abbr=$4
rp=$5

echo "SSBN ${model} ${abbr} ${rp} ${lower} ${upper}"

gdal_calc.py \
    -A data/tanzania_flood/SSBN_flood_data/${model}/TZ-${abbr}-${rp}-1.tif \
    --outfile=data/tanzania_flood/SSBN_${abbr}_${rp}_tmp_${lower}-${upper}.tif \
    --calc="(A>${lower}) & (A<=${upper})" \
    --type=Byte --NoDataValue=0 \
    --co="SPARSE_OK=YES" \
    --co="NBITS=1" \
    --quiet
    # Could enable compression
    # --co="COMPRESS=LZW"

# -8 means use 8-connectedness
gdal_polygonize.py \
    -8 \
    data/tanzania_flood/SSBN_${abbr}_${rp}_tmp_${lower}-${upper}.tif \
    -q \
    -f "ESRI Shapefile" \
    data/tanzania_flood/SSBN_${abbr}_${rp}_tmp_${lower}-${upper}.shp

ogr2ogr \
    -a_srs "EPSG:4326" \
    data/tanzania_flood/SSBN_${abbr}_${rp}_${lower}-${upper}.shp \
    data/tanzania_flood/SSBN_${abbr}_${rp}_tmp_${lower}-${upper}.shp

rm data/tanzania_flood/SSBN_${abbr}_${rp}_tmp_${lower}-${upper}.*
