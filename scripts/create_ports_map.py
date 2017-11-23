"""Generate ports map, including ferry terminals and sea ports
"""
# pylint: disable=C0103
import csv
import os

from utils import plot_pop, plot_countries, plot_regions

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

# TZ_TransNet_FerryTerminals
ports_filename = os.path.join(data_path, 'Infrastructure', 'Ports', 'TZ_ports.csv')

# Create figure
plt.figure(figsize=(6, 6), dpi=150)

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
plot_regions(ax, data_path)

xs = []
ys = []
with open(ports_filename, 'r', encoding="utf-8") as fh:
    r = csv.DictReader(fh)
    for record in r:
        x = float(record['longitude'])
        y = float(record['latitude'])
        xs.append(x)
        ys.append(y)
        name = record['name']
        if name in ('Kemondo Bay', 'Uvira', 'Mtwara'):
            y -= 0.35
        else:
            y += 0.05

        if x < 31:
            x += 0.05
            align = 'left'
        else:
            x -= 0.05
            align = 'right'
        ax.text(x, y, name, transform=proj_lat_lon, zorder=4, ha=align)

ax.scatter(xs, ys, facecolor='#1f78b4', s=5, zorder=3)

plt.title('Major Ferry Terminals and Sea Ports serving Tanzania')
output_filename = os.path.join(
    base_path,
    'figures',
    'ports_map.png'
)
plt.savefig(output_filename)
