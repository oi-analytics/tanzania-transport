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
railway_filename = os.path.join(data_path, 'Railway_data', 'TZ_TransNet_Railroads.shp')
station_filename = os.path.join(data_path, 'Railway_data', 'TZ_rail_station_locations.csv')

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
for record in shpreader.Reader(railway_filename).records():
    geom = record.geometry
    country = record.attributes["Country"]
    if country == "Tanzania":
        ax.add_geometries(
            [geom],
            crs=proj_3857,
            edgecolor='#33a02c',
            facecolor='none',
            zorder=3)

# Stations
with open(station_filename, 'r') as station_file:
    reader = csv.DictReader(station_file, delimiter="\t")
    xs = []
    ys = []
    for line in reader:
        x = float(line['Longitude'])
        y = float(line['Latitude'])
        xs.append(x)
        ys.append(y)

        name = line['Region']
        if name in ('Arusha', 'Mruazi', 'Morogoro'):
            y -= 0.35
        else:
            y += 0.05

        ax.text(x, y, name, transform=proj_lat_lon, zorder=5)
    ax.scatter(xs, ys, facecolor='#000000', s=3, zorder=4)


plt.title('Major Railway Stations in Tanzania')
output_filename = os.path.join(
    base_path,
    'figures',
    'rail_map.png'
)
plt.savefig(output_filename)
