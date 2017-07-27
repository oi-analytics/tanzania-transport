"""Generate detailed road network map of Tanzania
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

states_filename = os.path.join(data_path, 'Boundary_datasets',
                               'ne_10m_admin_0_countries_lakes.shp')

# TZ_TransNet_Roads, clipped to Tanzania
# PMO_TanRoads

# Read in Tanzania outline
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes["ISO_A2"]
    if country_code == "TZ":
        tz_geom = record.geometry
