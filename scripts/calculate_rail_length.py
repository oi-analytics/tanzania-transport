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
regional_road_filename = os.path.join(data_path, 'Railway_data', 'TZ_TransNet_Railroads.shp')

# Map from osm_id to line (TRL or TAZARA)
line_by_osm_id = {
    '23321368': 'TRL',
    '23345759': 'TRL',
    '23600447': 'TRL',
    '23818705': 'TAZARA',
    '23819458': 'TRL',
    '23819519': 'TRL',
    '23820886': 'TRL',
    '23820943': 'TRL',
    '23837370': 'TRL',
    '23837407': 'TRL',
    '23837424': 'TRL',
    '23859111': 'TRL',
    '23859316': 'TRL',
    '23939224': 'TRL',
    '23939837': 'TRL',
    '24187159': 'TRL',
    '162701151': 'TAZARA',
    '172541155': 'TRL',
    '200454397': 'TAZARA',
}

# Sum lengths by type
lengths_by_line = {
    'TRL': 0.0,
    'TAZARA': 0.0
}
total_length_m = 0.0

with fiona.open(regional_road_filename, 'r') as shp:
    for line in shp:
        country = line['properties']['Country']
        if country != 'Tanzania':
            continue

        osm_id = line['properties']['osm_id']
        rail_line = line_by_osm_id[osm_id]
        length = shape(line['geometry']).length

        total_length_m += length
        lengths_by_line[rail_line] += length

print("Total rail length: {:.2f} in {}".format(total_length_m, 'metres'))

# Output to CSV
output_filename = os.path.join(base_path, 'outputs', 'TZ_TransNet_Railroads_length_by_line.csv')

with open(output_filename, 'w') as output_file:
    output_file.write('line,length(km)\n')
    for line, length_m in lengths_by_line.items():
        output_file.write("{},{:.3f}\n".format(line, length_m/1000))
    output_file.write("{},{:.3f}\n".format('Total', total_length_m/1000))
