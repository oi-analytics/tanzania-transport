data/Railway_data/tanzania-rail-nodes.osm.pbf: data/tanzania-latest.osm.pbf
	# Extract railway nodes (not crossings) from OSM
	rm -f data/Railway_data/tanzania-rail-nodes.osm.pbf && \
	osmium tags-filter data/tanzania-latest.osm.pbf n/railway!=*crossing \
	-o data/Railway_data/tanzania-rail-nodes.osm.pbf

data/Railway_data/tanzania-rail-nodes.geojson: data/Railway_data/tanzania-rail-nodes.osm.pbf
	OSM_CONFIG_FILE=scripts/osmconf.ini ogr2ogr -f GeoJSON data/Railway_data/tanzania-rail-nodes.geojson \
	data/Railway_data/tanzania-rail-nodes.osm.pbf \
	layer points

data/Railway_data/tanzania-rail-ways.osm.pbf: data/tanzania-latest.osm.pbf
	# Extract railway ways from OSM
	rm -f data/Railway_data/tanzania-rail-ways.osm.pbf && \
	osmium tags-filter data/tanzania-latest.osm.pbf w/railway \
	-o data/Railway_data/tanzania-rail-ways.osm.pbf

data/Railway_data/tanzania-rail-ways.geojson: data/Railway_data/tanzania-rail-ways.osm.pbf
	OSM_CONFIG_FILE=scripts/osmconf.ini ogr2ogr -f GeoJSON data/Railway_data/tanzania-rail-ways.geojson \
	data/Railway_data/tanzania-rail-ways.osm.pbf \
	layer lines

data/Railway_data/tanzania-rail.txt: data/Railway_data/tanzania-rail-ways.geojson data/Railway_data/tanzania-rail-nodes.geojson
	# Process OSM rail to network representation
	python scripts/process_osm_rail.py


.PHONY: all clean
all:
	# all: make complete

clean:
	rm figures/*
	rm outputs/*
	# clean: make complete
