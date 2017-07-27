"""Generate transport corridor map, showing major routes and nodes for each mode
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

# Input data
base_path = os.path.join(os.path.dirname(__file__), '..')
data_path = os.path.join(base_path, 'data')

# TZ_TransNet_Roads, clipped to Tanzania
road_filename = os.path.join(data_path, 'Road_data', 'TZ_TransNet_Roads.shp')

# TransNet_Railroads
railway_filename = os.path.join(data_path, 'Railway_data', 'TZ_TransNet_Railroads.shp')

# TZ_TransNet_FerryTerminals and TZ_TransNet_FerryRoutes
ferry_path = os.path.join(data_path, 'Port_data')
ferry_terminals = os.path.join(ferry_path, 'TZ_TransNet_FerryTerminals.shp')
ferry_routes = os.path.join(ferry_path, 'TZ_TransNet_FerryRoutes.shp')

# tanzania_airports from ourairports.com
airport_path = os.path.join(data_path, 'Airport_data', 'tanzania_airports.csv')

# Natural Earth countries
states_filename = os.path.join(data_path, 'Boundary_datasets',
                               'ne_10m_admin_0_countries_lakes.shp')

# Read in Tanzania outline
for record in shpreader.Reader(states_filename).records():
    country_code = record.attributes["ISO_A2"]
    if country_code == "TZ":
        tz_geom = record.geometry
