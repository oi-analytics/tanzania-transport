"""Generate transport corridor map, showing major routes and nodes for each mode
"""
# pylint: disable=C0103
import csv
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

# TZ_TransNet_Roads, clipped to Tanzania
trunk_road_filename = os.path.join(inf_path, 'Roads', 'road_shapefiles', 'tanroads_nodes_main_all_2017_adj.shp')

# Railways
railway_nodes_filename = os.path.join(inf_path, 'Railways', 'railway_shapefiles', 'tanzania-rail-nodes-processed.shp')
railway_ways_filename = os.path.join(inf_path, 'Railways', 'railway_shapefiles', 'tanzania-rail-ways-processed.shp')

# Ports
ports_filename = os.path.join(inf_path, 'Ports', 'port_shapefiles', 'tz_port_nodes.shp')
port_edges_filename = os.path.join(inf_path, 'Ports', 'port_shapefiles', 'tz_port_edges.shp')

# Airports
airport_filename = os.path.join(inf_path, 'Airports', 'airport_shapefiles', 'tz_od_airport_nodes.shp')

# Multi-modal
multimodal_filename = os.path.join(inf_path, 'Multi_Modal', 'multi_shapefiles', 'tz_multi_modal_edges.shp')

output_filename = os.path.join(figures_path, 'multimodal_map.png')

# Icons
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')

# Create figure
plt.figure(figsize=(7, 7), dpi=300)
proj_lat_lon = ccrs.PlateCarree()
ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)
x0 = 39.17
x1 = 39.32
y0 = -6.78
y1 = -6.93
ax.set_extent([x0, x1, y0, y1], crs=proj_lat_lon)
set_ax_bg(ax)

proj_lat_lon = ccrs.PlateCarree()

# Background
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=5, location=(0.8,0.02))

# Roads
for record in shpreader.Reader(trunk_road_filename).records():
    geom = record.geometry
    class_ = record.attributes['roadclass']
    if class_ == 'T':
        edgecolor = '#d1170a'
    else:
        edgecolor = '#ed9a36'

    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor=edgecolor,
        facecolor='none',
        zorder=2)

# Railways
for record in shpreader.Reader(railway_ways_filename).records():
    geom = record.geometry
    if record.attributes['line_name'] != 'Unknown':
        ax.add_geometries(
            [geom],
            crs=proj_lat_lon,
            edgecolor='#33a02c',
            facecolor='none',
            zorder=3)

# Ferry routes
for record in shpreader.Reader(port_edges_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#051591',
        facecolor='none',
        zorder=3)

# Multi-modal links
for record in shpreader.Reader(multimodal_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='#051591',
        facecolor='none',
        zorder=3)



# Offset defines icon size
offset = 0.002

# Ferry ports
ferry_im = plt.imread(boat_icon_filename)
for record in shpreader.Reader(ports_filename).records():
    geom = record.geometry
    x = geom.x
    y = geom.y
    img_extent = (
        x - offset,
        x + offset,
        y - offset,
        y + offset
    )
    ax.imshow(ferry_im, origin='upper', extent=img_extent, transform=proj_lat_lon, zorder=4)
    ax.text(x + offset/2, y + offset/2, record.attributes['name'],
            transform=proj_lat_lon, zorder=4, ha='left', size=8)

# Airports
plane_im = plt.imread(plane_icon_filename)
for record in shpreader.Reader(airport_filename).records():
    geom = record.geometry
    x = geom.x
    y = geom.y
    img_extent = (
        x - offset,
        x + offset,
        y - offset,
        y + offset
    )
    ax.imshow(plane_im, origin='upper', extent=img_extent, transform=proj_lat_lon, zorder=5)
    ax.text(x + offset, y + offset, record.attributes['name'],
            transform=proj_lat_lon, zorder=4, ha='left', size=8)

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
multi_handle =  mpatches.Patch(color='#051591')

plt.legend(
    [plane_handle, boat_handle, major_road_handle, regional_road_handle, rail_handle, multi_handle],
    ["Airport", "Port", "Trunk Road", "Regional Road", "Railway", "Multi-modal link"],
    handler_map={
        boat_handle: HandlerImage(boat_icon_filename),
        plane_handle: HandlerImage(plane_icon_filename),
    },
    loc='lower left')

save_fig(output_filename)
