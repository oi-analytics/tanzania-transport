"""Weighted network for the volumes of annual tonnages along the roads and rail networks.
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import LineString

from utils import plot_pop, plot_countries, plot_regions

def main():
    # Input data
    base_path = os.path.join(os.path.dirname(__file__), '..')
    data_path = os.path.join(base_path, 'data')

    states_filename = os.path.join(data_path, 'Infrastructure', 'Boundaries',
                                'ne_10m_admin_0_countries_lakes.shp')

    # Roads
    road_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')

    # Rail
    rail_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_rail_spof_geom.shp')

    width_by_range = {
        (0, 1000): 0.005,
        (1000, 10000): 0.01,
        (10000, 100000): 0.02,
        (100000, 1000000): 0.04,
        (1000000, 10000000): 0.06,
        (10000000, 100000000): 0.08
    }

    road_data = [
        (record.geometry, record.attributes['ind_total'])
        for record in shpreader.Reader(road_filename).records()
    ]
    output_filename = os.path.join(
        base_path,
        'figures',
        'weighted_road_industry_total_map.png'
    )
    plot_weighted_network(
        data_path, width_by_range, road_data,
        output_filename, 'Annual freight tonnage on road in Tanzania', '#d1170a',
        't/y', 'TANROADS Trunk and Regional Roads'
    )

    rail_data = [
        (record.geometry, record.attributes['ind_total'])
        for record in shpreader.Reader(rail_filename).records()
    ]
    output_filename = os.path.join(
        base_path,
        'figures',
        'weighted_rail_industry_total_map.png'
    )
    plot_weighted_network(
        data_path, width_by_range, rail_data,
        output_filename, 'Annual freight tonnage on rail in Tanzania', '#33a02c',
        't/y', 'TRL and TAZARA Railways'
    )

    spof_filename = os.path.join(data_path, 'Analysis_results', 'tz_spof_flow_analysis.xlsx')

    road_flow_data = pd.read_excel(
        spof_filename,
        sheet_name='road_od_losses'
    )
    road_centrality = {}
    for i, row in road_flow_data.iterrows():
        centrality = row['centrality']
        link = int(row['link'])
        road_centrality[link] = centrality

    road_data = [
        (
            record.geometry,
            road_centrality[record.attributes['link']]
        )
        for record in shpreader.Reader(road_filename).records()
    ]

    width_by_range = {
        (0, 0.0001): 0.005,
        (0.0001, 0.001): 0.01,
        (0.001, 0.01): 0.02,
        (0.01, 0.1): 0.04,
        (0.1, 1): 0.08,
    }

    output_filename = os.path.join(
        base_path,
        'figures',
        'weighted_road_path_centrality_map.png'
    )
    plot_weighted_network(
        data_path, width_by_range, road_data,
        output_filename, 'Road link path centrality', '#d1170a',
        '', 'TANROADS Trunk and Regional Roads'
    )


    road_incr_cost = {}
    for i, row in road_flow_data.iterrows():
        incr_cost = row['tr_p_incr_high']
        link = int(row['link'])
        road_incr_cost[link] = incr_cost

    road_data = []
    for record in shpreader.Reader(road_filename).records():
        val = road_incr_cost[record.attributes['link']]
        if val < 0:
            val = 0
        road_data.append(
            (
                record.geometry,
                val
            )
        )

    width_by_range = {
        (0, 100): 0.005,
        (100, 1000): 0.01,
        (1000, 10000): 0.02,
        (10000, 100000): 0.04,
        (100000, 1000000): 0.08,
    }

    output_filename = os.path.join(
        base_path,
        'figures',
        'weighted_road_incr_cost_map.png'
    )
    plot_weighted_network(
        data_path, width_by_range, road_data,
        output_filename, 'Cost increase per road link', '#d1170a',
        'USD/day', 'TANROADS Trunk and Regional Roads'
    )


def plot_weighted_network(data_path, width_by_range, data,
                          output_filename, title, linecolor, unit, legend_text):
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

    # Grouped geoms to plot
    to_plot = {}
    for value_range in width_by_range:
        to_plot[value_range] = []

    for geom, val in data:
        for nmin, nmax in to_plot:
            if nmin <= val and val < nmax:
                to_plot[(nmin, nmax)].append(geom)

    for value_range, geoms in to_plot.items():
        ax.add_geometries(
            [geom.buffer(width_by_range[value_range]) for geom in geoms],
            crs=proj_lat_lon,
            linewidth=0,
            edgecolor=linecolor,
            facecolor=linecolor,
            zorder=2)

    # Legend
    # x0 = 28.6
    # x1 = 41.4
    # y0 = 0.5
    # y1 = -12.5
    x_l = 28.8
    x_r = 29.5
    base_y = -9
    for (i, ((nmin, nmax), width)) in enumerate(width_by_range.items()):
        y = base_y - (i*0.4)
        line = LineString([(x_l, y), (x_r, y)])
        ax.add_geometries(
            [line.buffer(width)],
            crs=proj_lat_lon,
            linewidth=0,
            edgecolor='#000000',
            facecolor='#000000',
            zorder=2)
        if nmax == 100000000:
            label = '>10000000 {}'.format(unit)
        else:
            label = '{}-{} {}'.format(nmin, nmax, unit)
        ax.text(
            x_r + 0.1,
            y - 0.15,
            label,
            horizontalalignment='left',
            transform=proj_lat_lon)

    legend_handles = [
        mpatches.Patch(color=linecolor, label=legend_text),
    ]
    plt.legend(
        handles=legend_handles,
        loc='lower left'
    )
    plt.title(title)

    plt.savefig(output_filename)
    plt.close()

if __name__ == '__main__':
    main()
