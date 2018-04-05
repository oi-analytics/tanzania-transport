"""Generate maps of flood hazards
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import shapely.geometry

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

hazard_base_path = os.path.join(
    data_path,
    'tanzania_flood'
)

output_filename = os.path.join(
    figures_path,
    'ssbn_map_1000.png'
)

# List of dicts, each with {return_period, filename, model, period}
hazard_file_details = []

# Return period of interest
return_period = 1000

# Global climate models
models = [
    ('Pluvial', 'TZ_pluvial_undefended', 'PU'),
    ('Fluvial', 'TZ_fluvial_undefended', 'FU')
]

# Current hazards
for model, model_dir, abbr in models:
    hazard_file_details.append({
            "return_period": return_period,
            "filename": os.path.join(
                hazard_base_path,
                'SSBN_flood_data',
                model_dir,
                'TZ-{}-{}-1.tif'.format(abbr, return_period)
            ),
            "model": model
    })

proj = ccrs.PlateCarree()

# Create figure
fig, axes = plt.subplots(
    nrows=1,
    ncols=2,
    subplot_kw=dict(projection=proj),
    figsize=(9, 6),
    dpi=150)

data_with_lat_lon = [get_data(details["filename"]) for details in hazard_file_details]

# Set up colormap and norm
cmap, norm = get_hazard_cmap_norm()

# Extent of area to focus on
zoom_extent = (37.5, 39.5, -8.25, -6.25)

# Plot data to axes
for (ax_num, ax), (data, lat_lon_extent), details in zip(enumerate(axes.flat), data_with_lat_lon, hazard_file_details):
    ax.locator_params(tight=True)
    ax.outline_patch.set_visible(False)

    # x/y labels
    ax.set_title(details["model"])
    if ax_num == 0:
        ax.text(
            -0.02,
            0.55,
            "{}y return".format(details["return_period"]),
            va='bottom',
            ha='center',
            rotation='vertical',
            rotation_mode='anchor',
            transform=ax.transAxes)

    ax.set_extent(zoom_extent, crs=proj)

    plot_basemap(ax, data_path)
    im = ax.imshow(data, extent=lat_lon_extent, cmap=cmap, norm=norm, zorder=1)


# Adjust layout
ax_list = list(axes.flat)
plt.tight_layout(pad=0.3, h_pad=0.3, w_pad=0.04, rect=(0.05, 0.1, 1, 1))

hazard_legend(im, ax_list)

# Add context
ax = plt.axes([0.01, 0.01, 0.2, 0.4], projection=proj)
tz_extent = (28.6, 41.4, -0.1, -13.2)
ax.set_extent(tz_extent, crs=proj)
plot_basemap(ax, data_path)

# Zoom extent: (37.5, 39.5, -8.25, -6.25)
x0, x1, y0, y1 = zoom_extent
box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
ax.add_geometries([box], crs=proj, edgecolor='#000000', facecolor='#d7d7d700')

# Save
save_fig(output_filename)
