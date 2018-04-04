"""Map border crossing nodes
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.legend_handler import HandlerBase
from matplotlib.image import BboxImage

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

# Input data
inf_path = os.path.join(data_path, 'Infrastructure')
resource_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources')


# Roads
road_filename = os.path.join(inf_path, 'Roads', 'road_shapefiles',
                             'tanroads_nodes_main_all_2017_adj.shp')

# Railways
railway_filename = os.path.join(inf_path, 'Railways', 'railway_shapefiles',
                                'tanzania-rail-nodes-processed.shp')

# Ports
ports_filename = os.path.join(inf_path, 'Ports', 'port_shapefiles', 'tz_port_nodes.shp')

# Airports
airport_filename = os.path.join(inf_path, 'Airports', 'airport_shapefiles', 'tz_od_airport_nodes.shp')

# Output
output_filename = os.path.join(figures_path, 'border_crossings_map.png')

# Icons
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')

# Create figure
ax = get_tz_axes()

proj_lat_lon = ccrs.PlateCarree()
proj_3857 = ccrs.epsg(3857)

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

tz_border_points_info = {
    'air': {
        'HTAR': 'Arusha ',
        'HTDA': 'Julius Nyerere',
        'HTKJ': 'Kilimanjaro ',
    },
    'road': {
         7507: 'Sirari',
         6306: 'Namanga',
         4028: 'Kasumulu',
         8406: 'Rusumo',
         5822: 'Holili',
         5313: 'Horohoro',
         4012: 'Tunduma',
         8529: 'Kabanga',
         8407: 'Mutukula',
    },
    'port': {
        'port_1': 'Dar es Salaam port',
        'port_2': 'Mtwara',
        'port_3': 'Tanga',
        'port_4': 'Mwanza',
        'port_9': 'Kigoma',
    },
    'rail': {
        'rail_node_16': 'Tunduma Station',
    }
}

node_buffer = 0.08

# Roads
road_node_ids = tz_border_points_info['road'].keys()
xs = []
ys = []
for record in shpreader.Reader(road_filename).records():
    id_ = record.attributes['nodenumber']
    if id_ in road_node_ids:
        geom = record.geometry
        x = geom.x
        y = geom.y
        xs.append(x)
        ys.append(y)
        ax.text(
            x + node_buffer, y + node_buffer,
            tz_border_points_info['road'][id_],
            transform=proj_lat_lon,
            zorder=4,
            size=8
        )
ax.scatter(xs, ys, facecolor='#d1170a', s=11, zorder=3)

# Railways
rail_node_ids = tz_border_points_info['rail'].keys()
xs = []
ys = []
for record in shpreader.Reader(railway_filename).records():
    id_ = record.attributes['id']
    if id_ in rail_node_ids:
        geom = record.geometry
        x = geom.x - 0.1
        y = geom.y
        xs.append(x)
        ys.append(y)
        ax.text(x + node_buffer, y + node_buffer, tz_border_points_info['rail'][id_], transform=proj_lat_lon, zorder=4, ha='right', size=8)
ax.scatter(xs, ys, facecolor='#33a02c', s=11, zorder=3)

# Ports
ferry_im = plt.imread(boat_icon_filename)
port_node_ids = tz_border_points_info['port'].keys()
for record in shpreader.Reader(ports_filename).records():
    id_ = record.attributes['id']
    if id_ in port_node_ids:
        geom = record.geometry
        x = geom.x
        y = geom.y
        offset = 0.15
        img_extent = (
            x - offset,
            x + offset,
            y - offset,
            y + offset
        )
        ax.imshow(ferry_im, origin='upper', extent=img_extent, transform=proj_lat_lon, zorder=4)

        ax.text(x + offset/2, y + offset/2, tz_border_points_info['port'][id_], transform=proj_lat_lon, zorder=4, size=8)

# Airports
plane_im = plt.imread(plane_icon_filename)
air_node_ids = tz_border_points_info['air'].keys()

plane_im = plt.imread(plane_icon_filename)
for record in shpreader.Reader(airport_filename).records():
    geom = record.geometry
    x = geom.x
    y = geom.y

    # Offset defines icon size
    offset = 0.15

    name = record.attributes['name']
    name = name.replace(' Airport', '')
    name = name.replace(' International', '')

    id_ = record.attributes['ident']
    if id_ not in air_node_ids:
        continue

    # Nudge airports which are next to ports
    if name == 'Julius Nyerere':
        x -= 0.2

    img_extent = (
        x - offset,
        x + offset,
        y - offset,
        y + offset
    )
    ax.imshow(plane_im, origin='upper', extent=img_extent, transform=proj_lat_lon, zorder=5)

    if name == 'Arusha':
        y += 0.07
        x += 0.05
        align = 'right'
    elif name == 'Julius Nyerere':
        y -= 0.21
        x -= 0.05
        align = 'right'
    else:
        y -= 0.21
        x += 0.05
        align = 'right'

    ax.text(x, y, tz_border_points_info['air'][id_], transform=proj_lat_lon, zorder=4, ha=align, size=8)

# Legend
class HandlerImage(HandlerBase):
    """Use image in legend

    Adapted from https://stackoverflow.com/questions/42155119/replace-matplotlib-legends-labels-with-image
    """
    def __init__(self, path, space=15, offset=5):
        self.space = space
        self.offset = offset
        self.image_data = plt.imread(path)
        super(HandlerImage, self).__init__()

    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        scale = 1.5
        bb = Bbox.from_bounds(
            xdescent + self.offset,
            ydescent,
            height * self.image_data.shape[1] / self.image_data.shape[0] * scale,
            height * scale)

        tbb = TransformedBbox(bb, trans)
        image = BboxImage(tbb)
        image.set_data(self.image_data)

        self.update_prop(image, orig_handle, legend)
        return [image]

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
