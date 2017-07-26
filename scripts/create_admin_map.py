"""Generate administrative map of Tanzania's regions and neighbouring countries
"""
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

plt.figure(figsize=(10, 10), dpi=150)

proj = ccrs.PlateCarree()
ax = plt.axes([0.025, 0.025, 0.95, 0.95], projection=proj)
x0 = 28.6
x1 = 41.4
y0 = -0.8
y1 = -13.2
ax.set_extent([x0, x1, y0, y1], crs=proj)

# Neighbours, for region map
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes["ISO_A2"]
    if country_code in ("BI", "RW", "CD", "UG", "KE", "ZM", "MW", "MZ", "SO"):
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#efefef')

# Regions
for record in shpreader.Reader(provinces_filename).records():
    country_code = record.attributes["iso_a2"]
    if country_code == "TZ":
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#d7d7d7')

        centroid = geom.centroid
        cx = geom.centroid.x
        cy = geom.centroid.y
        name = record.attributes["name"]
        if name == "Zanzibar South and Central":
            cy -= 0.18
        if name == "Dar-Es-Salaam":
            ha = 'left'
        else:
            ha = 'center'

        plt.text(
            cx,
            cy,
            name,
            horizontalalignment=ha,
            transform=proj)

plt.title("Neighbouring Countries and Regions of Tanzania")

ax = plt.axes([0, 0, 0.3, 0.4], projection=proj)
x0 = 16
x1 = 52
y0 = 10
y1 = -37
ax.set_extent([x0, x1, y0, y1], crs=proj)

# Africa, for neighbours map
for record in shpreader.Reader(states_filename).records():
    if record.attributes["CONTINENT"] == "Africa":
        geom = record.geometry
        country_code = record.attributes["ISO_A2"]
        if country_code == "TZ":
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='none')
        elif country_code in ("TZ", "BI", "RW", "CD", "UG", "KE", "ZM", "MW", "MZ", "SO"):
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#efefef')
        else:
            ax.add_geometries([geom], crs=proj, edgecolor='white', facecolor='#efefef')

        if country_code in ("TZ", "BI", "RW", "CD", "UG", "KE", "ZM", "MW", "MZ", "SO"):
            centroid = geom.centroid
            name = record.attributes["NAME"]
            if country_code == "CD":
                name = "DRC"
            plt.text(
                centroid.x,
                centroid.y,
                name,
                horizontalalignment='center',
                transform=proj)

output_filename = os.path.join(
    base_path,
    'figures',
    'admin_map.png'
)
plt.savefig(output_filename)
