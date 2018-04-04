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

import numpy as np
from osgeo import gdal
import shapely.geometry

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')
inf_path = os.path.join(data_path, 'Infrastructure')
resource_path = os.path.join(base_path, 'resources')

states_filename = os.path.join(inf_path, 'Boundaries', 'ne_10m_admin_0_countries_lakes.shp')

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

# Flood Hazard
model = 'HadGEM2-ES'
return_period = 1000

hazard_filename = os.path.join(
    data_path,
    'tanzania_flood',
    model,
    'rcp6p0',
    '2030-2069',
    'inun_dynRout_RP_{:05d}_bias_corr_masked_Tanzania'.format(return_period),
    'inun_dynRout_RP_{:05d}_bias_corr_contour_Tanzania.tif'.format(return_period)
)

# Icons
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')
train_icon_filename = os.path.join(resource_path, 'train.png')

# Create figure
plt.figure(figsize=(6, 6), dpi=150)

proj_lat_lon = ccrs.PlateCarree()
ax = plt.axes([0.025, 0.1, 0.95, 0.92], projection=proj_lat_lon)
zoom_extent = [38.3, 39.3, -4.8, -5.6]
ax.set_extent(zoom_extent, crs=proj_lat_lon)

# Background
# Read in Tanzania outline
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes["ISO_A2"]
    if country_code == "TZ":
        tz_geom = record.geometry
ax.add_geometries([tz_geom], crs=proj_lat_lon, edgecolor='#d7d7d7', facecolor='#fafafaee', zorder=0)

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
        offset = 0.02
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
        offset = 0.02

        # Nudge airports which are next to ports
        if line['name'] in ('Bukoba Airport', 'Julius Nyerere International Airport'):
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

def get_data(filename):
    """Read in data (as array) and extent of each raster
    """
    gdal.UseExceptions()
    ds = gdal.Open(filename)
    data = ds.ReadAsArray()
    data[data < 0] = 0

    gt = ds.GetGeoTransform()

    # get the edge coordinates
    width = ds.RasterXSize
    height = ds.RasterYSize
    xres = gt[1]
    yres = gt[5]

    xmin = gt[0]
    xmax = gt[0] + (xres * width)
    ymin = gt[3] + (yres * height)
    ymax = gt[3]

    lat_lon_extent = (xmin, xmax, ymax, ymin)

    return data, lat_lon_extent

data, lat_lon = get_data(hazard_filename)

# Find global min/max to use for consistent color-mapping
min_val = np.min(data)
max_val = np.max(data)

colors = plt.get_cmap('Blues')
# colors.colors[0] = (1, 1, 1, 0)  # set zero values to transparent white - works for e.g. viridis colormap
colors._segmentdata['alpha'][0] = (0, 0, 0)  # set zero values to transparent white - works for LinearSegmentedColorMap

im = ax.imshow(data, extent=lat_lon, cmap=colors, vmin=min_val, vmax=max_val, zorder=1)

# Add colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.05, pad=0.01, drawedges=False, orientation='horizontal')
cbar.outline.set_color("none")
cbar.ax.set_xlabel('Flood depth (m)')

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

plt.title('Transport network nr Tanga with {}y floods ({} model)'.format(return_period, model))

# Add context
ax = plt.axes([0.704, 0.155, 0.275, 0.275], projection=proj_lat_lon)
tz_extent = (28.6, 41.4, -0.1, -13.2)
ax.set_extent(tz_extent, crs=proj_lat_lon)

# Tanzania
ax.add_geometries([tz_geom], crs=proj_lat_lon, edgecolor='white', facecolor='#d7d7d7')

# Neighbours
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes['ISO_A2']
    if country_code in ('BI', 'RW', 'CD', 'UG', 'KE', 'ZM', 'MW', 'MZ', 'SO'):
        geom = record.geometry
        ax.add_geometries([geom], crs=proj_lat_lon, edgecolor='white', facecolor='#efefef')

# Zoom extent: (37.5, 39.5, -8.25, -6.25)
x0, x1, y0, y1 = zoom_extent
box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
ax.add_geometries([box], crs=proj_lat_lon, edgecolor='#000000', facecolor='#d7d7d700')


output_filename = os.path.join(
    base_path,
    'figures',
    'multimodal_hazard_map.png'
)
plt.savefig(output_filename)
