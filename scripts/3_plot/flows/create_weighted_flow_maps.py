"""All networks, showing link weights used by OD flows
"""
# pylint: disable=C0103
import os
import sys

from collections import OrderedDict

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from shapely.geometry import LineString

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

# Input data
inf_path = os.path.join(data_path, 'Infrastructure')
stats_path = os.path.join(data_path, 'results', 'result_shapefiles')

# Icons
resource_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources')
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')

# Border crossings
nodes = {
    "road": read_border_geoms_and_labels(
        "road",
        os.path.join(
            inf_path, 'Roads', 'road_shapefiles', 'tanroads_nodes_main_all_2017_adj.shp')
    ),
    "rail": read_border_geoms_and_labels(
        "rail",
        os.path.join(
            inf_path, 'Railways', 'railway_shapefiles', 'tanzania-rail-nodes-processed.shp')
    ),
    "port": read_border_geoms_and_labels(
        "port",
        os.path.join(
            inf_path, 'Ports', 'port_shapefiles', 'tz_port_nodes.shp')
    ),
    "air": read_border_geoms_and_labels(
        "air",
        os.path.join(
            inf_path, 'Airports', 'airport_shapefiles', 'tz_od_airport_nodes.shp')
    )
}

# Read outputs
scenario_to_suffix = {
    "current": "2016",
    "future": "fut_opt_trend_2030"
}
stats = {}
for sector in ["port", "rail", "road"]:
    for scenario in ["current", "future"]:
        filename = os.path.join(stats_path, "{}_stats_{}.shp".format(
            sector,
            scenario_to_suffix[scenario]
        ))
        if sector == "road":
            stats[("road_trunk", scenario)] = [
                record
                for record in shpreader.Reader(filename).records()
                if record.attributes['roadclass'] == 'T'
            ]
            stats[("road_regional", scenario)] = [
                record
                for record in shpreader.Reader(filename).records()
                if record.attributes['roadclass'] != 'T'
            ]
        else:
            stats[(sector, scenario)] = list(shpreader.Reader(filename).records())

plots = [
    ("AADF (thousand tonnes)", "tons"),
    ("Cost (million USD)", "cost"),
    ('% of OD flows', "centr"),
]
column_label_divisors = {
    "tons": 1000,
    "cost": 1000000,
    "centr": 1,
}
sector_groups = [
    ["road_regional", "road_trunk"],
    ["rail", "port"]
]
sector_colors = {
    "port": '#051591',
    "road_trunk": '#d1170a',
    "road_regional": '#ed9a36',
    "rail": '#33a02c',
}
proj_lat_lon = ccrs.PlateCarree()

for scenario in ["current_own_range", "current", "future"]:
    for legend_label, column in plots:
        for sectors in sector_groups:
            print(scenario, column, sectors)
            ax = get_tz_axes()
            plot_basemap(ax, data_path)
            plot_basemap_labels(ax, data_path)
            scale_bar(ax, length=100, location=(0.925,0.02))

            plot_border_crossings(ax, nodes, resource_path, show_labels=False)

            if scenario == "current_own_range":
                min_weight = round_sf(min(
                    min(
                        record.attributes[column]
                        for record
                        in stats[(sector, "current")]
                    )
                    for sector in sectors
                ))
                max_weight = round_sf(max(
                    max(
                        record.attributes[column]
                        for record
                        in stats[(sector, "current")]
                    )
                    for sector in sectors
                ))

            else:
                # consider both current and future
                min_weight = round_sf(min(
                    min(
                        record.attributes[column]
                        for record
                        in stats[(sector, scen)]
                    )
                    for sector in sectors
                    for scen in ["current", "future"]
                ))
                max_weight = round_sf(max(
                    max(
                        record.attributes[column]
                        for record
                        in stats[(sector, scen)]
                    )
                    for sector in sectors
                    for scen in ["current", "future"]
                ))
            print(min_weight, max_weight)

            # generate weight bins
            width_by_range = OrderedDict()
            n_steps = 9
            width_step = 0.01

            mins = np.linspace(min_weight, max_weight, n_steps)

            maxs = list(mins)
            maxs.append(max_weight*10)
            maxs = maxs[1:]

            assert len(maxs) == len(mins)

            for i, (min_, max_) in enumerate(zip(mins, maxs)):
                width_by_range[(min_, max_)] = (i+1) * width_step


            # for geom lookup
            if scenario == "current_own_range":
                scenario_key = "current"
            else:
                scenario_key = scenario

            for sector in sectors:
                # assign geoms to weight bins
                geoms_by_range = {}
                for value_range in width_by_range:
                    geoms_by_range[value_range] = []

                for record in stats[(sector, scenario_key)]:
                    val = record.attributes[column]
                    geom = record.geometry
                    for nmin, nmax in geoms_by_range:
                        if nmin <= val and val < nmax:
                            geoms_by_range[(nmin, nmax)].append(geom)

                # plot
                for range_, width in width_by_range.items():
                    ax.add_geometries(
                        [geom.buffer(width) for geom in geoms_by_range[range_]],
                        crs=proj_lat_lon,
                        edgecolor='none',
                        facecolor=sector_colors[sector],
                        zorder=2)

            x_l = 38.0
            x_r = x_l + 0.4
            base_y = -0.1
            y_step = 0.4
            y_text_nudge = 0.1
            x_text_nudge = 0.1

            ax.text(
                x_l,
                base_y + y_step - y_text_nudge,
                legend_label,
                horizontalalignment='left',
                transform=proj_lat_lon,
                size=8)

            divisor = column_label_divisors[column]
            for (i, ((nmin, nmax), width)) in enumerate(width_by_range.items()):
                y = base_y - (i*y_step)
                line = LineString([(x_l, y), (x_r, y)])
                ax.add_geometries(
                    [line.buffer(width)],
                    crs=proj_lat_lon,
                    linewidth=0,
                    edgecolor='#000000',
                    facecolor='#000000',
                    zorder=2)
                if nmin == max_weight:
                    label = '>{:.2f}'.format(max_weight/divisor)
                else:
                    label = '{:.2f}-{:.2f}'.format(nmin/divisor, nmax/divisor)
                ax.text(
                    x_r + x_text_nudge,
                    y - y_text_nudge,
                    label,
                    horizontalalignment='left',
                    transform=proj_lat_lon,
                    size=8)

            boat_handle = mpatches.Patch()
            plane_handle = mpatches.Patch()
            road_handle = mpatches.Patch(color=sector_colors['road_trunk'])
            regional_handle = mpatches.Patch(color=sector_colors['road_regional'])
            rail_handle = mpatches.Patch(color=sector_colors['rail'])
            port_handle = mpatches.Patch(color=sector_colors['port'])

            plt.legend(
                [
                    plane_handle, boat_handle, road_handle,
                    regional_handle, rail_handle, port_handle],
                [
                    "Airport", "Port", "Trunk Roads",
                    "Regional Roads", "Rail", "Waterway"
                ],
                handler_map={
                    boat_handle: HandlerImage(boat_icon_filename),
                    plane_handle: HandlerImage(plane_icon_filename),
                },
                loc='lower left')

            output_filename = os.path.join(
                figures_path,
                "flow_weights_{}_{}_{}.png".format(
                    "_".join(sectors),
                    column,
                    scenario
                )
            )
            plt.savefig(output_filename)
            plt.close()
