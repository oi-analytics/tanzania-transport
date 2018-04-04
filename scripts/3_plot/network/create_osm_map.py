"""Generate detailed road network map of Tanzania
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

# Input data
input_filename = os.path.join(data_path, 'Infrastructure', 'Roads',
                              'osm_mainroads', 'TZA.shp')
output_filename = os.path.join(figures_path, 'osm_network_map.png')

# Create figure
ax = get_tz_axes()

proj_lat_lon = ccrs.PlateCarree()
proj_3857 = ccrs.epsg(3857)

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

edgecolor = '#ba0f03'

roads = [
    record.geometry.buffer(0.005)
    for record in shpreader.Reader(input_filename).records()
]

ax.add_geometries(
    roads,
    crs=proj_lat_lon,
    linewidth=5,
    facecolor=edgecolor,
    edgecolor='none',
    zorder=2)

# Legend
legend_handles = [
    mpatches.Patch(color=edgecolor, label='OpenStreetMap roads')
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

plt.savefig(output_filename) # no svg
