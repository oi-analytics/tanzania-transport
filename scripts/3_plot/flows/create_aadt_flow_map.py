"""Map transport network (initially roads) with commodity flows
"""
import csv
import math
import os

from utils import plot_pop, plot_countries, plot_regions

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.colors

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')
inf_path = os.path.join(data_path, 'Infrastructure')

# Roads
road_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'tanroads_all_2017.shp')

# Create figure
plt.figure(figsize=(6, 7), dpi=150)

proj_lat_lon = ccrs.PlateCarree()
ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)
x0 = 28.6
x1 = 41.4
y0 = 0.5
y1 = -12.5
ax.set_extent([x0, x1, y0, y1], crs=proj_lat_lon)

# Background
plot_countries(ax, data_path)
plot_pop(plt, ax, data_path)

plt.title('AADT flows in Tanzania')

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

output_filename = os.path.join(
    base_path,
    'figures',
    'aadt_flow_map.png'
)
plt.savefig(output_filename)
