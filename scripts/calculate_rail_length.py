"""Calculate length of railways by line
"""
# pylint: disable=C0103
import os
from collections import defaultdict

from shapely.geometry import shape

import fiona

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

# PMO_TanRoads
regional_road_filename = os.path.join(data_path, 'Infrastructure', 'Railways', 'tanzania-rail-ways-processed.geojson')

# Sum lengths by type
lengths_by_line = defaultdict(float)
total_length_m = 0.0

with fiona.open(regional_road_filename, 'r') as source:
    for line in source:

        # rail_line = line['properties']['line']
        rail_line = 'unknown'
        length = shape(line['geometry']).length

        total_length_m += length
        lengths_by_line[rail_line] += length

print("Total rail length: {:.2f} in {}".format(total_length_m, 'metres'))

# Output to CSV
output_filename = os.path.join(base_path, 'outputs', 'railways_length_by_line.csv')

with open(output_filename, 'w') as output_file:
    output_file.write('line,length(km)\n')
    for line, length_m in lengths_by_line.items():
        output_file.write("{},{:.3f}\n".format(line, length_m/1000))
    output_file.write("{},{:.3f}\n".format('Total', total_length_m/1000))
