import os
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt

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

proj = ccrs.PlateCarree()
ax = plt.axes(projection=proj)
x0 = 28.6
x1 = 41.4
y0 = -0.2
y1 = -12.2
ax.set_extent([x0, x1, y0, y1], crs=proj)

for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes["ISO_A2"]
    if country_code in ("TZ", "BI", "RW", "CD", "UG", "KE", "ZM", "MW", "MZ", "SO"):
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='black', facecolor='#f4f4f4')

for record in shpreader.Reader(provinces_filename).records():
    country_code = record.attributes["iso_a2"]
    if country_code == "TZ":
        geom = record.geometry
        ax.add_geometries([geom], crs=proj, edgecolor='black', facecolor='#d7d7d7')

output_filename = os.path.join(
    base_path,
    'figures',
    'test.png'
)
plt.savefig(output_filename)
