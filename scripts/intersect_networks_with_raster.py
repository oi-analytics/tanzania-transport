"""Intersect hazard bands with networks

Output rows like:
- network_element_type (node/edge)
- sector (road/rail/port/airport)
- id
- model
- rp
- point_val

or instead of point values:
- band
- upper
- lower
"""
import os

import fiona
import numpy as np
import rasterio
import rasterio.features
import shapely.geometry


def main():
    for network_details in get_network_details():
        with fiona.open(network_details['path']) as network:
            for hazard_details in get_hazard_details():
                if network_details['node_or_edge'] == 'edge':
                    intersect_network_edges(network, network_details, hazard_details)
                else:
                    intersect_network_points(network, network_details, hazard_details)


def intersect_network_edges(network, network_details, hazard_details):
    sector = network_details['sector']
    node_or_edge = network_details['node_or_edge']
    id_key = get_id_key_for_sector(sector)

    hazard_path = hazard_details['path']
    model = hazard_details['model']
    rp = hazard_details['r_period']

    with rasterio.open(hazard_path) as dataset:
        raster_band = dataset.read(1)
        for element in network:
            edge = shapely.geometry.shape(element['geometry'])
            rv_array = rasterize_geom(edge, dataset)

            max_val = np.max(rv_array * raster_band)

            if max_val > 0.25:
                el_id = element['properties'][id_key]
                print(",".join([
                    node_or_edge,
                    sector,
                    str(el_id),
                    model,
                    str(int(rp)),
                    str(max_val)
                ]))

def rasterize_geom(geom, like, all_touched=False):
    """Convert geom to mask array
    inspiration from https://github.com/perrygeo/python-rasterstats
    """
    geoms = [(geom, 1)]
    rv_array = rasterio.features.rasterize(
        geoms,
        out_shape=like.shape,
        transform=like.affine,
        fill=0,
        all_touched=all_touched)
    return rv_array

def intersect_network_points(network, network_details, hazard_details):
    sector = network_details['sector']
    node_or_edge = network_details['node_or_edge']
    id_key = get_id_key_for_sector(sector)

    hazard_path = hazard_details['path']
    model = hazard_details['model']
    rp = hazard_details['r_period']

    with rasterio.open(hazard_path) as dataset:
        raster_band = dataset.read(1)
        for element in network:
            point = shapely.geometry.shape(element['geometry'])
            row, col = dataset.index(point.x, point.y)

            try:
                point_val = raster_band[row, col]
            except IndexError:
                continue

            if point_val > 0.25:
                el_id = element['properties'][id_key]
                print(",".join([
                    node_or_edge,
                    sector,
                    str(el_id),
                    model,
                    str(rp),
                    str(point_val)
                ]))


def get_network_details():
    base_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'data', 'Infrastructure'
    )
    return [
        {
            'sector': 'airport',
            'node_or_edge': 'node',
            'path': os.path.join(
                base_path,
                'Airports',
                'airport_shapefiles',
                'tz_od_airport_nodes.shp')
        },
        {
            'sector': 'port',
            'node_or_edge': 'node',
            'path': os.path.join(
                base_path,
                'Ports',
                'port_shapefiles',
                'tz_port_nodes.shp'),
        },
        {
            'sector': 'rail',
            'node_or_edge': 'node',
            'path': os.path.join(
                base_path,
                'Railways',
                'railway_shapefiles',
                'tanzania-rail-nodes-processed.shp'),
        },
        {
            'sector': 'rail',
            'node_or_edge': 'edge',
            'path': os.path.join(
                base_path,
                'Railways',
                'railway_shapefiles',
                'tanzania-rail-ways-processed.shp'),
        },
        {
            'sector': 'road',
            'node_or_edge': 'node',
            'path': os.path.join(
                base_path,
                'Roads',
                'road_shapefiles',
                'tanroads_nodes_main_all_2017_adj.shp'),
        },
        {
            'sector': 'road',
            'node_or_edge': 'edge',
            'path': os.path.join(
                base_path,
                'Roads',
                'road_shapefiles',
                'tanroads_main_all_2017_adj.shp'),
        }
    ]


def get_hazard_details():
    details = []
    base_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'data', 'tanzania_flood'
    )
    rps = [
        '00002',
        '00005',
        '00025',
        '00050',
        '00100',
        '00250',
        '00500',
        '01000'
    ]
    for rp in rps:
        path = os.path.join(
            base_path,
            'EUWATCH',
            "inun_dynRout_RP_{}_Tanzania".format(rp),
            "inun_dynRout_RP_{}_contour_Tanzania.tif".format(rp)
        )
        details.append({
            'path': path,
            'model': 'EUWATCH',
            'r_period': int(rp)
        })

    glofris_models = [
        'GFDL-ESM2M',
        'HadGEM2-ES',
        'IPSL-CM5A-LR',
        'MIROC-ESM-CHEM',
        'NorESM1-M'
    ]
    for model in glofris_models:
        for rp in rps:
            path = os.path.join(
                base_path,
                model,
                'rcp6p0',
                '2030-2069',
                "inun_dynRout_RP_{}_bias_corr_masked_Tanzania".format(rp),
                "inun_dynRout_RP_{}_bias_corr_contour_Tanzania.tif".format(rp)
            )
        details.append({
            'path': path,
            'model': model,
            'r_period': rp
        })

    # SSBN models have a different set of return periods
    ssbn_rps = [
        '5',
        '10',
        '20',
        '50',
        '75',
        '100',
        '200',
        '250',
        '500',
        '1000'
    ]
    ssbn_models = {
        'TZ_fluvial_defended': 'FD',
        'TZ_fluvial_undefended': 'FU',
        'TZ_pluvial_defended': 'PD',
        'TZ_pluvial_undefended': 'PU',
        'TZ_urban_defended': 'UD',
        'TZ_urban_undefended': 'UU'
    }
    for model, abbr in ssbn_models.items():
        for rp in ssbn_rps:
            path = os.path.join(
                base_path,
                'SSBN_flood_data',
                model,
                "TZ-{}-{}-1.tif".format(abbr, rp)
            )
        details.append({
            'path': path,
            'model': "SSBN_{}".format(abbr),
            'r_period': int(rp)
        })

    return details


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
