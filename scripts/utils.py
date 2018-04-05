"""Shared plotting functions
"""
import json
import os

from boltons.iterutils import pairwise
from geopy.distance import vincenty
from osgeo import gdal
from matplotlib.colors import LogNorm, ListedColormap, BoundaryNorm
from matplotlib.image import BboxImage
from matplotlib.legend_handler import HandlerBase
from matplotlib.transforms import Bbox, TransformedBbox

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

def load_config():
    """Read config.json
    """
    with open('config.json', 'r') as config_fh:
        config = json.load(config_fh)
    return config


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


def get_tz_axes():
    """Setup plot figure and return Tanzania axes
    """
    plt.figure(figsize=(7, 7), dpi=300)
    proj_lat_lon = ccrs.PlateCarree()
    ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)
    x0 = 28.6
    x1 = 41.4
    y0 = 0.5
    y1 = -12.5
    ax.set_extent([x0, x1, y0, y1], crs=proj_lat_lon)
    set_ax_bg(ax)
    return ax


def hazard_legend(im, ax):
    # Add colorbar
    cbar = plt.colorbar(
        im, ax=ax, fraction=0.05, pad=0.04, drawedges=False,
        shrink=0.9, orientation='horizontal',
        ticks=[0.5, 1, 1.5, 2, 998],
        boundaries=[0.01,0.5,1,1.5,2,998]
    )
    cbar.ax.set_xticklabels(["0.5", "1.0", "1.5", "2.0", ">2.0"])
    cbar.outline.set_color("none")
    cbar.ax.set_xlabel('Flood depth (m)')


def get_hazard_cmap_norm():
    cmap = ListedColormap(['none', '#d8efff', '#bfe4ff', '#93d4ff', '#2d8ccb', '#00519e'])
    norm = BoundaryNorm([0, 0.01, 0.5, 1, 1.5, 2, 998], cmap.N)
    return cmap, norm


def set_ax_bg(ax):
    ax.background_patch.set_facecolor('#c6e0ff')


def save_fig(output_filename):
    plt.savefig(output_filename)
    plt.savefig(output_filename.replace("png", "svg"))


def plot_basemap(ax, data_path):
    """Plot countries and regions background
    """
    proj = ccrs.PlateCarree()

    states_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_0_countries_lakes.shp'
    )

    states_over_lakes_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_0_countries.shp'
    )

    provinces_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_1_states_provinces_lakes.shp'
    )

    lakes_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_lakes.shp'
    )

    # Neighbours
    for record in shpreader.Reader(states_filename).records():
        country_code = record.attributes['ISO_A2']
        if country_code in ('BI', 'RW', 'CD', 'UG', 'KE', 'ZM', 'MW', 'MZ', 'SO'):
            geom = record.geometry
            ax.add_geometries(
                [geom],
                crs=proj,
                edgecolor='white',
                facecolor='#e0e0e0',
                zorder=1)

    # Regions
    for record in shpreader.Reader(provinces_filename).records():
        country_code = record.attributes['iso_a2']
        if country_code == 'TZ':
            geom = record.geometry
            ax.add_geometries([geom], crs=proj, edgecolor='#ffffff', facecolor='#d2d2d2')

    # Lakes
    for record in shpreader.Reader(lakes_filename).records():
        name = record.attributes['name']
        geom = record.geometry

        if name in (
                'Lake Victoria',
                'Lake Tanganyika',
                'Lake Malawi',
                'Lake Kivu',
                'Lake Edward',
                'Lake Rukwa',
                'Lake Bunyoni',
                'Lake Natron',
                'Lake Manyara',
                'Lake Lembeni',
                'Lake Eyasi'):
            ax.add_geometries(
                [geom],
                crs=proj,
                edgecolor='none',
                facecolor='#c6e0ff',
                zorder=1)

    # Tanzania, political border
    for record in shpreader.Reader(states_over_lakes_filename).records():
        country_code = record.attributes['ISO_A2']
        if country_code == 'TZ':
            geom = record.geometry
            ax.add_geometries([geom], crs=proj, edgecolor='#a0a0a0', facecolor='none')


