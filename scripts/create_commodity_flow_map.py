"""Map transport network (initially roads) with commodity flows
"""
import csv
import json
import math
import os
from collections import defaultdict

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

# Flows
flows_filename = os.path.join(inf_path, 'Roads', 'od_network_flows_2.csv')

commodities_of_interest = [
    'Vegetable Products',
    'Foodstuffs',
    'Mineral_Products'
]

# Create figure
proj_lat_lon = ccrs.PlateCarree()
fig, axes = plt.subplots(
    nrows=1,
    ncols=len(commodities_of_interest),
    subplot_kw=dict(projection=proj_lat_lon),
    figsize=(10, 3),
    dpi=150)

plt.suptitle('Commodity flows in Tanzania')

road_links = {}
for record in shpreader.Reader(road_filename).records():
    link = str(record.attributes['link'])
    geom = record.geometry
    road_links[link] = {
        'flows': defaultdict(float),
        'geom': geom,
        'id': link
    }

with open(flows_filename, 'r') as fh:
    r = csv.DictReader(fh)
    for line in r:
        links = json.loads(line['edge_path'])
        commodity = line['commodity']
        value = line['value']
        for link in links:
            road_links[str(link)]['flows'][commodity] += float(value)

# colors = plt.get_cmap('plasma')
colors = plt.get_cmap('YlOrRd')

extent = [28.6, 41.4, 0.5, -12.5]
max_value = 1

for commodity_name in commodities_of_interest:
    c_max_value = max(link['flows'][commodity_name] for link in road_links.values())
    if c_max_value > max_value:
        max_value = c_max_value

color_map = plt.cm.ScalarMappable(cmap=colors, norm=matplotlib.colors.LogNorm(vmin=1, vmax=max_value))

for i, ax in enumerate(axes):
    ax.set_extent(extent, crs=proj_lat_lon)

    # Background
    plot_countries(ax, data_path)
    plot_pop(plt, ax, data_path)

    commodity_name = commodities_of_interest[i]

    for link in road_links.values():
        value = link['flows'][commodity_name]
        if value > 0:
            color = color_map.to_rgba(value)
        else:
            color = color_map.to_rgba(1)

        geom = link['geom']

        ax.add_geometries(
            [geom],
            crs=proj_lat_lon,
            edgecolor=color,
            facecolor='none',
            zorder=2)
        ax.set_title(commodity_name.replace("_", " "))


plt.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.02, rect=(0.05, 0.1, 0.95, 0.9))

# Add colorbar
color_map._A = []  # hack in array to avoid error
ax_list = list(axes.flat)
cbar = plt.colorbar(color_map, ax=ax_list, fraction=0.05, pad=0.01, drawedges=False, orientation='vertical')
cbar.outline.set_color("none")
cbar.ax.set_ylabel('Tonnes of commodity flow')

output_filename = os.path.join(
    base_path,
    'figures',
    'commodity_flow_map.png'
)
plt.savefig(output_filename)
