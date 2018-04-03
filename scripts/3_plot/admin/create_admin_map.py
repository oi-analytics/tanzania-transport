"""Generate administrative map of Tanzania's regions and neighbouring countries
"""
# pylint: disable=C0103
import json
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

# Input data
with open('config.json', 'r') as config_fh:
    config = json.load(config_fh)

data_path = config['data_path']
figures_path = config['figures_path']

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

output_filename = os.path.join(
    figures_path,
    'admin_map.png'
)

plt.figure(figsize=(7, 7), dpi=300)

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
        ax.add_geometries([geom], crs=proj, edgecolor='#ffffff', facecolor='#e0e0e0')

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
        alpha=0.9,
        size=9,
        horizontalalignment='left',
        transform=proj)

nudge_regions = {
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

# Regions
for record in shpreader.Reader(provinces_filename).records():
    country_code = record.attributes['iso_a2']
    if country_code == 'TZ':
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='#ffffff', facecolor='#d2d2d2')

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

        plt.text(
            cx,
            cy,
            name,
            alpha=0.8,
            size=8,
            horizontalalignment=ha,
            transform=proj)

# Tanzania, political border
for record in shpreader.Reader(states_over_lakes_filename).records():
    country_code = record.attributes['ISO_A2']
    if country_code == 'TZ':
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='#a0a0a0', facecolor='#00000000')


# Africa, for neighbours map
ax = plt.axes([0.0375, 0.025, 0.25, 0.25], projection=proj)
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

plt.savefig(output_filename)
plt.savefig(output_filename.replace("png", "svg"))
