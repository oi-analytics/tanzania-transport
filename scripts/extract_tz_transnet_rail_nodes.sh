# Extract nodes from Railway lines

rm -f data/Railway_data/rail-start-points.*
rm -f data/Railway_data/rail-end-points.*

ogr2ogr \
    -a_srs "EPSG:3857" \
    -f "ESRI Shapefile" -dialect sqlite data/Railway_data/rail-start-points.shp \
    -sql "select ST_StartPoint(geometry), From_ as name, osm_id from TZ_TransNet_Railroads" \
    data/Railway_data/TZ_TransNet_Railroads.shp

ogr2ogr \
    -a_srs "EPSG:3857" \
    -f "ESRI Shapefile" -dialect sqlite data/Railway_data/rail-end-points.shp \
    -sql "select ST_EndPoint(geometry), \"To\" as name, osm_id from TZ_TransNet_Railroads" \
    data/Railway_data/TZ_TransNet_Railroads.shp