"""Generate transport corridor map, showing major routes and nodes for each mode
"""
# pylint: disable=C0103
import csv
import os

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
resource_path = os.path.join(base_path, 'resources')

# TZ_TransNet_Roads, clipped to Tanzania
road_filename = os.path.join(data_path, 'Road_data', 'TZ_TransNet_Roads.shp')

# TransNet_Railroads
railway_filename = os.path.join(data_path, 'Railway_data', 'TZ_TransNet_Railroads.shp')

# TZ_TransNet_FerryTerminals and TZ_TransNet_FerryRoutes
ferry_path = os.path.join(data_path, 'Port_data')
ferry_terminals_filename = os.path.join(ferry_path, 'TZ_TransNet_FerryTerminals.shp')
ferry_routes_filename = os.path.join(ferry_path, 'TZ_TransNet_FerryRoutes.shp')

# tanzania_airports from ourairports.com
airport_filename = os.path.join(data_path, 'Airport_data', 'tanzania_airports.csv')

# Natural Earth countries
states_filename = os.path.join(data_path, 'Boundary_datasets',
                               'ne_10m_admin_0_countries_lakes.shp')

# Icons
boat_icon_filename = os.path.join(resource_path, 'boat.png')
plane_icon_filename = os.path.join(resource_path, 'plane.png')
train_icon_filename = os.path.join(resource_path, 'train.png')

# Create figure
plt.figure(figsize=(10, 10), dpi=150)

proj_lat_lon = ccrs.PlateCarree()
proj_3857 = ccrs.epsg(3857)
ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)
x0 = 28.6
x1 = 41.4
y0 = 0.5
y1 = -12.5
ax.set_extent([x0, x1, y0, y1], crs=proj_lat_lon)

# Africa, for Tanzania and neighbours
for record in shpreader.Reader(states_filename).records():
    if record.attributes['CONTINENT'] != 'Africa':
        continue

    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_lat_lon,
        edgecolor='white',
        facecolor='#efefef',
        zorder=1)

# Major roads
for record in shpreader.Reader(road_filename).records():
    geom = record.geometry
    country = record.attributes["Country"]
    if country == "Tanzania":
        ax.add_geometries(
            [geom],
            crs=proj_3857,
            edgecolor='#1f78b4',
            facecolor='none',
            zorder=2)

# Railways
for record in shpreader.Reader(railway_filename).records():
    geom = record.geometry
    country = record.attributes["Country"]
    if country == "Tanzania":
        ax.add_geometries(
            [geom],
            crs=proj_3857,
            edgecolor='#33a02c',
            facecolor='none',
            zorder=3)

# Ferry routes
for record in shpreader.Reader(ferry_routes_filename).records():
    geom = record.geometry
    ax.add_geometries(
        [geom],
        crs=proj_3857,
        edgecolor='#ff7f00',
        facecolor='none',
        zorder=3)

# Ferry ports
ferry_im = plt.imread(boat_icon_filename)
for record in shpreader.Reader(ferry_terminals_filename).records():
    geom = record.geometry
    offset = 15000
    img_extent = (
        geom.x - offset,
        geom.x + offset,
        geom.y - offset,
        geom.y + offset
    )
    ax.imshow(ferry_im, origin='upper', extent=img_extent, transform=proj_3857, zorder=4)

# Airports
plane_im = plt.imread(plane_icon_filename)
with open(airport_filename, 'r') as airports_file:
    reader = csv.DictReader(airports_file)
    for line in reader:
        x = float(line['longitude_deg'])
        y = float(line['latitude_deg'])

        # Small airports with smaller icon
        if line['type'] == 'large_airport':
            offset = 0.2
        elif line['type'] == 'medium_airport':
            offset = 0.125
        else:
            offset = 0.1

        # Nudge airports which are next to ferry ports
        if line['name'] == 'Bukoba Airport':
            x -= 0.25
        elif line['name'] == 'Musoma Airport':
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
road_handle = mpatches.Patch(color='#1f78b4')
rail_handle = mpatches.Patch(color='#33a02c')
ferry_handle = mpatches.Patch(color='#ff7f00')

plt.legend(
    [plane_handle, boat_handle, road_handle, rail_handle, ferry_handle],
    ["Airport", "Ferry Terminal", "Major Road", "Railway", "Ferry route"],
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
