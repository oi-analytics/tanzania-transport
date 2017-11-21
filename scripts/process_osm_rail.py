"""Process OSM rail to network representation
- filter out service=siding,sid,yard,crossover (from ways)
- filter out railway=residential,residdential,tram,station (from ways)
- split ways on junctions and at stations
- match station names to canonical set
"""
import os

import fiona
from fiona.crs import from_epsg
from rtree import index
import shapely.geometry
import shapely.ops

BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'Railway_data')

NODES_PATH = os.path.join(BASE_PATH, 'tanzania-rail-nodes.geojson')
WAYS_PATH = os.path.join(BASE_PATH, 'tanzania-rail-ways.geojson')

MAJOR_NODES_PATH = os.path.join(BASE_PATH, 'transcribed', 'TZ_railways_map_nodes.csv')
MAJOR_WAYS_PATH = os.path.join(BASE_PATH, 'transcribed', 'TZ_railways_map_edges.csv')

NODES_OUTPUT_PATH = os.path.join(BASE_PATH, 'tanzania-rail-nodes-processed.geojson')
WAYS_OUTPUT_PATH = os.path.join(BASE_PATH, 'tanzania-rail-ways-processed.geojson')


# Read nodes
OSM_NODES = {}
OSM_NODES_INDEX = index.Index()

with fiona.open(NODES_PATH) as fh:
    for i, record in enumerate(fh):
        if record['properties']['railway'] in ('subway_entrance', 'yes', 'buffer_stop'):
            continue
        geom = shapely.geometry.shape(record['geometry'])
        record['geom'] = geom
        OSM_NODES[i] = record
        OSM_NODES_INDEX.insert(i, geom.bounds)
print("Nodes read", len(OSM_NODES))


# Read ways
OSM_WAYS = {}
OSM_WAYS_INDEX = index.Index()

with fiona.open(WAYS_PATH) as fh:
    for i, record in enumerate(fh):
        if record['properties']['service'] in ('siding', 'sid', 'yard', 'crossover'):
            continue
        if record['properties']['railway'] in ('residential', 'residdential', 'tram', 'station'):
            continue
        geom = shapely.geometry.shape(record['geometry'])
        record['geom'] = geom
        OSM_WAYS[i] = record
        OSM_WAYS_INDEX.insert(i, geom.bounds)
print("Ways read", len(OSM_WAYS))


# Split ways at junctions
MAX_J_SPLIT_WAYS_ID = 0
OSM_J_SPLIT_WAYS = {}
OSM_J_SPLIT_WAYS_INDEX = index.Index()
for i, way in OSM_WAYS.items():
    check_ids = list(OSM_WAYS_INDEX.intersection(way['geom'].bounds))
    hits = []

    for other_i in check_ids:
        if i == other_i:
            continue

        other_way = OSM_WAYS[other_i]
        intersection = way['geom'].intersection(other_way['geom'])

        if not intersection:
            continue
        elif intersection.geometryType() == 'Point':
            hits.append(intersection)
        elif intersection.geometryType() == 'MultiPoint':
            hits.extend(point for point in intersection)
        elif intersection.geometryType() == 'GeometryCollection':
            hits.extend(geom for geom in list(intersection) if geom.geometryType() == 'Point')
        else:
            print(way)
            print(other_way)
            print(intersection)
            exit()

    if hits:
        segments = shapely.ops.split(way['geom'], shapely.geometry.MultiPoint(hits))
    else:
        segments = [way['geom']]

    for segment in list(segments):
        OSM_J_SPLIT_WAYS[MAX_J_SPLIT_WAYS_ID] = {
            'type': 'Feature',
            'geom': segment,
            'geometry': shapely.geometry.mapping(segment),
            'properties': way['properties']
        }
        OSM_J_SPLIT_WAYS_INDEX.insert(MAX_J_SPLIT_WAYS_ID, segment.bounds)
        MAX_J_SPLIT_WAYS_ID += 1

print("Ways split at junctions", len(OSM_J_SPLIT_WAYS))


# Move stations to ways
OSM_W_NODES = {}
OSM_W_NODES_INDEX = index.Index()
for node_i, node in OSM_NODES.items():
    check_ids = list(OSM_J_SPLIT_WAYS_INDEX.nearest(node['geom'].bounds, 1))
    distances = {}
    for i in check_ids:
        way = OSM_J_SPLIT_WAYS[i]
        dist = way['geom'].distance(node['geom'])
        distances[dist] = i

    min_dist = min(distances.keys())
    way_i = distances[min_dist]
    way = OSM_J_SPLIT_WAYS[way_i]

    snap = way['geom'].interpolate(way['geom'].project(node['geom']))

    OSM_W_NODES[node_i] = {
        'type': 'Feature',
        'geom': snap,
        'geometry': shapely.geometry.mapping(snap),
        'properties': node['properties']
    }
    OSM_W_NODES_INDEX.insert(node_i, snap.bounds)
