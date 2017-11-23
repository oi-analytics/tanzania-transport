# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 13:27:10 2017

@author: cenv0574
"""

import networkx as nx
import numpy as np
import pandas as pd
import json
import matplotlib as mpl

#plt.ioff()

mpl.rcParams['figure.dpi'] = mpl.rcParams['savefig.dpi'] = 100

def get_path(sg,n0, n1):
    """If n0 and n1 are connected nodes in the graph, this function
    return an array of point coordinates along the road linking
    these two nodes."""
    return np.array(json.loads(sg[n0][n1]['Json'])['coordinates'])

def get_path_subset(sg,n0, n1):
    """If n0 and n1 are connected nodes in the graph, this function
    return an array of point coordinates along the road linking
    these two nodes."""
    return np.array(json.loads(sg[n0][n1]['attr']['Json'])['coordinates'])

def geocalc(lat0, lon0, lat1, lon1):
    """Return the distance (in km) between two points in
    geographical coordinates."""
    
    EARTH_R = 6372.8
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


def get_full_path(sg,path):
    """Return the positions along a path."""
    p_list = []
    curp = None
    for i in range(len(path)-1):
        p = get_path(sg,path[i], path[i+1])
        if curp is None:
            curp = p
        if np.sum((p[0]-curp)**2) > np.sum((p[-1]-curp)**2):
            p = p[::-1,:]
        p_list.append(p)
        curp = p[-1]
    return np.vstack(p_list)

def get_shortest_distance(sg,nodes,geom_in):
    pos0 = geom_in.y,geom_in.x
    pos0_i = np.argmin(np.sum((nodes[:,::-1] - pos0)**2, axis=1))
    sg_subset = nx.Graph()
    for n0,n1 in nx.bfs_edges(sg,tuple(nodes[pos0_i])):
        sg_subset.add_edge(n0,n1,attr=sg[n0][n1])
        if sg[n0][n1]['highway'] == 'trunk' or sg[n0][n1]['highway'] == 'primary':
            end_points = [n0,n1]
            break

    nodes_sub = np.array(sg_subset.nodes())

    for n0, n1 in sg_subset.edges():
        path = get_path_subset(sg_subset,n0, n1)
        distance = get_path_length(path)
        sg_subset[n0][n1]['distance'] = distance   
    inb = []
    for point in end_points:   
         # Compute the length of the road segments.
        # Get the closest nodes in the graph.
        pos0_i = np.argmin(np.sum((nodes_sub[:,::-1] - pos0)**2, axis=1))
        pos1_i = np.argmin(np.sum((nodes_sub[:,::-1] - tuple(reversed(point)))**2, axis=1))
       
        # Compute the shortest path.
        path = nx.shortest_path(sg_subset,
                                source=tuple(nodes_sub[pos0_i]),
                                target=tuple(nodes_sub[pos1_i]),
                                weight='distance')
        
        roads = pd.DataFrame([sg_subset[path[i]][path[i + 1]]
                              for i in range(len(path) - 1)],
                             columns=['osm_id', 'name',
                                      'highway','distance'])
        
        if roads['distance'].sum() > 0:
            inb.append(roads['distance'].sum())
 
    return min(inb)

