"""Shared plotting functions
"""
import os

from osgeo import gdal
from matplotlib.colors import LogNorm

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader


def plot_countries(ax, data_path):
    """Plot countries background
    """
    proj_lat_lon = ccrs.PlateCarree()

    # Natural Earth countries
    states_filename = os.path.join(data_path, 'Boundary_datasets',
                                'ne_10m_admin_0_countries_lakes.shp')


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


def plot_pop(plt, ax, data_path):
    """Plot population background
    """
    # WorldPop TZA_popmap15adj_v2b
    population_filename = os.path.join(data_path, 'Population_data', 'TZA_popmap15adj_v2b_resampled.tif')

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
    im = ax.imshow(data, extent=lat_lon_extent, cmap=colors, norm=LogNorm(vmin=0.1, vmax=10000), zorder=1, alpha=0.5)


def plot_regions(ax, data_path):
    """Plot regions background
    """
    proj_lat_lon = ccrs.PlateCarree()

    # Regions
    provinces_filename = os.path.join(
        data_path,
        'Boundary_datasets',
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