"""Generate ports map, including ferry terminals and sea ports
"""
# pylint: disable=C0103
import csv
import os
import sys

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

# Input
ports_filename = os.path.join(data_path, 'Infrastructure', 'Ports',
                              'port_shapefiles', 'tz_port_nodes.shp')
edges_filename = os.path.join(data_path, 'Infrastructure', 'Ports',
                              'port_shapefiles', 'tz_port_edges.shp')

output_filename = os.path.join(figures_path, 'ports_map.png')

# Create figure
ax = get_tz_axes()

proj_lat_lon = ccrs.PlateCarree()

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

color = '#051591'

# Ferry routes
geoms = [
    record.geometry
    for record in shpreader.Reader(edges_filename).records()
]

ax.add_geometries(
    geoms,
    crs=proj_lat_lon,
    edgecolor=color,
    facecolor='none',
    alpha=0.5,
    zorder=3)

# Ferry ports
xs = []
ys = []
for record in shpreader.Reader(ports_filename).records():
    geom = record.geometry
    x = geom.x
    y = geom.y
    xs.append(x)
    ys.append(y)
    name = record.attributes['name']
    if name in ('Uvira', 'Port Bell'):
        y -= 0.3
    else:
        y += 0.05
    if name == 'Kemondo Bay':
        y -= 0.1
        x -= 0.05
    if name == 'Bujumbura':
        x += 0.05
        y -= 0.1

    if x < 31:
        x += 0.05
        align = 'left'
    else:
        x -= 0.05
        align = 'right'
    ax.text(x, y, name, transform=proj_lat_lon, zorder=4, ha=align, size=8)

ax.scatter(xs, ys, facecolor=color, s=7, zorder=3)

# Legend
legend_handles = [
    mpatches.Patch(color=color, label='Ports and waterways')
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

save_fig(output_filename)
