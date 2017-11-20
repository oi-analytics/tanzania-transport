"""Generate ports map, including ferry terminals and sea ports
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
ferry_path = os.path.join(data_path, 'Port_data')

# TZ_TransNet_FerryTerminals
ferry_terminals_filename = os.path.join(ferry_path, 'TZ_TransNet_FerryTerminals.shp')

# Mundy Ports
ports_filename = os.path.join(ferry_path, 'Mundy_Port', 'WPI_Africa_MundyData.shp')

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

# Sea ports
xs = []
ys = []
for record in shpreader.Reader(ports_filename).records():
    if record.attributes['FIPS_COUNT'] != 'TANZANIA':
        continue
    geom = record.geometry
    x = geom.x
    y = geom.y
    xs.append(x)
    ys.append(y)
    name = record.attributes['MAIN_PORT_'].title()
    x -= 0.05
    if name in ('Mjimwema Terminal', 'Mtwara', 'Chake Chake'):
        y -= 0.35
    else:
        y += 0.05
    ax.text(x, y, name, transform=proj_lat_lon, zorder=4, ha='right')

ax.scatter(xs, ys, facecolor='#1f78b4', s=5, zorder=3)

# Ferry ports
xs = []
ys = []
for record in shpreader.Reader(ferry_terminals_filename).records():
    if record.attributes['Country'] != 'Tanzania':
        continue
    geom = record.geometry
    x = geom.x
    y = geom.y
    xs.append(x)
    ys.append(y)
    name = record.attributes['Name']
    x -= 5000
    if name in ('Kampala'):
        y -= 35000
        print(name)
    else:
        y += 5000
    ax.text(x, y, name, transform=proj_3857, zorder=4, ha='right')

ax.scatter(xs, ys, facecolor='#1f78b4', s=5, transform=proj_3857, zorder=3)


plt.title('Major Ferry Terminals and Sea Ports in Tanzania')
output_filename = os.path.join(
    base_path,
    'figures',
    'ports_map.png'
)
plt.savefig(output_filename)