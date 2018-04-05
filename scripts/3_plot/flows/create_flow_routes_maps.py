"""All networks, highlighting routes used by OD flows
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

# Read flows
stats = {}
for sector in ["port", "rail", "road"]:
    filename = os.path.join(stats_path, "{}_stats_2016.shp".format(
        sector
    ))
    if sector == "road":
        stats["road_trunk"] = [
            record
            for record in shpreader.Reader(filename).records()
            if record.attributes['roadclass'] == 'T'
        ]
        stats["road_regional"] = [
            record
            for record in shpreader.Reader(filename).records()
            if record.attributes['roadclass'] != 'T'
        ]
    else:
        stats[sector] = list(shpreader.Reader(filename).records())

# Plot maps
plots = [
    ("Transit", "tr_ftype"),
    ("Import/export", "imexp_ftyp"),
    ("Domestic", "d_ftype"),
]
sector_colors = {
    "port": '#051591',
    "road_trunk": '#d1170a',
    "road_regional": '#ed9a36',
    "rail": '#33a02c',
}

proj_lat_lon = ccrs.PlateCarree()

for label, column in plots:
    print(label)
    ax = get_tz_axes()
    plot_basemap(ax, data_path)
    plot_basemap_labels(ax, data_path)
    plot_border_crossings(ax, nodes, resource_path, show_labels=False)

    for sector in ["port", "rail", "road_trunk", "road_regional"]:
        fg_geoms = [
            record.geometry
            for record in stats[sector]
            if record.attributes[column]
        ]
        ax.add_geometries(
            fg_geoms,
            crs=proj_lat_lon,
            edgecolor=sector_colors[sector],
            alpha=1,
            facecolor='none'
        )
        bg_geoms = [
            record.geometry
            for record in stats[sector]
            if not record.attributes[column]
        ]
        ax.add_geometries(
            bg_geoms,
            crs=proj_lat_lon,
            edgecolor=sector_colors[sector],
            alpha=0.2,
            facecolor='none'
        )

    # Legend
    boat_icon_filename = os.path.join(resource_path, 'boat.png')
    plane_icon_filename = os.path.join(resource_path, 'plane.png')

    boat_handle = mpatches.Patch()
    plane_handle = mpatches.Patch()
    road_handle = mpatches.Patch(color=sector_colors['road_trunk'])
    road_regional_handle = mpatches.Patch(color=sector_colors['road_regional'])
    rail_handle = mpatches.Patch(color=sector_colors['rail'])
    port_handle = mpatches.Patch(color=sector_colors['port'])

    plt.legend(
        [plane_handle, boat_handle, road_handle, road_regional_handle, rail_handle, port_handle],
        ["Airport", "Port", "Trunk Roads", "Regional Roads", "Rail", "Waterway"],
        handler_map={
            boat_handle: HandlerImage(boat_icon_filename),
            plane_handle: HandlerImage(plane_icon_filename),
        },
        loc='lower left')

    output_filename = os.path.join(figures_path, "flow_routes_{}.png".format(
        column.replace("_ftype", "")
    ))
    plt.savefig(output_filename)
    plt.close()