def plot_basemap_labels(ax, data_path):
    """Plot countries and regions background
    """
    proj = ccrs.PlateCarree()
    extent = ax.get_extent()

    provinces_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_1_states_provinces_lakes.shp'
    )

    lakes_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_lakes.shp'
    )

    # Neighbour labels
    neighbours = [
        {'country': 'Kenya', 'cx': 36.9, 'cy': -2.1},
        {'country': 'Uganda', 'cx': 29.9, 'cy': -0.8},
        {'country': 'Rwanda', 'cx': 29.5, 'cy': -1.9},
        {'country': 'Burundi', 'cx': 29.3, 'cy': -3.2},
        {'country': 'DRC', 'cx': 28.7, 'cy': -5.8},
        {'country': 'Zambia', 'cx': 32.1, 'cy': -10.5},
        {'country': 'Malawi', 'cx': 33.5, 'cy': -11.7},
        {'country': 'Mozambique', 'cx': 37.1, 'cy': -12.3}
    ]
    for neighbour in neighbours:
        x = neighbour['cx']
        y = neighbour['cy']
        if within_extent(x, y, extent):
            ax.text(
                x, y,
                neighbour['country'].upper(),
                alpha=0.7,
                size=9,
                horizontalalignment='left',
                transform=proj)

    # Regions
    nudge_regions = {
        'Dar-Es-Salaam': (0.2, 0),
        'Kagera': (0.2, 0),
        'Kilimanjaro': (0.2, 0),
        'Manyara': (0.15, 0.1),
        'Morogoro': (0.25, 0),
        'Pwani': (0.1, -0.2),
    }

    no_label_regions = [
        'Kaskazini-Pemba',
        'Kaskazini-Unguja',
        'Kusini-Pemba',
        'Zanzibar South and Central',
        'Zanzibar West'
    ]

    for record in shpreader.Reader(provinces_filename).records():
        country_code = record.attributes['iso_a2']
        if country_code == 'TZ':
            geom = record.geometry
            centroid = geom.centroid
            cx = geom.centroid.x
            cy = geom.centroid.y
            name = record.attributes['name']

            if name in no_label_regions:
                continue

            if name in nudge_regions:
                dx, dy = nudge_regions[name]
                cx += dx
                cy += dy

            if name == 'Dar-Es-Salaam':
                ha = 'left'
            else:
                ha = 'center'

            if within_extent(cx, cy, extent):
                ax.text(
                    cx,
                    cy,
                    name,
                    alpha=0.7,
                    size=8,
                    horizontalalignment=ha,
                    transform=proj)

    # Lakes
    for record in shpreader.Reader(lakes_filename).records():
        name = record.attributes['name']
        geom = record.geometry
        if name in (
                'Lake Victoria',
                'Lake Tanganyika',
                'Lake Malawi'):
            cx = geom.centroid.x
            cy = geom.centroid.y
            # nudge
            if name == 'Lake Victoria':
                cy -= 0.2

            if within_extent(cx, cy, extent):
                ax.text(
                    cx,
                    cy,
                    name,
                    alpha=0.7,
                    size=7,
                    horizontalalignment='center',
                    transform=proj)

    # Ocean
    cx = 39.8
    cy = -7.3
    if within_extent(cx, cy, extent):
        ax.text(
            cx,
            cy,
            'Indian Ocean',
            alpha=0.7,
            size=7,
            horizontalalignment='left',
            transform=proj)


def within_extent(x, y, extent):
    xmin, xmax, ymin, ymax = extent
    return xmin < x and x < xmax and ymin < y and y < ymax


