"""Map transport network (initially roads) with commodity flows
"""
# pylint: disable=C0103
import math
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.colors

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

# Input data
config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']
inf_path = os.path.join(data_path, 'Infrastructure')

# Roads
road_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'tanroads_all_2017.shp')

output_filename = os.path.join(
    figures_path,
    'aadt_flow_map.png'
)

# Create figure
ax = get_tz_axes()
proj_lat_lon = ccrs.PlateCarree()

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

aadt_and_geoms = []
for record in shpreader.Reader(road_filename).records():
    aadt = record.attributes['curredaadt']
    geom = record.geometry
    if aadt is None:
        aadt = 0
    aadt_and_geoms.append((aadt, geom, ))


aadts = [aadt for aadt, geom in aadt_and_geoms]
max_aadt = math.log(max(aadts))

# colors = plt.get_cmap('plasma')
colors = plt.get_cmap('YlOrRd')
color_map = plt.cm.ScalarMappable(cmap=colors, norm=matplotlib.colors.LogNorm(vmin=1, vmax=max(aadts)))

for aadt, geom in aadt_and_geoms:
    if aadt > 0:
        color = color_map.to_rgba(aadt)
    else:
        color = color_map.to_rgba(1)
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor=color,
        facecolor='none',
        zorder=2)

# Add colorbar
color_map._A = []
cbar = plt.colorbar(color_map, ax=ax, fraction=0.1, pad=0.01, drawedges=False, orientation='horizontal')
cbar.outline.set_color("none")
cbar.ax.set_xlabel('Vehicle counts')

plt.savefig(output_filename)
