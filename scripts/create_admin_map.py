"""Generate administrative map of Tanzania's regions and neighbouring countries
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

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
    'Boundary_datasets',
    'ne_10m_admin_0_countries_lakes.shp'
)

provinces_filename = os.path.join(
    data_path,
    'Boundary_datasets',
    'ne_10m_admin_1_states_provinces_lakes.shp'
)

plt.figure(figsize=(6, 6), dpi=150)

proj = ccrs.PlateCarree()
ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj)
x0 = 28.6
x1 = 41.4
y0 = -0.1
y1 = -13.2
ax.set_extent([x0, x1, y0, y1], crs=proj)

# Neighbours
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes['ISO_A2']
    if country_code in ('BI', 'RW', 'CD', 'UG', 'KE', 'ZM', 'MW', 'MZ', 'SO'):
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#efefef')

# Neighbour labels
neighbours = [
    {
        'country': 'Kenya',
        'cx': 36.9,
        'cy': -2.1
    },
    {
        'country': 'Uganda',
        'cx': 29.9,
        'cy': -0.8
    },
    {
        'country': 'Rwanda',
        'cx': 29.2,
        'cy': -1.9
    },
    {
        'country': 'Burundi',
        'cx': 29.2,
        'cy': -3.4
    },
    {
        'country': 'DRC',
        'cx': 28.7,
        'cy': -5.9
    },
    {
        'country': 'Zambia',
        'cx': 32.1,
        'cy': -10.5
    },
    {
        'country': 'Malawi',
        'cx': 33.5,
        'cy': -11.7
    },
    {
        'country': 'Mozambique',
        'cx': 37.1,
        'cy': -12.3
    }
]
for neighbour in neighbours:
    plt.text(
        neighbour['cx'],
        neighbour['cy'],
        neighbour['country'].upper(),
        horizontalalignment='left',
        transform=proj)

nudge_regions = {
    'Dar-Es-Salaam': (-0.35, 0),
    'Kagera': (0.2, 0),
    'Kaskazini-Pemba': (0, 0.2),
    'Kaskazini-Unguja': (0, 0.1),
    'Kusini-Pemba': (0, -0.2),
    'Manyara': (0.1, 0.1),
    'Pwani': (0.1, -0.2),
    'Zanzibar South and Central': (-0.3, -0.25),
}

# Regions
for record in shpreader.Reader(provinces_filename).records():
    country_code = record.attributes['iso_a2']
    if country_code == 'TZ':
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#d7d7d7')

        centroid = geom.centroid
        cx = geom.centroid.x
        cy = geom.centroid.y
        name = record.attributes['name']

        if name in nudge_regions:
            dx, dy = nudge_regions[name]
            cx += dx
            cy += dy

        if name == 'Dar-Es-Salaam':
            ha = 'left'
        else:
            ha = 'center'

        plt.text(
            cx,
            cy,
            name,
            horizontalalignment=ha,
            transform=proj)

plt.title('Neighbouring Countries and Regions of Tanzania')

ax = plt.axes([0.0375, 0.025, 0.25, 0.25], projection=proj)
x0 = 8
x1 = 52
y0 = 10
y1 = -37
ax.set_extent([x0, x1, y0, y1], crs=proj)

# Africa, for neighbours map
for record in shpreader.Reader(states_filename).records():
    if record.attributes['CONTINENT'] == 'Africa':
        geom = record.geometry
        country_code = record.attributes['ISO_A2']
        if country_code == 'TZ':
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#d7d7d7')
            # plt.text(
            #     geom.centroid.x,
            #     geom.centroid.y,
            #     'Tanzania',
            #     horizontalalignment='left',
            #     transform=proj)
        else:
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#efefef')

output_filename = os.path.join(
    base_path,
    'figures',
    'admin_map.png'
)
plt.savefig(output_filename)
