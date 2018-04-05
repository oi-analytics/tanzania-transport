"""Plot flooding impact on infrastructure

(a) For roads, plot incr_fact and tr_p_incr_high losses for flooding present/future
(b) For rail, plot ind_tot losses for flooding present/future
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
    # Input data
    config = load_config()
    data_path = config['data_path']
    figures_path = config['figures_path']

    # Roads
    road_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')
    # Rail
    rail_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_rail_spof_geom.shp')
    # Exposure
    exposure_filename = os.path.join(
        data_path, 'Analysis_results', 'tz_flood_stats_3.xlsx')

    x0 = 28.6
    x1 = 41.4
    y0 = 0.5
    y1 = -12.5
    tz_extent = [x0, x1, y0, y1]
    proj_lat_lon = ccrs.PlateCarree()

    specs = [
        # tanroads_link_flooding: link: incr_fact ton_km_loss (rpmin_curr,rpmin_fut >0)
        {
            'title': 'Flooding impact on road rerouting',
            'sheet_name': 'tanroads_link_flooding',
            'shape_filename': road_filename,
            'id_col': 'link',
            'val_col': 'incr_fact',
            'legend_label': 'Increase factor',
            'filename': 'impact_road_incr_fact.png',
            'weights': {
                0: 0.005,
                5: 0.01,
                10: 0.02,
                50: 0.04,
                100: 0.06,
                1100: 0.08
            }
        },
        {
            'title': 'Flooding impact on road freight',
            'sheet_name': 'tanroads_link_flooding',
            'shape_filename': road_filename,
            'id_col': 'link',
            'val_col': 'tr_p_incr_high',
            'legend_label': 'USD/day',
            'filename': 'impact_road_tr_p_incr_high.png',
            'weights': {
                0: 0.005,
                100: 0.01,
                1000: 0.02,
                10000: 0.04,
                100000: 0.08
            }
        },
        # rail_edge_flooding: id: ind_total (rpmin_curr,rpmin_fut >0)
        {
            'title': 'Flooding impact on rail freight flows',
            'sheet_name': 'rail_edge_flooding',
            'shape_filename': rail_filename,
            'id_col': 'id',
            'val_col': 'ind_total',
            'legend_label': 'Tons of freight',
            'filename': 'impact_rail_ind_total.png',
            'weights': {
                0: 0.005,
                1000: 0.01,
                10000: 0.02,
                100000: 0.04,
                1000000: 0.08
            }
        },
    ]

    for spec in specs:
        print(spec['title'])
        # Read from excel
        excel_data = pd.read_excel(
            exposure_filename,
            sheet_name=spec['sheet_name']
        )
        lookup = {}
        for _, row in excel_data.iterrows():
            value = row[spec['val_col']]
            rpmin_curr = row['rpmin_curr']
            rpmin_fut = row['rpmin_fut']

            if spec['id_col'] == 'link':
                id_ = int(row[spec['id_col']])
            else:
                id_ = row[spec['id_col']]

            lookup[id_] = (value, rpmin_curr, rpmin_fut)

        curr = []
        fut = []
        for record in shpreader.Reader(spec['shape_filename']).records():
            id_ = record.attributes[spec['id_col']]
            value, rpmin_curr, rpmin_fut = lookup[id_]

            if rpmin_curr > 0:
                curr.append((record.geometry, value, rpmin_curr))

            if rpmin_fut > 0:
                fut.append((record.geometry, value, rpmin_fut))

        _, axes = plt.subplots(
            nrows=1,
            ncols=2,
            subplot_kw=dict(projection=proj_lat_lon),
            figsize=(10, 5),
            dpi=150)

        for ax, data, subtitle in zip(axes, [curr, fut], ["Current", "Future"]):
            ax.locator_params(tight=True)
            ax.set_extent(tz_extent, crs=proj_lat_lon)
            ax.set_title(subtitle)

            plot_basemap(ax, data_path)

            # Set color_map
            colors = plt.get_cmap('cool')
            color_map = plt.cm.ScalarMappable(
                cmap=colors, norm=matplotlib.colors.Normalize(vmin=0, vmax=1000))

            plot_color_map_weighted_network(
                ax, data, proj_lat_lon, color_map, spec['weights'])

        # Legend on first axis
        ax = axes[0]
        x_l = 28.8
        x_r = 29.5
        base_y = -9
        ax.text(
            x_l,
            base_y + 0.05,
            spec['legend_label'],
            horizontalalignment='left',
            transform=proj_lat_lon)

        prev_weight = None
        prev_width = None
        for (i, (weight, width)) in enumerate(sorted(spec['weights'].items())):
            if prev_width is None:
                prev_width = width
                prev_weight = weight
                continue

            label = '{}-{}'.format(prev_weight, weight)

            y = base_y - (i*0.5)
            line = LineString([(x_l, y), (x_r, y)])
            ax.add_geometries(
                [line.buffer(prev_width)],
                crs=proj_lat_lon,
                linewidth=0,
                edgecolor='#000000',
                facecolor='#000000',
                zorder=2)
            ax.text(
                x_r + 0.1,
                y - 0.15,
                label,
                horizontalalignment='left',
                transform=proj_lat_lon)

            prev_width = width
            prev_weight = weight

        # Last legend entry
        label = '>{}'.format(prev_weight)
        y = base_y - ((i+1)*0.5)
        line = LineString([(x_l, y), (x_r, y)])
        ax.add_geometries(
            [line.buffer(prev_width)],
            crs=proj_lat_lon,
            linewidth=0,
            edgecolor='#000000',
            facecolor='#000000',
            zorder=2)
        ax.text(
            x_r + 0.1,
            y - 0.15,
            label,
            horizontalalignment='left',
            transform=proj_lat_lon)

        # Add colorbar
        color_map._A = []  # hack in array to avoid error
        cbar = plt.colorbar(
            color_map, ax=axes.flat, fraction=0.03, pad=0.03, drawedges=False,
            orientation='vertical')
        cbar.outline.set_color("none")
        cbar.ax.set_ylabel('Return period (y)')

        plt.suptitle(spec['title'])
        output_filename = os.path.join(figures_path, spec['filename'])
        plt.savefig(output_filename)
        plt.close()


def plot_color_map_weighted_network(ax, data, proj, color_map, weights):
    """Plot line data to current map
    """
    for geom, value, rpmin in data:
        color = color_map.to_rgba(rpmin)

        step_value = 0
        for step in sorted(weights.keys()):
            if value > step:
                step_value = step

        ax.add_geometries(
            [geom.buffer(weights[step_value])],
            crs=proj,
            edgecolor=color,
            facecolor=color,
            linewidth=0,
            zorder=2)

if __name__ == '__main__':
    main()
