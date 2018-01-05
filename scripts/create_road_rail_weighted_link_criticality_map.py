"""Weighted network for the link criticality (number of times route length increases)
over road and rail networks.
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from shapely.geometry import LineString

from utils import plot_pop, plot_countries, plot_regions

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

states_filename = os.path.join(data_path, 'Infrastructure', 'Boundaries',
                               'ne_10m_admin_0_countries_lakes.shp')

# Roads
road_filename = os.path.join(
    data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')

# Rail
rail_filename = os.path.join(
    data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_rail_spof_geom.shp')

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
plot_regions(ax, data_path)

# All roads
roads_by_incr_fact = {
    (0, 5): [],
    (5, 10): [],
    (10, 50): [],
    (50, 100): [],
    (100, 1100): [],
    (1100, None): []
}

width_by_range = {
    (0, 5): 0.005,
    (5, 10): 0.01,
    (10, 50): 0.02,
    (50, 100): 0.04,
    (100, 1100): 0.06,
    (1100, None): 0.08
}

for record in shpreader.Reader(road_filename).records():
    geom = record.geometry
    incr_fact = record.attributes['incr_fact']
    if incr_fact > 1100:
        roads_by_incr_fact[(1100, None)].append(geom)
    else:
        for nmin, nmax in roads_by_incr_fact:
            if nmin <= incr_fact and incr_fact < nmax:
                roads_by_incr_fact[(nmin, nmax)].append(geom)

for ind_range, geoms in roads_by_incr_fact.items():
    ax.add_geometries(
        [geom.buffer(width_by_range[ind_range]) for geom in geoms],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#d1170a',
        facecolor='#d1170a',
        zorder=2)


# All rail
rail_by_incr_fact = {
    (0, 5): [],
    (5, 10): [],
    (10, 50): [],
    (50, 100): [],
    (100, 1100): [],
    (1100, None): []
}

for record in shpreader.Reader(rail_filename).records():
    geom = record.geometry
    incr_fact = record.attributes['incr_fact']
    if incr_fact > 1100:
        rail_by_incr_fact[(1100, None)].append(geom)
    else:
        for nmin, nmax in rail_by_incr_fact:
            if nmin <= incr_fact and incr_fact < nmax:
                rail_by_incr_fact[(nmin, nmax)].append(geom)

for ind_range, geoms in rail_by_incr_fact.items():
    ax.add_geometries(
        [geom.buffer(width_by_range[ind_range]) for geom in geoms],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#33a02c',
        facecolor='#33a02c',
        zorder=2)

# Legend
# x0 = 28.6
# x1 = 41.4
# y0 = 0.5
# y1 = -12.5
x_l = 28.8
x_r = 29.5
base_y = -8.5
for (i, ((nmin, nmax), width)) in enumerate(width_by_range.items()):
    y = base_y - (i*0.4)
    line = LineString([(x_l, y), (x_r, y)])
    ax.add_geometries(
        [line.buffer(width)],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#000000',
        facecolor='#000000',
        zorder=2)
    if nmax is None:
        label = 'Single point of failure'
    else:
        label = '{}-{}'.format(nmin, nmax)
    ax.text(
        x_r + 0.1,
        y - 0.15,
        label,
        horizontalalignment='left',
        transform=proj_lat_lon)

legend_handles = [
    mpatches.Patch(color='#d1170a', label='TANROADS Trunk and Regional Roads'),
    mpatches.Patch(color='#33a02c', label='TRL and TAZARA Railways'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)
plt.title('Route increase factor for road and rail in Tanzania')


output_filename = os.path.join(
    base_path,
    'figures',
    'weighted_road_rail_increase_factor_map.png'
)
plt.savefig(output_filename)
