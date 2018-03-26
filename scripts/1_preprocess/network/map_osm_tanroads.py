# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 14:15:54 2017

@author: cenv0574
"""

import networkx as nx
import os
import numpy as np
import json
import pandas as pd
import geopandas as gpd
import shapely.wkt
import shapely.ops

def get_path(n0, n1,sg):
    """If n0 and n1 are connected nodes in the graph, this function
    return an array of point coordinates along the road linking
    these two nodes."""
    return np.array(json.loads(sg[n0][n1]['Json'])['coordinates'])

EARTH_R = 6372.8
def geocalc(lat0, lon0, lat1, lon1):
    """Return the distance (in km) between two points in
    geographical coordinates."""
    lat0 = np.radians(lat0)
    lon0 = np.radians(lon0)
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    dlon = lon0 - lon1
    y = np.sqrt(
        (np.cos(lat1) * np.sin(dlon)) ** 2
       + (np.cos(lat0) * np.sin(lat1)
        - np.sin(lat0) * np.cos(lat1) * np.cos(dlon)) ** 2)
    x = np.sin(lat0) * np.sin(lat1) + \
        np.cos(lat0) * np.cos(lat1) * np.cos(dlon)
    c = np.arctan2(y, x)
    return EARTH_R * c

def get_path_length(path):
    return np.sum(geocalc(path[1:,0], path[1:,1],
                          path[:-1,0], path[:-1,1]))

def get_full_path(path,sg):
    """Return the positions along a path."""
    p_list = []
    curp = None
    for i in range(len(path)-1):
        p = get_path(path[i], path[i+1],sg)
        if curp is None:
            curp = p
        if np.sum((p[0]-curp)**2) > np.sum((p[-1]-curp)**2):
            p = p[::-1,:]
        p_list.append(p)
        curp = p[-1]
    return np.vstack(p_list)

if __name__ == "__main__":

# =============================================================================
# # set basics and give version number
# =============================================================================
    infra_type = 'highway'
    
    base_path = os.path.join(os.path.dirname(__file__), '..')
    country_data_dir = os.path.join(base_path,'input_data')
    
    # give version:
    version = 'v5'
# =============================================================================
#     # load tanzania data from OSM    
# =============================================================================
   
    country = 'tanzania'
    country_path_in = os.path.join(country_data_dir,'%s-%s-tr.shp' % (country,infra_type))
    country_path_2 = os.path.join(base_path,'calc','%s-%s.shp' % (country,infra_type))
    country_path_out = os.path.join(base_path,'output_data','tanroads_all_2017_%s.shp' % (version))

# =============================================================================
# give the dataset max speeds based on the given weights in the extract_osm function
# =============================================================================
    gpd_country = gpd.read_file(country_path_in)
    weights = {1: '80', 2:'60', 3: '50', 4:'40',5:'40'}
    gpd_country['speed'] = gpd_country['weight'].map(lambda x: np.int(weights[x]))
    gpd_country.crs = {'init' :'epsg:4326'}
    gpd_country.to_file(country_path_2)
    
# =============================================================================
#     # load country graph
# =============================================================================
    g = nx.read_shp(country_path_2)
    sg = max(nx.connected_component_subgraphs(g.to_undirected()), key=len)

# =============================================================================
#     # read nodes
# =============================================================================
    nodes = np.array(sg.nodes())

# =============================================================================
#     # get dict with all the nodes   
# =============================================================================
    pos = {k: v for k,v in enumerate(sg.nodes())}

# =============================================================================
#     # load nodes from tanroads
# =============================================================================
    node_path = os.path.join(base_path,'input_data','nodes_2017.shp')
    nodes_tanroads = gpd.read_file(node_path)
    
# =============================================================================
#     # Load tanroads all
# =============================================================================
    tanroads_path = os.path.join(base_path,'calc','tanroads_all_2017.shp')
    tanroads_2017 = gpd.read_file(tanroads_path)    
    tanroads_2017.geometry
    combi_routes = list(zip(list(tanroads_2017.startumber),list(tanroads_2017.endnoumber)))
    
# =============================================================================
#     # Compute the length of the road segments.
# =============================================================================
    for n0, n1 in sg.edges():
        path = get_path(n0, n1,sg)
        distance = get_path_length(path)
        sg[n0][n1]['distance'] = distance
        sg[n0][n1]['t_time'] = distance/sg[n0][n1]['speed']    
        
# =============================================================================
# MAIN CALCULATION: find and compare geometries between osm and tanroads
# =============================================================================
    inb_shortest = {}
    count = 0
    failures = []
    for route in combi_routes:    
        try:
            origin = np.array(nodes_tanroads[nodes_tanroads['NodeNumber'] == route[0]].geometry.y)[0],np.array(nodes_tanroads[nodes_tanroads['NodeNumber'] == route[0]].geometry.x)[0]
            destination = np.array(nodes_tanroads[nodes_tanroads['NodeNumber'] == route[1]].geometry.y)[0],np.array(nodes_tanroads[nodes_tanroads['NodeNumber'] == route[1]].geometry.x)[0]
        
            pos0_i = np.argmin(np.sum((nodes[:,::-1] - origin)**2, axis=1))
            pos1_i = np.argmin(np.sum((nodes[:,::-1] - destination)**2, axis=1))            

            # Compute the shortest path.
            path = nx.shortest_path(sg,
                                    source=tuple(nodes[pos0_i]),
                                    target=tuple(nodes[pos1_i]),
                                    weight='distance')
            
            roads = pd.DataFrame([sg[path[i]][path[i + 1]]
                                  for i in range(len(path) - 1)],
                                 columns=['osm_id', 'name','Wkt',
                                          'highway', 'weight','t_time','distance'])
            
        
            roads['geometry'] = roads['Wkt'].map(shapely.wkt.loads)
            roads.drop('Wkt', axis=1,inplace=True) 
            lines = shapely.ops.linemerge(list(roads.geometry))
            get_index = tanroads_2017.query('startumber == %s and endnoumber == %s' % (route[0],route[1])).index[0]
            distance = roads['distance'].sum()
            distance_tr = get_path_length(np.array(list(tanroads_2017.loc[get_index].geometry.coords)))

# =============================================================================
# update geodataframe based on difference in distance. If osm is shorter, use osm
# =============================================================================
            if distance < distance_tr: 
                inb_shortest[route] = lines
            else:
                inb_shortest[route] = tanroads_2017.loc[get_index].geometry
        except:
            failures.append(route)
            count += 1
            get_index = tanroads_2017.query('startumber == %s and endnoumber == %s' % (route[0],route[1])).index[0]
            inb_shortest[route] = tanroads_2017.loc[get_index].geometry

# =============================================================================
# and create a list of the geometries with all the new routes
# =============================================================================
    inb_list = []     
    for route in combi_routes:    
        inb_list.append(inb_shortest[route])

# =============================================================================
# and save to new file
# =============================================================================
    tanroads_2017['geometry'] = inb_list
    tanroads_2017.to_file(country_path_out)


    
    