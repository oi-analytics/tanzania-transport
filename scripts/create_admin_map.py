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

ne_10m_admin_1_states_provinces_lakes_filename = os.path.join(
    data_path,
    'Boundary_datasets',
    'ne_10m_admin_1_states_provinces_lakes.shp'
)

ax = plt.axes(projection=ccrs.UTM(37, southern_hemisphere=True))
x0 = 29.34
x1 = 43.29
y0 = -0.99
y1 = -11.75
ax.set_extent([x0, x1, y0, y1], crs=ccrs.PlateCarree())

ax.background_patch.set_visible(False)
ax.outline_patch.set_visible(False)

for geom in shpreader.Reader(ne_10m_admin_1_states_provinces_lakes_filename).geometries():
    ax.add_geometries([geom], crs=ccrs.PlateCarree(), edgecolor='black', facecolor='#888888')

output_filename = os.path.join(
    base_path,
    'figures',
    'test.png'
)
plt.savefig(output_filename)
