"""Generate transport corridor map, showing major routes and nodes for each mode
"""
# pylint: disable=C0103
import csv
import os

from utils import plot_pop, plot_countries, plot_regions

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

# TransNet_Railroads
# Railways
railway_nodes_filename = os.path.join(data_path, 'Infrastructure', 'Railways', 'tanzania-rail-nodes-processed.shp')
railway_ways_filename = os.path.join(data_path, 'Infrastructure', 'Railways', 'tanzania-rail-ways-processed.shp')

# Create figure
plt.figure(figsize=(6, 6), dpi=150)

proj_lat_lon = ccrs.PlateCarree()
proj_3857 = ccrs.epsg(3857)
ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)
x0 = 28.6
x1 = 41.4
y0 = 0.5
y1 = -12.5
ax.set_extent([x0, x1, y0, y1], crs=proj_lat_lon)

# Background
plot_countries(ax, data_path)
plot_pop(plt, ax, data_path)
plot_regions(ax, data_path)

# Railways
for record in shpreader.Reader(railway_ways_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#33a02c',
        facecolor='none',
        zorder=3)

# Stations
xs = []
ys = []
minor_xs = []
minor_ys = []
for record in shpreader.Reader(railway_nodes_filename).records():
    node_type = record.attributes['node_type']
    if node_type == 'junction':
        continue

    geom = record.geometry
    x = geom.x
    y = geom.y
    if node_type == 'minor':
        minor_xs.append(x)
        minor_ys.append(y)
    else:
        xs.append(x)
        ys.append(y)

    if node_type in ('major', 'transfer', 'final'):
        name = record.attributes['name']
        if name in ('Arusha', 'Mruazi', 'Morogoro', 'Mpanda', 'Mbeya', 'Tunduma'):
            y -= 0.35
        else:
            y += 0.05

        if name in ('Nakonde (Zambia)', 'Kidatu', 'Isaka', 'Ruvu', 'Kilosa'):
            align = 'right'
        else:
            align = 'left'
        ax.text(x, y, name, transform=proj_lat_lon, zorder=5, ha=align)

ax.scatter(minor_xs, minor_ys, facecolor='#000000', s=1, zorder=4)
ax.scatter(xs, ys, facecolor='#000000', s=5, zorder=5)


plt.title('Major Railway Stations in Tanzania')
output_filename = os.path.join(
    base_path,
    'figures',
    'rail_map.png'
)
plt.savefig(output_filename)
