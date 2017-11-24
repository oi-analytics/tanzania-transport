"""Use converted hazard threshold outlines to intersect transport networks
"""
import csv
import os.path

import fiona
import shapely.geometry
from rtree import index

from utils import line_length


def main():
    """Read hazards and transport networks, output exposure for each model/return
    """
    # Input data
    base_path = os.path.join(os.path.dirname(__file__), '..')
    data_path = os.path.join(base_path, 'data')
    inf_path = os.path.join(data_path, 'Infrastructure')

    # Roads
    trunk_road_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'trunk_roads_2017.shp')
    regional_road_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'region_roads_2017.shp')

    # Railways
    railway_nodes_filename = os.path.join(inf_path, 'Railways', 'tanzania-rail-nodes-processed.shp')
    railway_ways_filename = os.path.join(inf_path, 'Railways', 'tanzania-rail-ways-processed.shp')

    # Ports
    ports_filename = os.path.join(inf_path, 'Ports', 'TZ_ports.csv')

    # Airports
    airport_filename = os.path.join(inf_path, 'Airports', 'TZ_airport_node_flows.csv')

    # Hazards
    hazard_path = os.path.join(data_path, 'tanzania_flood')
    all_hazard_details = get_hazard_details(hazard_path)

    # filter while testing
    hazard_details = all_hazard_details[:9]

    for j, hazard_detail in enumerate(hazard_details):
        if j != 4:
            continue
        print(hazard_detail)
        hazards, hazard_index = read_hazard(hazard_detail)
        for i, road in enumerate(roads(trunk_road_filename, regional_road_filename)):
            if i != 587:
                continue
            to_check = hazard_index.intersection(road['geom'].bounds)
            exposed_segments = []
            exposed_length = 0
            for fid in to_check:
                if fid != 726:
                    continue
                hazard = hazards[fid]
                # print(road)
                print(hazard)
                intersection = road['geom'].intersection(hazard['geom'])
                if intersection:
                    exposed_length += line_length(intersection)
                    exposed_segments.append(intersection)

            props = road['properties']
            name = "{}-{}".format(props['STARTENAME'], props['ENDNOENAME'])
            if exposed_length:
                print(name, exposed_length)


def read_hazard(detail):
    """Read hazards into dict and rtree index
    """
    hazard_index = index.Index()
    hazards = {}
    with fiona.open(detail['filename']) as records:
        for i, record in enumerate(records):
            hazards[i] = record
            record['geom'] = shapely.geometry.shape(record['geometry'])
            hazard_index.insert(i, record['geom'].bounds)
    return hazards, hazard_index


def get_hazard_details(hazard_path):
    """Get list of {model, return, filename} dicts for hazard scenarios
    """
    glofris_models = [
        'EUWATCH',
        'GFDL-ESM2M',
        'HadGEM2-ES',
        'IPSL-CM5A-LR',
        'MIROC-ESM-CHEM',
        'NorESM1-M',
    ]
    glofris_return_periods = [
        '00002',  # not in SSBN
        '00005',
        '00025',  # not in SSBN
        '00050',
        '00100',
        '00250',
        '00500',
        '01000',
    ]
    glofris_hazard_details = [
        {
            'model': model,
            'return': return_period,
            'filename': os.path.join(hazard_path, '{}_{}_mask-0.25.shp'.format(model, return_period))
        }
        for model in glofris_models
        for return_period in glofris_return_periods
    ]
    ssbn_models = [
        'SSBN_FD',  # TZ_fluvial_defended
        'SSBN_FU',  # TZ_fluvial_undefended
        'SSBN_PD',  # TZ_pluvial_defended
        'SSBN_PU',  # TZ_pluvial_undefended
        'SSBN_UD',  # TZ_urban_defended
        'SSBN_UU',  # TZ_urban_undefended
    ]
    ssbn_return_periods = [
        '5',
        '10',  # not in GLOFRIS
        '20',  # not in GLOFRIS
        '50',
        '75',  # not in GLOFRIS
        '100',
        '200',  # not in GLOFRIS
        '250',
        '500',
        '1000',
    ]
    ssbn_hazard_details = [
        {
            'model': model,
            'return': return_period,
            'filename': os.path.join(hazard_path, '{}_{}_mask-0.25.shp'.format(model, return_period))
        }
        for model in ssbn_models
        for return_period in ssbn_return_periods
    ]

    return glofris_hazard_details + ssbn_hazard_details


def roads(trunk_road_filename, regional_road_filename):
    """Generate road features
    """
    with fiona.open(trunk_road_filename) as records:
        for record in records:
            record['geom'] = shapely.geometry.shape(record['geometry'])
            yield record
    with fiona.open(regional_road_filename) as records:
        for record in records:
            record['geom'] = shapely.geometry.shape(record['geometry'])
            yield record


def rail_ways(railway_ways_filename):
    """Generate rail ways
    """
    with fiona.open(railway_ways_filename) as records:
        for record in records:
            record['geom'] = shapely.geometry.shape(record['geometry'])
            yield record


def rail_stations(railway_nodes_filename):
    """Generate rail stations
    """
    with fiona.open(railway_nodes_filename) as records:
        for record in records:
            record['geom'] = shapely.geometry.shape(record['geometry'])
            yield record


def ports(ports_filename):
    """Generate ports
    """
    with open(ports_filename) as source:
        reader = csv.DictReader(source)
        for record in reader:
            record['geom'] = shapely.geometry.Point(record['longitude_deg'], record['latitude_deg'])
            yield record


def airports(airports_filename):
    """Generate airports
    """
    with open(airports_filename) as source:
        reader = csv.DictReader(source)
        for record in reader:
            record['geom'] = shapely.geometry.Point(record['longitude'], record['latitude'])
            yield record


if __name__ == '__main__':
    main()

