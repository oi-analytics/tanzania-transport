"""Generate transport corridor map, showing major routes and nodes for each mode
"""
# pylint: disable=C0103
import csv
import os

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
trunk_road_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'trunk_roads_2017.shp')
regional_road_filename = os.path.join(inf_path, 'Roads', 'Tanroads_flow_shapefiles', 'region_roads_2017.shp')

# Railways
railway_nodes_filename = os.path.join(inf_path, 'Railways', 'tanzania-rail-nodes-processed.shp')
railway_ways_filename = os.path.join(inf_path, 'Railways', 'tanzania-rail-ways-processed.shp')

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

# Major roads
for record in shpreader.Reader(trunk_road_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#d1170a',
        facecolor='none',
        zorder=2)

# Regional roads
for record in shpreader.Reader(regional_road_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#ed9a36',
        facecolor='none',
        zorder=2)

# Railways
for record in shpreader.Reader(railway_ways_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#33a02c',
        facecolor='none',
        zorder=3)

# Ferry ports
ferry_im = plt.imread(boat_icon_filename)
with open(ports_filename, 'r', encoding="utf-8") as fh:
    r = csv.DictReader(fh)
    for record in r:
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

# Airports
plane_im = plt.imread(plane_icon_filename)
with open(airport_filename, 'r') as airports_file:
    reader = csv.DictReader(airports_file)
    for line in reader:
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
major_road_handle = mpatches.Patch(color='#d1170a')
regional_road_handle = mpatches.Patch(color='#ed9a36')
rail_handle = mpatches.Patch(color='#33a02c')

plt.legend(
    [plane_handle, boat_handle, major_road_handle, regional_road_handle, rail_handle],
    ["Airport", "Port", "Trunk Road", "Regional Road", "Railway"],
    handler_map={
        boat_handle: HandlerImage(boat_icon_filename),
        plane_handle: HandlerImage(plane_icon_filename),
    },
    loc='lower left')

plt.title('Major Transport Corridors in Tanzania')


output_filename = os.path.join(
    base_path,
    'figures',
    'corridor_map.png'
)
plt.savefig(output_filename)
