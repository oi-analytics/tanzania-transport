"""Generate maps of flood hazards
"""
# pylint: disable=C0103
import os

from osgeo import gdal

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry

# Input data
base_path = os.path.join(
    os.path.dirname(__file__),
    '..'
)

data_path = os.path.join(
    base_path,
    'data'
)

states_filename = os.path.join(
    data_path,
    'Infrastructure',
    'Boundaries',
    'ne_10m_admin_0_countries_lakes.shp'
)

lakes_filename = os.path.join(
    data_path,
    'Infrastructure',
    'Boundaries',
    'Major Lakes.shp'
)

hazard_base_path = os.path.join(
    data_path,
    'tanzania_flood'
)

# List of dicts, each with {return_period, filename, model, period}
hazard_file_details = []

# Return periods of interest
return_periods = [5, 1000]

# Global climate models
models = [
    'GFDL-ESM2M',
    'HadGEM2-ES',
    'IPSL-CM5A-LR',
    'MIROC-ESM-CHEM',
    'NorESM1-M',
]

# Current hazards
for return_period in return_periods:
    hazard_file_details.append({
        "return_period": return_period,
        "filename": os.path.join(
            hazard_base_path,
            'EUWATCH',
            'inun_dynRout_RP_{:05d}_Tanzania'.format(return_period),
            'inun_dynRout_RP_{:05d}_contour_Tanzania.tif'.format(return_period)
        ),
        "model": "Current",
        "period": "Current"
    })

# Modelled future hazards (under different GCMs)
for model in models:
    for return_period in return_periods:
        hazard_file_details.append({
            "return_period": return_period,
            "filename": os.path.join(
                hazard_base_path,
                model,
                'rcp6p0',
                '2030-2069',
                'inun_dynRout_RP_{:05d}_bias_corr_masked_Tanzania'.format(return_period),
                'inun_dynRout_RP_{:05d}_bias_corr_contour_Tanzania.tif'.format(return_period)
            ),
            "model": model,
            "period": "2030-2069"
        })


def get_data(filename):
    """Read in data (as array) and extent of each raster
    """
    gdal.UseExceptions()
    ds = gdal.Open(filename)
    data = ds.ReadAsArray()
    data[data <= 0.25] = 0
    data[(data > 0.25) & (data <=25)] = 1
    data[data > 25] = 2

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


# Read in Tanzania outline
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes["ISO_A2"]
    if country_code == "TZ":
        tz_geom = record.geometry

# Read in major lakes
major_lakes = []
for record in shpreader.Reader(lakes_filename).records():
    major_lakes.append(record.geometry)

proj = ccrs.PlateCarree()
colors = plt.get_cmap('Blues')
# colors.colors[0] = (1, 1, 1, 0)  # set zero values to transparent white - works for e.g. viridis colormap
colors._segmentdata['alpha'][0] = (0, 0, 0)  # set zero values to transparent white - works for LinearSegmentedColorMap

# Create figure
fig, axes = plt.subplots(
    nrows=2+len(models),
    ncols=len(return_periods),
    subplot_kw=dict(projection=proj),
    figsize=(4, 9),
    dpi=150)

data_with_lat_lon = [get_data(details["filename"]) for details in hazard_file_details]

# Find global min/max to use for consistent color-mapping
min_val = np.min([np.min(data) for data, lat_lon in data_with_lat_lon])
max_val = np.max([np.max(data) for data, lat_lon in data_with_lat_lon])

# Extent of area to focus on
zoom_extent = (37.8, 39.6, -8.5, -6.7)

# Plot data to axes
for (ax_num, ax), (data, lat_lon_extent), details in zip(enumerate(axes.flat), data_with_lat_lon, hazard_file_details):
    ax.locator_params(tight=True)
    ax.outline_patch.set_visible(False)

    # x/y labels
    if ax_num < len(return_periods):
        ax.set_title("{}y return".format(details["return_period"]))
    if ax_num % len(return_periods) == 0:
        ax.text(
            -0.07,
            0.55,
            details["model"],
            va='bottom',
            ha='center',
            rotation='vertical',
            rotation_mode='anchor',
            transform=ax.transAxes)

    ax.set_extent(zoom_extent, crs=proj)
    ax.add_geometries([tz_geom], crs=proj, edgecolor='#d7d7d7', facecolor='#fafafa', zorder=0)
    im = ax.imshow(data, extent=lat_lon_extent, cmap=colors, vmin=min_val, vmax=max_val, zorder=1)
    ax.add_geometries(major_lakes, crs=proj, facecolor='white', zorder=2)

# Add context
for ax_num, ax in enumerate(axes.flat):
    if ax_num == len(return_periods)*(len(models)+1):
        ax.locator_params(tight=True)
        tz_extent = (28.6, 41.4, -0.1, -13.2)
        ax.set_extent(tz_extent, crs=proj)

        # Tanzania
        ax.add_geometries([tz_geom], crs=proj, edgecolor='white', facecolor='#fafafa')

        # Neighbours
        for record in shpreader.Reader(states_filename).records():
            country_code = record.attributes['ISO_A2']
            if country_code in ('BI', 'RW', 'CD', 'UG', 'KE', 'ZM', 'MW', 'MZ', 'SO'):
                geom = record.geometry
                ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#efefef')

        # Zoom extent: (37.5, 39.5, -8.25, -6.25)
        x0, x1, y0, y1 = zoom_extent
        box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
        ax.add_geometries([box], crs=proj, edgecolor='#000000', facecolor='#d7d7d700')

        im = ax.imshow(data, extent=lat_lon_extent, cmap=colors, vmin=min_val, vmax=max_val, zorder=1)
    elif ax_num > len(return_periods)*(len(models)+1):
        ax.locator_params(tight=True)
        ax.outline_patch.set_visible(False)

# Adjust layout
ax_list = list(axes.flat)
plt.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.02, rect=(0, 0, 1, 1))

# Save
output_filename = os.path.join(
    base_path,
    'figures',
    'hazard_map.png'
)
plt.savefig(output_filename)
