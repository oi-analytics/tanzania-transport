"""Plot infrastructure exposure

Count map, histogram:
Edge exposure number of times exposed / number of models

Count map, histogram
per link, lowest return period (current euwatch) to which it is exposed
per link, lowest return period (across any model) to which it is exposed
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
    config = load_config()
    data_path = config['data_path']
    figures_path = config['figures_path']

    states_filename = os.path.join(data_path, 'Infrastructure', 'Boundaries',
                                'ne_10m_admin_0_countries_lakes.shp')

    # Roads
    road_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')

    # Rail
    rail_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_rail_spof_geom.shp')

    # Exposure
    exposure_filename = os.path.join(
        data_path, 'Analysis_results', 'tz_flood_stats_3.xlsx')

    proj_lat_lon = ccrs.PlateCarree()

    specs = [
        # tanroads_link_flooding: link: model_frequency,rpmin_curr,rpmin_fut
        {
            'sheet_name': 'tanroads_link_flooding',
            'shape_filename': road_filename,
            'id_col': 'link',
            'val_col': 'model_frequency',
            'legend_label': 'Proportion of models exposed',
            'filename': 'exposure_road_links_model_frequency.png',
            'title': 'Road link exposure to flooding'
        },
        {
            'sheet_name': 'tanroads_link_flooding',
            'shape_filename': road_filename,
            'id_col': 'link',
            'val_col': 'rpmin_curr',
            'legend_label': 'Return period (y)',
            'filename': 'exposure_road_links_rpmin_curr.png',
            'title': 'Road minimum current return period exposure'
        },
        {
            'sheet_name': 'tanroads_link_flooding',
            'shape_filename': road_filename,
            'id_col': 'link',
            'val_col': 'rpmin_fut',
            'legend_label': 'Return period (y)',
            'filename': 'exposure_road_links_rpmin_future.png',
            'title': 'Road minimum future return period exposure'
        },
        # rail_edge_flooding: id: model_frequency,rpmin_curr,rpmin_fut
        {
            'sheet_name': 'rail_edge_flooding',
            'shape_filename': rail_filename,
            'id_col': 'id',
            'val_col': 'model_frequency',
            'legend_label': 'Proportion of models exposed',
            'filename': 'exposure_rail_links_model_frequency.png',
            'title': 'Rail link exposure to flooding'
        },
        {
            'sheet_name': 'rail_edge_flooding',
            'shape_filename': rail_filename,
            'id_col': 'id',
            'val_col': 'rpmin_curr',
            'legend_label': 'Return period (y)',
            'filename': 'exposure_rail_links_rpmin_curr.png',
            'title': 'Rail minimum current return period exposure'
        },
        {
            'sheet_name': 'rail_edge_flooding',
            'shape_filename': rail_filename,
            'id_col': 'id',
            'val_col': 'rpmin_fut',
            'legend_label': 'Return period (y)',
            'filename': 'exposure_rail_links_rpmin_future.png',
            'title': 'Rail minimum future return period exposure'
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
        for i, row in excel_data.iterrows():
            value = row[spec['val_col']]
            if spec['id_col'] == 'link':
                id_ = int(row[spec['id_col']])
            else:
                id_ = row[spec['id_col']]

            if spec['val_col'] == 'model_frequency':
                # convert to ratio
                lookup[id_] = float(value) / 44
            else:
                lookup[id_] = value

        data = []
        for record in shpreader.Reader(spec['shape_filename']).records():
            value = lookup[record.attributes[spec['id_col']]]
            if spec['val_col'] == 'model_frequency':
                data.append((record.geometry, value))
            else:
                if value > 0:
                    data.append((record.geometry, value))

        ax = get_tz_axes()
        plot_basemap(ax, data_path)

        if spec['val_col'] == 'model_frequency':
            cmap_name = 'YlOrRd'
            max_value = 1
        else:
            cmap_name = 'YlOrRd_r'
            # max_value = max(value for geom, value in data)
            max_value = 1000

        plot_color_map_network(ax, data, proj_lat_lon, spec['legend_label'], cmap_name, max_value)

        output_filename = os.path.join(
            figures_path,
            spec['filename'])
        plt.savefig(output_filename)
        plt.close()


def plot_color_map_network(ax, data, proj, label, cmap_name, max_value):
    """Plot line data to current map
    """
    # Set color_map
    colors = plt.get_cmap(cmap_name)
    color_map = plt.cm.ScalarMappable(cmap=colors, norm=matplotlib.colors.Normalize(vmin=0, vmax=max_value))


    for geom, value in data:
        if value > 0:
            color = color_map.to_rgba(value)
        else:
            color = color_map.to_rgba(0)

        ax.add_geometries(
            [geom],
            crs=proj,
            edgecolor=color,
            facecolor='none',
            zorder=2)

    # Add colorbar
    color_map._A = []  # hack in array to avoid error
    cbar = plt.colorbar(color_map, ax=ax, fraction=0.05, pad=0.01, drawedges=False, orientation='horizontal')
    cbar.outline.set_color("none")
    cbar.ax.set_xlabel(label)

if __name__ == '__main__':
    main()
