"""Generate maps of flood hazards
"""
# pylint: disable=C0103
import os

from osgeo import gdal

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import numpy as np

# Input data
base_path = os.path.join(
    os.path.dirname(__file__),
    '..'
)

data_path = os.path.join(
    base_path,
    'data'
)

hazard_base_path = os.path.join(
    data_path,
    'tanzania_flood'
)

# List of dicts, each with {return_period, filename, model, period}
hazard_file_details = []

# Return periods of interest
return_periods = [2, 5, 10, 25, 50, 100, 250, 500, 1000]

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



# Create figure
fig, axes = plt.subplots(
    nrows=1+len(models),
    ncols=len(return_periods),
    figsize=(18, 12),
    dpi=150)

# Plot data to axes
for (ax_num, ax), details in zip(enumerate(axes.flat), hazard_file_details):
    print(details["model"], details["return_period"])
    data, lat_lon_extent = get_data(details["filename"])
    ax.locator_params(tight=True)

    # x/y labels
    if ax_num < len(return_periods):
        ax.set_title("{}y return".format(details["return_period"]))
    if ax_num % len(return_periods) == 0:
        ax.text(
            -0.8,
            0.55,
            details["model"],
            va='bottom',
            ha='center',
            rotation='vertical',
            rotation_mode='anchor',
            transform=ax.transAxes)

    # flatten to 1D
    data.flatten()
    # exclude infinite and nan
    data = data[np.isfinite(data)]
    # exclude negative and 'max' values
    data = data[(data >= 0) & (data < 999)]
    ax.set_ylim([0,10000])
    ax.set_xlim([0,15])
    ax.hist(data, bins=15, range=(0, 15))

# Adjust layout
ax_list = list(axes.flat)
plt.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.04, rect=(0.05, 0, 1, 1))

# Save
output_filename = os.path.join(
    base_path,
    'figures',
    'flood_depth_histograms.png'
)
plt.savefig(output_filename)