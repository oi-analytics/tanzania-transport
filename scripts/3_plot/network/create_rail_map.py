"""Generate transport corridor map, showing major routes and nodes for each mode
"""
# pylint: disable=C0103
import csv
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

# Railways
railway_nodes_filename = os.path.join(
    data_path, 'Infrastructure', 'Railways', 'railway_shapefiles',
    'tanzania-rail-nodes-processed.shp')
railway_ways_filename = os.path.join(
    data_path, 'Infrastructure', 'Railways', 'railway_shapefiles',
    'tanzania-rail-ways-processed.shp')

output_filename = os.path.join(figures_path, 'rail_map.png')

# Create figure
ax = get_tz_axes()
proj_lat_lon = ccrs.PlateCarree()

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

geom_by_line = defaultdict(list)
color_by_line = {
    'Central': '#fd8f00',
    'Link': '#538235',
    'Mpanda': '#ff33cc',
    'Mwanza': '#5f5f5f',
    'Singida':'#be9000',
    'Tanga': '#006fc0',
    'TAZARA': '#33a02c',
    'TRL-TAZARA': '#37ce7e'
}

# Railways
for record in shpreader.Reader(railway_ways_filename).records():
    geom = record.geometry
    line = record.attributes['line_name']
    geom_by_line[line].append(geom)

for line, geoms in geom_by_line.items():
    if line == 'Unknown':
        continue
    if line in ('Link', 'Tanga'):
        ax.add_geometries(
            geoms,
            crs=proj_lat_lon,
            linestyle='dashed',
            edgecolor=color_by_line[line],
            facecolor='none',
            zorder=3)
    else:
        ax.add_geometries(
            geoms,
            crs=proj_lat_lon,
            edgecolor=color_by_line[line],
            facecolor='none',
            zorder=3)

# Stations
xs = []
ys = []
for record in shpreader.Reader(railway_nodes_filename).records():
    node_type = record.attributes['rail_node_']
    if node_type in ('major', 'final'):
        geom = record.geometry
        x = geom.x
        y = geom.y
        xs.append(x)
        ys.append(y)
        name = record.attributes['name']
        if name in ('Arusha', 'Isaka', 'Mruazi', 'Morogoro', 'Mpanda', 'Mbeya', 'Tunduma'):
            y -= 0.3
        else:
            y += 0.1
        if name == 'Isaka':
            x -= 0.05

        if name in ('Kidatu', 'Isaka', 'Ruvu', 'Kilosa', 'Arusha'):
            align = 'right'
        else:
            align = 'left'
        ax.text(x, y, name, transform=proj_lat_lon, zorder=5, ha=align)

ax.scatter(xs, ys, facecolor='#000000', s=5, zorder=5)

# Legend
legend_handles = [
    mpatches.Patch(color=color, label=line)
    for line, color in color_by_line.items()
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

save_fig(output_filename)