print("Nodes moved", len(OSM_W_NODES))


def split_line_with_point(line, point):
    distance_on_line = line.project(point)
    coords = list(line.coords)

    for j, p in enumerate(coords):
        pd = line.project(shapely.geometry.Point(p))
        if pd == distance_on_line:
            if j == 0 or j == len(coords) - 1:
                return [line]
            else:
                return [
                    shapely.geometry.LineString(coords[:j+1]),
                    shapely.geometry.LineString(coords[j:])
                ]
        elif distance_on_line < pd:
            cp = line.interpolate(distance_on_line)
            ls1_coords = coords[:j]
            ls1_coords.append(cp.coords[0])
            ls2_coords = [cp.coords[0]]
            ls2_coords.extend(coords[j:])
            return [shapely.geometry.LineString(ls1_coords), shapely.geometry.LineString(ls2_coords)]


# Split ways at stations
MAX_S_SPLIT_WAYS_ID = 0
OSM_S_SPLIT_WAYS = {}
OSM_S_SPLIT_WAYS_INDEX = index.Index()
for i, way in OSM_J_SPLIT_WAYS.items():
    check_ids = list(OSM_W_NODES_INDEX.intersection(way['geom'].bounds))
    hits = []

    for node_i in check_ids:
        node = OSM_W_NODES[node_i]
        intersection = way['geom'].intersection(node['geom'])

        if not intersection:
            intersection = way['geom'].intersection(node['geom'].buffer(0.0000000001))

        if not intersection:
            continue
        elif intersection.geometryType() == 'Point':
            hits.append(intersection)
        elif intersection.geometryType() == 'MultiPoint':
            hits.extend(point for point in intersection)
        elif intersection.geometryType() == 'LineString':
            start_point = shapely.geometry.Point(intersection.coords[0])
            hits.append(start_point)
        elif intersection.geometryType() == 'GeometryCollection':
            hits.extend(geom for geom in list(intersection) if geom.geometryType() == 'Point')
        else:
            print(way)
            print(node)
            print(intersection)
            exit()

    if hits:
        # segments = shapely.ops.split(way['geom'], shapely.geometry.MultiPoint(hits))
        line = way['geom']
        segments = [line]
        for hit in hits:
            new_segments = []
            for segment in filter(lambda x: not x.is_empty, segments):
                # add the newly split 2 lines or the same line if not split
                new_segments.extend(split_line_with_point(segment, hit))
                segments = new_segments
    else:
        segments = [way['geom']]

    for segment in list(segments):
        OSM_S_SPLIT_WAYS[MAX_S_SPLIT_WAYS_ID] = {
            'type': 'Feature',
            'geom': segment,
            'geometry': shapely.geometry.mapping(segment),
            'properties': way['properties']
        }
        OSM_S_SPLIT_WAYS_INDEX.insert(MAX_S_SPLIT_WAYS_ID, segment.bounds)
        MAX_S_SPLIT_WAYS_ID += 1

print("Ways split at stations", len(OSM_S_SPLIT_WAYS))



# Join ways if split at non-junction, non-station



# Create nodes at all end-points (junction, terminus)



# Write all
if os.path.exists(WAYS_OUTPUT_PATH):
    os.remove(WAYS_OUTPUT_PATH)

with fiona.open(WAYS_OUTPUT_PATH, 'w',
            driver="GeoJSON",
            schema={
                'geometry': 'LineString',
                'properties': {
                    'name': 'str',
                    'osm_id': 'str'
                }
            },
            crs=from_epsg(4326)) as sink:
    for feature in OSM_S_SPLIT_WAYS.values():
        feature['properties'] = {
            'name': feature['properties']['name'],
            'osm_id': feature['properties']['osm_id']
        }
        sink.write(feature)

if os.path.exists(NODES_OUTPUT_PATH):
    os.remove(NODES_OUTPUT_PATH)
with fiona.open(NODES_OUTPUT_PATH, 'w',
            driver="GeoJSON",
            schema={
                'geometry': 'Point',
                'properties': {
                    'name': 'str',
                    'osm_id': 'str'
                }
            },
            crs=from_epsg(4326)) as sink:
    for feature in OSM_W_NODES.values():
        feature['properties'] = {
            'name': feature['properties']['name'],
            'osm_id': feature['properties']['osm_id']
        }
        sink.write(feature)