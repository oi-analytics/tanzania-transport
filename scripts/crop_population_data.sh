# Crop/clip data to Mwanza regions for population_roads map

# population raster
gdal_translate -projwin 32.5 -2.3 33.6 -3.3 \
    data/Population_data/TZA_popmap15adj_v2b.tif \
    data/Population_data/TZA_popmap15adj_v2b_mwanza.tif

# road vectors
rm data/Road_data/*_mwanza*
ogr2ogr -s_srs "EPSG:3857" -t_srs "EPSG:4326" \
    data/Road_data/TZ_TransNet_Roads_4326.shp \
    data/Road_data/TZ_TransNet_Roads.shp

ogr2ogr -clipsrc 32.5 -3.3 33.6 -2.3 \
    data/Road_data/gis.osm_roads_free_1_mwanza.shp \
    data/Road_data/gis.osm_roads_free_1.shp

ogr2ogr -clipsrc 32.5 -3.3 33.6 -2.3 \
    data/Road_data/PMO_Tanroads_mwanza.shp \
    data/Road_data/PMO_Tanroads.shp

ogr2ogr -clipsrc 32.5 -3.3 33.6 -2.3 \
    data/Road_data/TZ_TransNet_Roads_mwanza.shp \
    data/Road_data/TZ_TransNet_Roads_4326.shp
