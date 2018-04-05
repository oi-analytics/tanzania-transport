"""Map multi-point failure scenarios
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.colors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import LineString

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

def main():
    """Plot maps
    """
    # Input data
    scenarios = [
        {
            'name':'A',
            'links': [1994, 6870, 6855]
        },
        {
            'name':'B',
            'links': [3143, 910]
        },
        {
            'name':'C',
            'links': [906, 907, 905, 4020, 4015]
        },
    ]

    config = load_config()
    data_path = config['data_path']
    figures_path = config['figures_path']

    road_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')
    output_filename = os.path.join(
        figures_path,
        'mpof_scenarios_map.png')

    x0 = 28.6
    x1 = 41.4
    y0 = 0.5
    y1 = -12.5
    tz_extent = [x0, x1, y0, y1]
    proj_lat_lon = ccrs.PlateCarree()

    _, axes = plt.subplots(
        nrows=1,
        ncols=3,
        subplot_kw=dict(projection=proj_lat_lon),
        figsize=(12, 5),
        dpi=150)

    once = True
    for ax, scenario in zip(axes.flat, scenarios):
        ax.locator_params(tight=True)
        ax.set_extent(tz_extent, crs=proj_lat_lon)

        ax.set_title("Scenario {}".format(scenario['name']))

        plot_basemap(ax, data_path)

        highlight = []
        other = []

        for record in shpreader.Reader(road_filename).records():
            if record.attributes['link'] in scenario['links']:
                highlight.append(record.geometry.buffer(0.06))
            else:
                other.append(record.geometry.buffer(0.005))

        ax.add_geometries(
            other,
            crs=proj_lat_lon,
            edgecolor='#000000',
            linewidth=0,
            facecolor='#000000',
            zorder=2)

        ax.add_geometries(
            highlight,
            crs=proj_lat_lon,
            edgecolor='#d1170a',
            linewidth=0,
            facecolor='#d1170a',
            zorder=3)

        if once:
            once = False
            highlight_handle = mpatches.Patch(color='#d1170a')
            other_handle = mpatches.Patch(color='#000000')

            ax.legend(
                [highlight_handle, other_handle],
                ["Affected roads", "Other TANROADS trunk and regional roads"],
                loc='lower left')

    plt.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.02, rect=(0, 0, 1, 1))

    plt.savefig(output_filename)
    plt.close()

if __name__ == '__main__':
    main()
