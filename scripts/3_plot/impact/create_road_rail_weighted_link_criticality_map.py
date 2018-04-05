"""Weighted network for the link criticality (number of times route length increases)
over road and rail networks.
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from shapely.geometry import LineString

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *

# Input data
config = load_config()
data_path = config['data_path']
figures_path = config['figures_path']

states_filename = os.path.join(data_path, 'Infrastructure', 'Boundaries',
                               'ne_10m_admin_0_countries_lakes.shp')

# Roads
road_filename = os.path.join(
    data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')

# Rail
rail_filename = os.path.join(
    data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_rail_spof_geom.shp')

proj_lat_lon = ccrs.PlateCarree()

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


# Create figure for road, just rerouting
print("figure for road, rerouting")
ax = get_tz_axes()
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

for ind_range, geoms in roads_by_incr_fact.items():
    if ind_range[1] is None:
        buf = 0.01
    else:
        buf = width_by_range[ind_range]
    ax.add_geometries(
        [geom.buffer(buf) for geom in geoms],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#d1170a',
        facecolor='#d1170a',
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
    if nmax is None:
        continue
        # label = 'Single point of failure'
    else:
        label = '{}-{}'.format(nmin, nmax)
    y = base_y - (i*0.4)
    line = LineString([(x_l, y), (x_r, y)])
    ax.add_geometries(
        [line.buffer(width)],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#000000',
        facecolor='#000000',
        zorder=2)
    ax.text(
        x_r + 0.1,
        y - 0.15,
        label,
        horizontalalignment='left',
        transform=proj_lat_lon)

legend_handles = [
    mpatches.Patch(color='#d1170a', label='TANROADS Trunk and Regional Roads'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

output_filename = os.path.join(
    figures_path,
    'weighted_road_increase_factor_map.png'
)
plt.savefig(output_filename)
plt.close()



# Create figure for rail, just rerouting
ax = get_tz_axes()
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925, 0.02))

for ind_range, geoms in rail_by_incr_fact.items():
    if ind_range[1] is None:
        buf = 0.01
    else:
        buf = width_by_range[ind_range]
    ax.add_geometries(
        [geom.buffer(buf) for geom in geoms],
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
    if nmax is None:
        continue
        # label = 'Single point of failure'
    else:
        label = '{}-{}'.format(nmin, nmax)
    y = base_y - (i*0.4)
    line = LineString([(x_l, y), (x_r, y)])
    ax.add_geometries(
        [line.buffer(width)],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#000000',
        facecolor='#000000',
        zorder=2)
    ax.text(
        x_r + 0.1,
        y - 0.15,
        label,
        horizontalalignment='left',
        transform=proj_lat_lon)

legend_handles = [
    mpatches.Patch(color='#33a02c', label='TRL and TAZARA Railways'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

output_filename = os.path.join(
    figures_path,
    'weighted_rail_increase_factor_map.png'
)
plt.savefig(output_filename)
plt.close()



# Create figure for road, spof
print("figure for road, spof")
ax = get_tz_axes()
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

for ind_range, geoms in roads_by_incr_fact.items():
    if ind_range[1] is None:
        buf = width_by_range[ind_range]
    else:
        buf = 0.01
    ax.add_geometries(
        [geom.buffer(buf) for geom in geoms],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#d1170a',
        facecolor='#d1170a',
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
    if nmax is not None:
        continue
    else:
        label = 'Single point of failure'
        # label = '{}-{}'.format(nmin, nmax)
    y = base_y - (i*0.4)
    line = LineString([(x_l, y), (x_r, y)])
    ax.add_geometries(
        [line.buffer(width)],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#000000',
        facecolor='#000000',
        zorder=2)
    ax.text(
        x_r + 0.1,
        y - 0.15,
        label,
        horizontalalignment='left',
        transform=proj_lat_lon)

legend_handles = [
    mpatches.Patch(color='#d1170a', label='TANROADS Trunk and Regional Roads'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

output_filename = os.path.join(
    figures_path,
    'weighted_road_spof_map.png'
)
plt.savefig(output_filename)
plt.close()



# Create figure for rail, spof
print("figure for rail, spof")
ax = get_tz_axes()
plot_basemap(ax, data_path)
plot_basemap_labels(ax, data_path)
scale_bar(ax, length=100, location=(0.925,0.02))

for ind_range, geoms in rail_by_incr_fact.items():
    if ind_range[1] is None:
        buf = width_by_range[ind_range]
    else:
        buf = 0.01
    ax.add_geometries(
        [geom.buffer(buf) for geom in geoms],
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
    if nmax is not None:
        continue
    else:
        label = 'Single point of failure'
        # label = '{}-{}'.format(nmin, nmax)
    y = base_y - (i*0.4)
    line = LineString([(x_l, y), (x_r, y)])
    ax.add_geometries(
        [line.buffer(width)],
        crs=proj_lat_lon,
        linewidth=0,
        edgecolor='#000000',
        facecolor='#000000',
        zorder=2)
    ax.text(
        x_r + 0.1,
        y - 0.15,
        label,
        horizontalalignment='left',
        transform=proj_lat_lon)

legend_handles = [
    mpatches.Patch(color='#33a02c', label='TRL and TAZARA Railways'),
]
plt.legend(
    handles=legend_handles,
    loc='lower left'
)

output_filename = os.path.join(
    figures_path,
    'weighted_rail_spof_map.png'
)
plt.savefig(output_filename)
plt.close()
