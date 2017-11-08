"""Generate detailed road network map of Tanzania
"""
# pylint: disable=C0103
import os

from utils import plot_pop, plot_countries, plot_regions

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

states_filename = os.path.join(data_path, 'Boundary_datasets',
                               'ne_10m_admin_0_countries_lakes.shp')

# TZ_TransNet_Roads, clipped to Tanzania
major_road_filename = os.path.join(data_path, 'Road_data', 'TZ_TransNet_Roads.shp')
# PMO_TanRoads
regional_road_filename = os.path.join(data_path, 'Road_data', 'PMO_Tanroads_3857.shp')

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

# Regional roads
for record in shpreader.Reader(regional_road_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_3857,
        edgecolor='#33a02c',
        linewidth=3,
        facecolor='none',
        zorder=2)

# Major roads
for record in shpreader.Reader(major_road_filename).records():
    geom = record.geometry
    outline = geom.buffer(2000)
    country = record.attributes["Country"]
    if country == "Tanzania":
        ax.add_geometries(
            [outline],
            crs=proj_3857,
            linewidth=3,
            edgecolor='#1f78b4',
            facecolor='none',
            zorder=3)

# Legend
legend_handles = [
    mpatches.Patch(color='#1f78b4', label='Major Roads'),
    mpatches.Patch(color='#33a02c', label='Regional Roads'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)
plt.title('Major and Regional Roads in Tanzania')


output_filename = os.path.join(
    base_path,
    'figures',
    'road_network_map.png'
)
plt.savefig(output_filename)
