data/tanzania-latest.osm.pbf:
	wget http://download.geofabrik.de/africa/tanzania-latest.osm.pbf && \
	mv tantanzania-latest.osm.pbf data/

data/Infrastructure/Railways/tanzania-rail-nodes.osm.pbf: data/tanzania-latest.osm.pbf
	# Extract railway nodes (not crossings) from OSM
	rm -f data/Infrastructure/Railways/tanzania-rail-nodes.osm.pbf && \
	osmium tags-filter data/tanzania-latest.osm.pbf n/railway!=*crossing \
	-o data/Infrastructure/Railways/tanzania-rail-nodes.osm.pbf

data/Infrastructure/Railways/tanzania-rail-nodes.geojson: data/Infrastructure/Railways/tanzania-rail-nodes.osm.pbf
	OSM_CONFIG_FILE=scripts/osmconf.ini ogr2ogr -f GeoJSON data/Infrastructure/Railways/tanzania-rail-nodes.geojson \
	data/Infrastructure/Railways/tanzania-rail-nodes.osm.pbf \
	layer points

data/Infrastructure/Railways/tanzania-rail-ways.osm.pbf: data/tanzania-latest.osm.pbf
	# Extract railway ways from OSM
	rm -f data/Infrastructure/Railways/tanzania-rail-ways.osm.pbf && \
	osmium tags-filter data/tanzania-latest.osm.pbf w/railway \
	-o data/Infrastructure/Railways/tanzania-rail-ways.osm.pbf

data/Infrastructure/Railways/tanzania-rail-ways.geojson: data/Infrastructure/Railways/tanzania-rail-ways.osm.pbf
	OSM_CONFIG_FILE=scripts/osmconf.ini ogr2ogr -f GeoJSON data/Infrastructure/Railways/tanzania-rail-ways.geojson \
	data/Infrastructure/Railways/tanzania-rail-ways.osm.pbf \
	layer lines

data/Infrastructure/Railways/tanzania-rail-nodes-processed.geojson: data/Infrastructure/Railways/tanzania-rail-ways.geojson data/Infrastructure/Railways/tanzania-rail-nodes.geojson
	# Process OSM rail to network representation
	python scripts/process_osm_rail.py

data/Infrastructure/Railways/tanzania-rail-nodes-processed.shp: data/Infrastructure/Railways/tanzania-rail-nodes-processed.geojson
	# Convert GeoJSON to shp
	ogr2ogr -f "ESRI Shapefile" \
		-sql 'SELECT name, id, osm_id, rail_node_type as node_type from "tanzania-rail-nodes-processed"' \
		tanzania-rail-nodes-processed.shp tanzania-rail-nodes-processed.geojson \
	ogr2ogr -f "ESRI Shapefile" \
		tanzania-rail-ways-processed.shp tanzania-rail-ways-processed.geojson

.PHONY: all clean
all: data/Infrastructure/Railways/tanzania-rail-nodes-processed.shp
	# all: make complete

clean:
	rm figures/*
	rm outputs/*
	# clean: make complete
