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



def main():
    """Process OSM rail stations and lines
    """
    nodes, node_index = read_nodes()
    print("Nodes read", len(nodes))

    ways, way_index = read_ways()
    print("Ways read", len(ways))

    ways, way_index = split_ways_at_junctions(ways, way_index)
    print("Ways split at junctions", len(ways))

    nodes, node_index = move_nodes_to_ways(nodes, ways, way_index)
    print("Nodes moved", len(nodes))

    ways, way_index = split_ways_at_stations(nodes, node_index, ways)
    print("Ways split at stations", len(ways))

    ways, way_index = join_ways(nodes, node_index, ways, way_index)
    nodes, node_index = create_nodes_at_endpoints(nodes, node_index, ways, way_index)
    nodes, ways = clean_network(nodes, node_index, ways, way_index)
    write_all(nodes, NODES_OUTPUT_PATH, ways, WAYS_OUTPUT_PATH)


def read_nodes():
    """Read all nodes
    """
    nodes = {}
    node_index = index.Index()
    with fiona.open(NODES_PATH) as source:
        for i, record in enumerate(source):
            if record['properties']['railway'] in ('subway_entrance', 'yes', 'buffer_stop'):
                continue
            geom = shapely.geometry.shape(record['geometry'])
            record['geom'] = geom
            nodes[i] = record
            node_index.insert(i, geom.bounds)
    return nodes, node_index


def read_ways():
    """Read all ways
    """
    ways = {}
    way_index = index.Index()
    with fiona.open(WAYS_PATH) as source:
        for i, record in enumerate(source):
            if record['properties']['service'] in ('siding', 'sid', 'yard', 'crossover'):
                continue
            if record['properties']['railway'] in ('residential', 'residdential',
                                                   'tram', 'station'):
                continue
            geom = shapely.geometry.shape(record['geometry'])
            record['geom'] = geom
            ways[i] = record
            way_index.insert(i, geom.bounds)
    return ways, way_index


def split_ways_at_junctions(ways, way_index):
    """Split all ways at junction intersections
    """
    max_id = 0
    split_ways = {}
    split_ways_index = index.Index()
    for i, way in ways.items():
        check_ids = list(way_index.intersection(way['geom'].bounds))
        hits = []

        for other_i in check_ids:
            if i == other_i:
                continue

            other_way = ways[other_i]
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
            split_ways[max_id] = {
                'type': 'Feature',
                'geom': segment,
                'geometry': shapely.geometry.mapping(segment),
                'properties': way['properties']
            }
            split_ways_index.insert(max_id, segment.bounds)
            max_id += 1
    return split_ways, split_ways_index


def move_nodes_to_ways(nodes, ways, way_index):
    """Move station nodes to intersect with their nearest line
    """
    moved_nodes = {}
    moved_nodes_index = index.Index()
    for node_i, node in nodes.items():
        check_ids = list(way_index.nearest(node['geom'].bounds, 1))
        distances = {}
        for i in check_ids:
            way = ways[i]
            dist = way['geom'].distance(node['geom'])
            distances[dist] = i

        min_dist = min(distances.keys())
        way_i = distances[min_dist]
        way = ways[way_i]

        snap = way['geom'].interpolate(way['geom'].project(node['geom']))

        moved_nodes[node_i] = {
            'type': 'Feature',
            'geom': snap,
            'geometry': shapely.geometry.mapping(snap),
            'properties': node['properties']
        }
        moved_nodes_index.insert(node_i, snap.bounds)
    return moved_nodes, moved_nodes_index


def split_line_with_point(line, point):
    """Split a line using a point

    - code directly similar to shapely.ops.split, with checks removed so that
    line must be split even if point doesn't intersect.
    """
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
            return [
                shapely.geometry.LineString(ls1_coords),
                shapely.geometry.LineString(ls2_coords)
            ]


def split_ways_at_stations(nodes, node_index, ways):
    """Split all ways at station nodes
    """
    max_id = 0
    split_ways = {}
    split_ways_index = index.Index()
    for i, way in ways.items():
        check_ids = list(node_index.intersection(way['geom'].bounds))
        hits = []

        for node_i in check_ids:
            node = nodes[node_i]
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
                print("Unhandled intersection type:")
                print(way)
                print(node)
                print(intersection)
                exit()

        segments = [way['geom']]
        if hits:
            # segments = shapely.ops.split(way['geom'], shapely.geometry.MultiPoint(hits))
            for hit in hits:
                new_segments = []
                for segment in filter(lambda x: not x.is_empty, segments):
                    # add the newly split 2 lines or the same line if not split
                    new_segments.extend(split_line_with_point(segment, hit))
                    segments = new_segments

        for segment in list(segments):
            split_ways[max_id] = {
                'type': 'Feature',
                'geom': segment,
                'geometry': shapely.geometry.mapping(segment),
                'properties': way['properties']
            }
            split_ways_index.insert(max_id, segment.bounds)
            max_id += 1
    return split_ways, split_ways_index


def line_endpoints(line):
    start = shapely.geometry.Point(line.coords[0])
    end = shapely.geometry.Point(line.coords[-1])
    return start, end


def other_end(line, point):
    start, end = line_endpoints(line)
    if start.equals(point):
        return end
    if end.equals(point):
        return start


def join_ways(nodes, node_index, ways, way_index):
    """Join ways if split at non-junction, non-station
    """
    return ways, way_index

    max_id = 0
    joined_ways = {}
    joined_way_index = index.Index()
    considered = set()
    for way_i, way in ways.items():
        if way_i in considered:
            continue
        start, end = line_endpoints(way['geom'])
    # return joined_ways, joined_ways_index


def create_nodes_at_endpoints(nodes, node_index, ways, way_index):
    """Ensure that network is topologically complete with nodes at endpoints
    """
    return nodes, node_index


def clean_network(nodes, node_index, ways, way_index):
    """Clean network properties
    - map node names to canonical station names
    - add endpoint references to edges
    """
    return nodes, ways


def write_all(nodes, node_path, ways, way_path):
    """Write all data to output files
    """
    if os.path.exists(way_path):
        os.remove(way_path)

    with fiona.open(way_path, 'w',
                    driver="GeoJSON",
                    schema={
                        'geometry': 'LineString',
                        'properties': {
                            'name': 'str',
                            'osm_id': 'str'
                        }
                    },
                    crs=from_epsg(4326)) as sink:
        for feature in ways.values():
            feature['properties'] = {
                'name': feature['properties']['name'],
                'osm_id': feature['properties']['osm_id']
            }
            sink.write(feature)

    if os.path.exists(node_path):
        os.remove(node_path)
    with fiona.open(node_path, 'w',
                    driver="GeoJSON",
                    schema={
                        'geometry': 'Point',
                        'properties': {
                            'name': 'str',
                            'osm_id': 'str'
                        }
                    },
                    crs=from_epsg(4326)) as sink:
        for feature in nodes.values():
            feature['properties'] = {
                'name': feature['properties']['name'],
                'osm_id': feature['properties']['osm_id']
            }
            sink.write(feature)

if __name__ == '__main__':
    main()
