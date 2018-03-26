"""Intersect hazard bands with networks

Output rows like:
- network_element_type (node/edge)
- sector (road/rail/port/airport)
- id
- model
- rp
- band
- upper
- lower
"""
import os

import fiona
import shapely.geometry

def main():
    for sector, node_or_edge, path in get_network_details():
        with fiona.open(path) as network:
            intersect_euwatch(sector, node_or_edge, network)
            intersect_glofris(sector, node_or_edge, network)


def get_network_details():
    base_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'data', 'Infrastructure'
    )
    return [
        (
            'airport',
            'node',
            os.path.join(
                base_path,
                'Airports',
                'airport_shapefiles',
                'tz_od_airport_nodes.shp')
        ),
        (
            'port',
            'node',
            os.path.join(
                base_path,
                'Ports',
                'port_shapefiles',
                'tz_port_nodes.shp'),
        ),
        (
            'rail',
            'node',
            os.path.join(
                base_path,
                'Railways',
                'railway_shapefiles',
                'tanzania-rail-nodes-processed.shp'),
        ),
        (
            'rail',
            'edge',
            os.path.join(
                base_path,
                'Railways',
                'railway_shapefiles',
                'tanzania-rail-ways-processed.shp'),
        ),
        (
            'road',
            'node',
            os.path.join(
                base_path,
                'Roads',
                'road_shapefiles',
                'tanroads_nodes_main_all_2017_adj.shp'),
        ),
        (
            'road',
            'edge',
            os.path.join(
                base_path,
                'Roads',
                'road_shapefiles',
                'tanroads_main_all_2017_adj.shp'),
        )
    ]


def intersect_euwatch(sector, node_or_edge, network):
    hazard_path = os.path.join(
        os.path.dirname(__file__), '..', 'data',
        'tanzania_flood', 'hazard_bands_euwatch.shp')
    intersect_network(sector, node_or_edge, network, hazard_path)


def intersect_glofris(sector, node_or_edge, network):
    hazard_path = os.path.join(
        os.path.dirname(__file__), '..', 'data',
        'tanzania_flood', 'hazard_bands_glofris.shp')
    intersect_network(sector, node_or_edge, network, hazard_path)


def intersect_network(sector, node_or_edge, network, hazard_path):
    id_key = get_id_key_for_sector(sector)

    with fiona.open(hazard_path) as hazard_bands:
        for band in hazard_bands:
            if 'geometry' not in band or band['geometry'] is None:
                continue
            band_shape = shapely.geometry.shape(band['geometry'])
            if band_shape.is_empty:
                continue
            if not band_shape.is_valid:
                band_shape = band_shape.buffer(0)

            model = band['properties']['model']
            rp = band['properties']['r_period']
            threshold = band['properties']['threshold']
            upper = band['properties']['upper']
            lower = band['properties']['lower']

            for element in network:
                el_shape = shapely.geometry.shape(element['geometry'])
                if el_shape.intersects(band_shape):
                    el_id = element['properties'][id_key]
                    print(",".join([
                        node_or_edge,
                        sector,
                        str(el_id),
                        model,
                        str(rp),
                        threshold,
                        str(upper),
                        str(lower)
                    ]))

def get_id_key_for_sector(sector):
    lu = {
        'road': 'gid',
        'rail': 'id',
        'port': 'id',
        'airport': 'ident'
    }
    return lu[sector]

if __name__ == '__main__':
    main()
