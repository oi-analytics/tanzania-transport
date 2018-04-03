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
type_and_qlty = defaultdict(int)
total_length = 0.0

with fiona.open(regional_road_filename, 'r') as shp:
    for line in shp:
        km_paved = line['properties']['KMPAVED']
        km_unpaved = line['properties']['KMUNPAVED']

        # metre length from geometry - needs to be reprojected
        # geom_length = shape(line['geometry']).length

        total_length += km_paved + km_unpaved

        type_and_qlty[("regional", "paved")] += km_paved
        type_and_qlty[("regional", "unpaved")] += km_unpaved

with fiona.open(trunk_road_filename, 'r') as shp:
    for line in shp:
        km_paved = line['properties']['KMPAVED']
        km_unpaved = line['properties']['KMUNPAVED']

        # metre length from geometry - needs to be reprojected
        # geom_length = shape(line['geometry']).length

        total_length += km_paved + km_unpaved

        type_and_qlty[("trunk", "paved")] += km_paved
        type_and_qlty[("trunk", "unpaved")] += km_unpaved

print("Total road length: {:.2f} in {}".format(total_length, 'kilometres'))

# Output to CSV
output_type_and_qlty_filename = os.path.join(base_path, 'outputs', 'road_length_by_type_paved.csv')

with open(output_type_and_qlty_filename, 'w') as output_file:
    output_file.write('type,surfacecon,length(km)\n')
    for (type_, surfacecon), length_km in type_and_qlty.items():
        output_file.write("{},{},{:.3f}\n".format(type_, surfacecon, length_km))
