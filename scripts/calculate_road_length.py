"""Calculate length of road by type (from PMO_TanRoads)
"""
# pylint: disable=C0103
import os

from shapely.geometry import shape

import fiona

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

# PMO_TanRoads
regional_road_filename = os.path.join(data_path, 'Road_data', 'PMO_Tanroads_3857.shp')

# Sum lengths by type
lengths_by_type = {
    'Earth': 0.0,
    'Gravel': 0.0,
    'Not Existing': 0.0,
    'Paved': 0.0,
    'Unpaved': 0.0
}
total_length_m = 0.0

with fiona.open(regional_road_filename, 'r') as shp:
    for line in shp:
        road_type = line['properties']['road_qlty']
        length = shape(line['geometry']).length

        total_length_m += length
        lengths_by_type[road_type] += length

print("Total road length: {:.2f} in {}".format(total_length_m, 'metres'))

# Output to CSV
output_filename = os.path.join(base_path, 'outputs', 'PMO_TanRoads_3857_length_by_road_qlty.csv')

with open(output_filename, 'w') as output_file:
    output_file.write('road_qlty,length(km)\n')
    for road_qlty, length_m in lengths_by_type.items():
        output_file.write("{},{:.3f}\n".format(road_qlty, length_m/1000))
    output_file.write("{},{:.3f}\n".format('Total', total_length_m/1000))
