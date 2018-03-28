"""Intersect hazard bands with networks

Output rows like:
- network_element_type (node/edge)
- sector (road/rail/port/airport)
- id
- model
- rp
- point_val
"""
import csv
import os
import sys

import fiona
from rasterstats import zonal_stats

def main(filenum):
    # all output printed to STDOUT - start with CSV header
    with open('osm_intersection_{}.csv'.format(filenum), 'w') as fh:
        w = csv.writer(fh)
        w.writerow((
            'network_element',
            'sector',
            'id',
            'model',
            'return_period',
            'flood_depth'
        ))
        for network_details in get_network_details(filenum):
            with fiona.open(network_details['path']) as network:
                for hazard_details in get_hazard_details():
                    for line in intersect_network(network, network_details, hazard_details):
                        w.writerow(line)

def intersect_network(network, network_details, hazard_details):
    sector = network_details['sector']
    node_or_edge = network_details['node_or_edge']

    hazard_path = hazard_details['path']
    model = hazard_details['model']
    return_period = hazard_details['r_period']

    all_stats = zonal_stats(network, hazard_path, stats=['max'])

    for stats, element in zip(all_stats, network):
        max_ = stats['max']
        if max_ is not None and max_ > 0 and max_ < 999:
            yield (
                node_or_edge,
                sector,
                str(element['properties']['id']),
                model,
                str(int(return_period)),
                str(max_),
                element['properties']['highway']
            )

def get_network_details(filenum):
    base_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'data', 'Infrastructure'
    )
    return [
        {
            'sector': 'road_osm',
            'node_or_edge': 'edge',
            'path': os.path.join(
                base_path,
                'Roads',
                'osm_mainroads',
                'TZA.shp.{}.shp'.format(filenum)),
        }
    ]


def get_hazard_details():
    details = []
    base_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'data', 'tanzania_flood'
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
    ssbn_models = [
        ('TZ_fluvial_undefended', 'FU'),
        ('TZ_pluvial_undefended', 'PU')
    ]
    for model, abbr in ssbn_models:
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

if __name__ == '__main__':
    print("Running", sys.argv[1])
    main(sys.argv[1])
