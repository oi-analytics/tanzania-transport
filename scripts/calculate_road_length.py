"""Calculate length of road by type (from PMO_TanRoads)
"""
# pylint: disable=C0103
import os

from collections import defaultdict
from shapely.geometry import shape

import fiona

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')
roads_path = os.path.join(data_path, 'Infrastructure', 'Roads', 'Tanroads_flow_shapefiles')

# PMO_TanRoads
regional_road_filename = os.path.join(roads_path, 'region_roads_2017.shp')
trunk_road_filename = os.path.join(roads_path, 'trunk_roads_2017.shp')

# Sum lengths by type
lengths_by_qlty = {
    'Earth': 0.0,
    'Gravel': 0.0,
    'Not Existing': 0.0,
    'Paved': 0.0,
    'Unpaved': 0.0
}
type_and_qlty = defaultdict(int)
total_length_m = 0.0

with fiona.open(regional_road_filename, 'r') as shp:
    for line in shp:
        road_qlty = line['properties']['road_qlty']

        # using the 'type' attribute and 'surfacecon' only ever gives
        # trunk-unpaved OR regional-paved OR null-null (never e.g. trunk-paved)

        type_ = line['properties']['roadclass']
        type_ = type_.strip()

        if type_ == 'R':
            type_ = 'Regional Road'
        if type_ == 'T':
            type_ = 'Trunk Road'

        if road_qlty == 'Paved':
            surfacecon = 'Paved'
        else:
            surfacecon = 'Unpaved'

        # kilometre length from attr - sometimes null
        length_1 = line['properties']['length_1']
        # metre length from geometry
        length = shape(line['geometry']).length

        total_length_m += length
        lengths_by_qlty[road_qlty] += length

        type_and_qlty[(type_, surfacecon)] += length

print("Total road length: {:.2f} in {}".format(total_length_m, 'metres'))

# Output to CSV
output_filename = os.path.join(base_path, 'outputs', 'road_length_by_road_qlty.csv')
output_type_and_qlty_filename = os.path.join(base_path, 'outputs', 'road_length_by_type_surfacecon.csv')

with open(output_filename, 'w') as output_file:
    output_file.write('road_qlty,length(km)\n')
    for road_qlty, length_m in lengths_by_qlty.items():
        output_file.write("{},{:.3f}\n".format(road_qlty, length_m/1000))

with open(output_type_and_qlty_filename, 'w') as output_file:
    output_file.write('type,surfacecon,length(km)\n')
    for (type_, surfacecon), length_m in type_and_qlty.items():
        output_file.write("{},{},{:.3f}\n".format(type_, surfacecon, length_m/1000))
