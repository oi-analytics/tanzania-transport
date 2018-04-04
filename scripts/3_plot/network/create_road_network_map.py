"""Generate detailed road network map of Tanzania
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

# Input data
inf_path = os.path.join(data_path, 'Infrastructure')

# TZ_TransNet_Roads, clipped to Tanzania
cr_file = os.path.join(inf_path, 'Roads', 'road_shapefiles',
                             'tanroads_main_all_2017_adj.shp')
co_file = os.path.join(figures_path, 'road_network_map_2017.png')


fr_file = os.path.join(inf_path, 'Roads', 'road_shapefiles',
                             'tanroads_main_all_2030_adj.shp')
fo_file = os.path.join(figures_path, 'road_network_map_2030.png')

for road_filename, output_filename in [(cr_file, co_file), (fr_file, fo_file)]:
    # Create figure
    ax = get_tz_axes()

    proj_lat_lon = ccrs.PlateCarree()
    proj_3857 = ccrs.epsg(3857)

    # Background
    plot_basemap(ax, data_path)
    plot_basemap_labels(ax, data_path)
    scale_bar(ax, length=100, location=(0.925,0.02))

    trunk_paved = []
    trunk_unpaved = []
    regional_paved = []
    regional_unpaved = []

    for record in shpreader.Reader(road_filename).records():
        trunk = record.attributes['roadclass'] == 'T'
        paved = record.attributes['road_cond'] == 'paved'
        if trunk and paved:
            trunk_paved.append(record.geometry)
        elif trunk and (not paved):
            trunk_unpaved.append(record.geometry)
        elif (not trunk) and paved:
            regional_paved.append(record.geometry)
        else:
            regional_unpaved.append(record.geometry)

    tp_color = '#ba0f03'
    tu_color = '#ff7b72'
    rp_color = '#e0881f'
    ru_color = '#ffe0bc'

    ax.add_geometries(
        trunk_paved,
        crs=proj_lat_lon,
        linewidth=5,
        edgecolor=tp_color,
        facecolor='none',
        zorder=5)
    ax.add_geometries(
        trunk_unpaved,
        crs=proj_lat_lon,
        edgecolor=tu_color,
        facecolor='none',
        zorder=4)
    ax.add_geometries(
        regional_paved,
        crs=proj_lat_lon,
        edgecolor=rp_color,
        facecolor='none',
        zorder=3)
    ax.add_geometries(
        regional_unpaved,
        crs=proj_lat_lon,
        edgecolor=ru_color,
        facecolor='none',
        zorder=2)

    # Legend
    legend_handles = [
        mpatches.Patch(color=tp_color, label='Trunk (paved)'),
        mpatches.Patch(color=tu_color, label='Trunk (unpaved)'),
        mpatches.Patch(color=rp_color, label='Regional (paved)'),
        mpatches.Patch(color=ru_color, label='Regional (unpaved)'),
    ]
    plt.legend(
        handles=legend_handles,
        loc='lower left'
    )

    save_fig(output_filename)
