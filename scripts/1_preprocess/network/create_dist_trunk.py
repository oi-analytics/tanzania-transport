# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 11:38:17 2017

@author: cenv0574
"""

import geopandas as gpd

import os
import pandas as pd
from shapely.geometry import Point
import networkx as nx
from network_analysis import get_shortest_distance
import numpy as np

if __name__ == "__main__":

    '''Set some starting variables. i.e. define region'''
    curdir = os.getcwd()
    region = 'Mwanza'
    country = 'Tanzania'

    '''Set file in and output names'''
    shape_in = curdir+"\\regions\\"+region+'.shp'
    raster_out = curdir+"\\%s-globpop.tif" % region
    raster_in = 'F:\Dropbox\Oxford\Tanzania\TZA_Roads\GLOBPOP\TZA_popmap15adj_v2b.tif'
    outCSVName = 'points_%s_in.csv' % region

    '''Clip to region and convert to points'''
    os.system('gdalwarp -cutline '+shape_in+' -crop_to_cutline -dstalpha '+raster_in+' '+raster_out)
    os.system('gdal2xyz.py -skip 3 -csv '+raster_out+' '+ outCSVName)

    '''Load points and convert to geodataframe with coordinates'''    
    load_points = pd.read_csv(outCSVName,header=None,names=['x','y','pop_dens'],index_col=None)
    load_points = load_points[load_points['pop_dens'] > 5] 
 
    geometry = [Point(xy) for xy in zip(load_points.x, load_points.y)]
    load_points = load_points.drop(['x', 'y'], axis=1)
    crs = {'init': 'epsg:4326'}
    points_gdp = gpd.GeoDataFrame(load_points, crs=crs, geometry=geometry)
    del load_points

    ''' Load local road network of the pre-defined region'''
    g = nx.read_shp("cleaned_regions//%s-highway-1.shp" % region)

    g_undir = nx.connected_component_subgraphs(g.to_undirected())
    lengths = [len(x) for x in list(g_undir)]
    
    sg =  max(nx.connected_component_subgraphs(g.to_undirected()), key=len)
    pos = {k: v for k,v in enumerate(sg.nodes())}

    nodes = np.array(sg.nodes())

    points_gdp['dist_trunk'] = points_gdp['geometry'].apply(lambda x: get_shortest_distance(sg,nodes,x)) 
    points_gdp.to_file(driver = 'ESRI Shapefile', filename= "dist_trunk_%s.shp" % region)             
        