def scale_bar(ax, length=100, location=(0.5, 0.05), linewidth=3):
    """Draw a scale bar

    Adapted from https://stackoverflow.com/questions/32333870/how-can-i-show-a-km-ruler-on-a-cartopy-matplotlib-plot/35705477#35705477

    Parameters
    ----------
    ax : axes
    length : int
        length of the scalebar in km.
    location: tuple
        center of the scalebar in axis coordinates (ie. 0.5 is the middle of the plot)
    linewidth: float
        thickness of the scalebar.
    """
    # lat-lon limits
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())

    # Transverse mercator for length
    x = (llx1 + llx0) / 2
    y = lly0 + (lly1 - lly0) * location[1]
    tmc = ccrs.TransverseMercator(x, y)

    # Extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(tmc)

    # Scalebar location coordinates in metres
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]
    bar_xs = [sbx - length * 500, sbx + length * 500]

    # Plot the scalebar and label
    ax.plot(bar_xs, [sby, sby], transform=tmc, color='k', linewidth=linewidth)
    ax.text(sbx, sby + 10*length, str(length) + ' km', transform=tmc,
            horizontalalignment='center', verticalalignment='bottom')


def plot_pop(plt, ax, data_path):
    """Plot population background
    """
    # WorldPop TZA_popmap15adj_v2b
    population_filename = os.path.join(data_path, 'Infrastructure', 'Population',
                                       'TZA_popmap15adj_v2b_resampled.tif')

    # Read in raster data
    gdal.UseExceptions()
    ds = gdal.Open(population_filename)
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

    # Create color map
    colors = plt.get_cmap('Greys')

    # Plot population data
    ax.imshow(data, extent=lat_lon_extent, cmap=colors, norm=LogNorm(vmin=0.1, vmax=10000), zorder=1, alpha=0.5)


def plot_regions(ax, data_path):
    """Plot regions background
    """
    proj_lat_lon = ccrs.PlateCarree()

    # Regions
    provinces_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_1_states_provinces_lakes.shp'
    )

    # Regions
    for record in shpreader.Reader(provinces_filename).records():
        country_code = record.attributes['iso_a2']
        if country_code == 'TZ':
            geom = record.geometry
            ax.add_geometries([geom], crs=proj_lat_lon, edgecolor='#ffffff', facecolor=(1, 1, 1, 0), zorder=2)

            centroid = geom.centroid
            cx = geom.centroid.x
            cy = geom.centroid.y
            name = record.attributes['name']

            skip_regions = [
                'Dar-Es-Salaam',
                'Kusini-Pemba',
                'Kaskazini-Pemba',
                'Kaskazini-Unguja',
                'Zanzibar South and Central',
                'Zanzibar West',
            ]
            if name in skip_regions:
                continue

            nudge_regions = {
                'Kagera': (0.2, 0),
                'Manyara': (0.1, 0.1),
                'Pwani': (0.1, -0.2),
            }

            if name in nudge_regions:
                dx, dy = nudge_regions[name]
                cx += dx
                cy += dy

            if name == 'Dar-Es-Salaam':
                ha = 'left'
            else:
                ha = 'center'

            ax.text(
                cx,
                cy,
                name.upper(),
                alpha=0.3,
                size=6,
                horizontalalignment=ha,
                transform=proj_lat_lon)


def line_length(line, ellipsoid='WGS-84'):
    """Length of a line in meters, given in geographic coordinates

    Adapted from https://gis.stackexchange.com/questions/4022/looking-for-a-pythonic-way-to-calculate-the-length-of-a-wkt-linestring#answer-115285

    Args:
        line: a shapely LineString object with WGS-84 coordinates
        ellipsoid: string name of an ellipsoid that `geopy` understands (see
            http://geopy.readthedocs.io/en/latest/#module-geopy.distance)

    Returns:
        Length of line in meters
    """
    if line.geometryType() == 'MultiLineString':
        return sum(line_length(segment) for segment in line)

    return sum(
        vincenty(a, b, ellipsoid=ellipsoid).meters
        for a, b in pairwise(line.coords)
    )


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
