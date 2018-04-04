"""Generate airport map
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

# tanzania_airports from ourairports.com
airport_filename = os.path.join(data_path, 'Infrastructure', 'Airports',
                                'airport_shapefiles', 'tz_od_airport_nodes.shp')
output_filename = os.path.join(figures_path, 'airports_map.png')

# Create figure
ax = get_tz_axes()

proj_lat_lon = ccrs.PlateCarree()
proj_3857 = ccrs.epsg(3857)

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

# Airports
selected_color = '#5b1fb4'
major_color = '#b41f78'
xs = []
ys = []
minor_xs = []
minor_ys = []
for record in shpreader.Reader(airport_filename).records():
    if record.attributes['iso_countr'] != 'TZ':
        continue

    geom = record.geometry
    x = geom.x
    y = geom.y

    name = record.attributes['name']
    name = name.replace(' Airport', '')
    name = name.replace(' International', '')

    if name not in (
            'Julius Nyerere',
            'Arusha',
            'Kilimanjaro'):

        minor_xs.append(x)
        minor_ys.append(y)
        continue

    xs.append(x)
    ys.append(y)

    if name == 'Arusha':
        y += 0.07
        x += 0.05
        align = 'right'
    elif name == 'Julius Nyerere':
        y -= 0.1
        x -= 0.05
        align = 'right'
    else:
        y += 0.05
        x += 0.05
        align = 'left'

    ax.text(x, y, name, transform=proj_lat_lon, zorder=4, ha=align, size=8)

ax.scatter(xs, ys, facecolor=selected_color, s=11, zorder=3)
ax.scatter(minor_xs, minor_ys, facecolor=major_color, s=5, zorder=3)

# Legend
legend_handles = [
    mpatches.Patch(color=selected_color, label='Study Airports'),
    mpatches.Patch(color=major_color, label='Other Major Airports')
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

save_fig(output_filename)
