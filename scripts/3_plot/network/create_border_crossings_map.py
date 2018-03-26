"""Map border crossing nodes
"""
# pylint: disable=C0103
import csv
import os
import re

from utils import plot_pop, plot_countries, plot_regions

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.legend_handler import HandlerBase
from matplotlib.image import BboxImage

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')
inf_path = os.path.join(data_path, 'Infrastructure')
resource_path = os.path.join(base_path, 'resources')

# TZ_TransNet_Roads, clipped to Tanzania
road_nodes_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'nodes_2017.shp')

# Railways
railway_nodes_filename = os.path.join(inf_path, 'Railways', 'tanzania-rail-nodes-processed.shp')

# Ports
ports_filename = os.path.join(inf_path, 'Ports', 'TZ_ports.csv')

# Airports
airport_filename = os.path.join(inf_path, 'Airports', 'TZ_airport_node_flows.csv')

# Icons
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')
train_icon_filename = os.path.join(resource_path, 'train.png')

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

tz_border_points_info = {
    'air': [
        ('Arusha airport', 'HTAR'),
        ('Dar es Salaam Intl. airport', 'HTDA'),
        ('Kilimanjaro Intl. airport', 'HTKJ'),
        ('Mwanza airport', 'HTMW')
    ],
    'road': [
        ('Sirari', 7507),
        ('Namanga', 6306),
        ('Kasumulu', 4028),
        ('Rusumo', 8406),
        ('Holili', 5822),
        ('Horohoro', 5313),
        ('Tunduma', 4012),
        ('Kabanga', 8529),
        ('Mutukula', 8407),
    ],
    'port': [
        ('Dar es Salaam port', '1'),
        ('Mtwara', '2'),
        ('Tanga port', '3'),
        ('Mwanza port', '4'),
        ('Kigoma port', '9'),
    ],
    'rail': [
        ('Tunduma rail station', 'rail_node_16'),
    ]
}

node_buffer = 0.1

# Roads
road_node_ids = [node_id for node, node_id in tz_border_points_info['road']]
for record in shpreader.Reader(road_nodes_filename).records():
    if record.attributes['NodeNumber'] in road_node_ids:
        geom = record.geometry
        ax.add_geometries(
            [geom.buffer(node_buffer)],
            crs=proj_lat_lon,
            edgecolor='#d1170a',
            facecolor='#d1170a',
            zorder=2)

        x, y, x1, y1 = geom.bounds
        ax.text(
            x + node_buffer, y + node_buffer,
            re.sub(
                r'\(.*\)',
                '',
                record.attributes['NodeName'].title(),
            ),
            transform=proj_lat_lon,
            zorder=4
        )

# Railways
rail_node_ids = [node_id for node, node_id in tz_border_points_info['rail']]
for record in shpreader.Reader(railway_nodes_filename).records():
    if record.attributes['id'] in rail_node_ids:
        geom = record.geometry
        ax.add_geometries(
            [geom.buffer(node_buffer)],
            crs=proj_lat_lon,
            edgecolor='#33a02c',
            facecolor='#33a02c',
            zorder=3)

        x, y, x1, y1 = geom.bounds
        ax.text(x + node_buffer, y + node_buffer, record.attributes['name'] + ' Station', transform=proj_lat_lon, zorder=4, ha='right')

# Ports
ferry_im = plt.imread(boat_icon_filename)
port_node_ids = [node_id for node, node_id in tz_border_points_info['port']]
with open(ports_filename, 'r', encoding="utf-8-sig") as fh:
    r = csv.DictReader(fh)
    for record in r:
        if record['id'] in port_node_ids:
            x = float(record['longitude'])
            y = float(record['latitude'])
            offset = 0.15
            img_extent = (
                x - offset,
                x + offset,
                y - offset,
                y + offset
            )
            ax.imshow(ferry_im, origin='upper', extent=img_extent, transform=proj_lat_lon, zorder=4)

            ax.text(x + offset, y + offset, record['name'], transform=proj_lat_lon, zorder=4)

# Airports
plane_im = plt.imread(plane_icon_filename)
air_node_ids = [node_id for node, node_id in tz_border_points_info['air']]
with open(airport_filename, 'r') as airports_file:
    reader = csv.DictReader(airports_file)
    for line in reader:
        if line['ident'] in air_node_ids:
            x = float(line['longitude_deg'])
            y = float(line['latitude_deg'])

            # Offset defines icon size
            offset = 0.15

            # Nudge airports which are next to ports
            if line['name'] in ('Bukoba Airport', 'Julius Nyerere International Airport', 'Mtwara Airport'):
                x -= 0.2
            elif line['name'] in ('Musoma Airport', 'Kigoma Airport'):
                x += 0.2
            elif line['name'] == 'Mwanza Airport':
                x += 0.2
                y -= 0.1

            img_extent = (
                x - offset,
                x + offset,
                y - offset,
                y + offset
            )
            ax.imshow(plane_im, origin='upper', extent=img_extent, transform=proj_lat_lon, zorder=5)

            name = line['name']
            if name == 'Mwanza Airport':
                continue

            if name in [
                'Julius Nyerere International Airport',
                'Kilimanjaro International Airport',
                'Abeid Amani Karume International Airport',
                'Mbeya Airport',
                'Pemba Airport',
                ]:
                y -= 0.35
            else:
                y += 0.05

            if name in [
                'Abeid Amani Karume International Airport',
                'Mtwara Airport',
                'Julius Nyerere International Airport',
                'Lake Manyara Airport',
                'Mafia Island Airport',
                'Pemba Airport',
                'Tanga Airport',
                'Songwe Airport',
                'Dodoma Airport'
                ]:
                x -= 0.05
                align = 'right'
            else:
                x += 0.05
                align = 'left'

            name = name.replace(' Airport', '')
            name = name.replace(' International', '')
            ax.text(x, y, name, transform=proj_lat_lon, zorder=4, ha=align)

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

plt.title('Major Border Crossings in Tanzania')


output_filename = os.path.join(
    base_path,
    'figures',
    'border_crossings_map.png'
)
plt.savefig(output_filename)
