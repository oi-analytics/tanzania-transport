# Resample population raster, picking max values
gdalwarp \
  -tr 0.008333 0.008333 \
  -r max \
  ../data/Infrastructure/Population/TZA_popmap15adj_v2b.tif \
  ../data/Infrastructure/Population/TZA_popmap15adj_v2b_resampled.tif
