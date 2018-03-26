"""Generate airport map
"""
# pylint: disable=C0103
import csv
import os

from utils import plot_pop, plot_countries, plot_regions

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

# tanzania_airports from ourairports.com
airport_filename = os.path.join(data_path, 'Infrastructure', 'Airports', 'TZ_airport_node_flows.csv')

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

# Airports
xs = []
ys = []
with open(airport_filename, 'r') as airports_file:
    reader = csv.DictReader(airports_file)
    for line in reader:
        x = float(line['longitude_deg'])
        y = float(line['latitude_deg'])
        xs.append(x)
        ys.append(y)
        name = line['name']
        if name in [
            'Julius Nyerere International Airport',
            'Kilimanjaro International Airport',
            'Abeid Amani Karume International Airport',
            'Mbeya Airport',
            'Pemba Airport',
            ]:
            y -= 0.35
        else:
            y += 0.05

        if name in [
            'Abeid Amani Karume International Airport',
            'Mtwara Airport',
            'Julius Nyerere International Airport',
            'Lake Manyara Airport',
            'Mafia Island Airport',
            'Pemba Airport',
            'Tanga Airport',
            'Songwe Airport',
            'Dodoma Airport'
            ]:
            x -= 0.05
            align = 'right'
        else:
            x += 0.05
            align = 'left'

        name = name.replace(' Airport', '')
        name = name.replace(' International', '')
        ax.text(x, y, name, transform=proj_lat_lon, zorder=4, ha=align)

ax.scatter(xs, ys, facecolor='#b41f78', s=5, zorder=3)



plt.title('Major Airports in Tanzania')

output_filename = os.path.join(
    base_path,
    'figures',
    'airports_map.png'
)
plt.savefig(output_filename)
