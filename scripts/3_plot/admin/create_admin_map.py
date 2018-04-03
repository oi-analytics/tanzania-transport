"""Generate administrative map of Tanzania's regions and neighbouring countries
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import load_config, get_tz_axes, save_fig, plot_basemap, plot_basemap_labels

config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

states_filename = os.path.join(
    data_path,
    'Infrastructure',
    'Boundaries',
    'ne_10m_admin_0_countries_lakes.shp'
)

output_filename = os.path.join(
    figures_path,
    'admin_map.png'
)

ax = get_tz_axes()
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)

# Africa, for neighbours map
proj = ccrs.PlateCarree()
ax = plt.axes([0.035, 0.025, 0.25, 0.25], projection=proj)
x0 = 8
x1 = 52
y0 = 10
y1 = -37
ax.set_extent([x0, x1, y0, y1], crs=proj)

for record in shpreader.Reader(states_filename).records():
    if record.attributes['CONTINENT'] == 'Africa':
        geom = record.geometry
        country_code = record.attributes['ISO_A2']
        if country_code == 'TZ':
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#c4c4c4')
        else:
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#e0e0e0')

save_fig(output_filename)
