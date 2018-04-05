"""Map border crossing nodes
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
resource_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources')

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

# Output
output_filename = os.path.join(figures_path, 'border_crossings_map.png')


# Create figure
ax = get_tz_axes()

proj_lat_lon = ccrs.PlateCarree()

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

plot_border_crossings(ax, nodes, resource_path)

# Legend
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')

boat_handle = mpatches.Patch()
plane_handle = mpatches.Patch()
road_handle = mpatches.Patch(color='#d1170a')
rail_handle = mpatches.Patch(color='#33a02c')

plt.legend(
    [plane_handle, boat_handle, road_handle, rail_handle],
    ["Airport", "Port", "Road", "Railway"],
    handler_map={
        boat_handle: HandlerImage(boat_icon_filename),
        plane_handle: HandlerImage(plane_icon_filename),
    },
    loc='lower left')

save_fig(output_filename)
