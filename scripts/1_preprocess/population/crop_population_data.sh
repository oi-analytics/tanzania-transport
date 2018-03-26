# Crop/clip data to Mwanza regions for population_roads map

# population raster
gdal_translate -projwin 32.5 -2.3 33.6 -3.3 \
    data/Infrastructure/Population/TZA_popmap15adj_v2b.tif \
    data/Infrastructure/Population/TZA_popmap15adj_v2b_mwanza.tif

# road vectors
rm data/Infrastructure/Roads/*_mwanza*
ogr2ogr -s_srs "EPSG:3857" -t_srs "EPSG:4326" \
    data/Infrastructure/Roads/TZ_TransNet_Roads_4326.shp \
    data/Infrastructure/Roads/TZ_TransNet_Roads.shp

ogr2ogr -clipsrc 32.5 -3.3 33.6 -2.3 \
    data/Infrastructure/Roads/gis.osm_roads_free_1_mwanza.shp \
    data/Infrastructure/Roads/gis.osm_roads_free_1.shp

ogr2ogr -clipsrc 32.5 -3.3 33.6 -2.3 \
    data/Infrastructure/Roads/PMO_Tanroads_mwanza.shp \
    data/Infrastructure/Roads/PMO_Tanroads.shp

ogr2ogr -clipsrc 32.5 -3.3 33.6 -2.3 \
    data/Infrastructure/Roads/TZ_TransNet_Roads_mwanza.shp \
    data/Infrastructure/Roads/TZ_TransNet_Roads_4326.shp
