# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 14:16:47 2017

@author: cenv0574
"""

import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Point,LineString, shape,MultiPoint
import fiona
from rtree import index

def update_network(shape_in,nodes_in,shape_out,basepath,update_in=None):

# =============================================================================
#     Load data
# =============================================================================
    country_data = os.path.join(base_path,'input_data',shape_in)
    country_out = os.path.join(base_path,'output_data',shape_out)
    nodes_data = os.path.join(base_path,'input_data',nodes_in)

# =============================================================================
#    Read data
# =============================================================================
    tza_network = gpd.read_file(country_data)
    nodes_in =  gpd.read_file(nodes_data)   

# =============================================================================
# If osm is not satisfying or it just did not work, update some geometries the
#    hard way
# =============================================================================

    if update_in is not None:
        update_data = os.path.join(base_path,'calc',update_in)
        tza_update = gpd.read_file(update_data) 

        for update in tza_update.iterrows():
            link = int(pd.DataFrame(update[1]).T.link)
            tza_network = tza_network[tza_network.link != int(link)]
    
        tza_new = tza_network.append(tza_update, ignore_index=True)
        tza_new = gpd.GeoDataFrame(tza_new,geometry=tza_new.geometry)

    else:
        tza_new = tza_network

# =============================================================================
# Create spatial index of nodes
# =============================================================================
    idx_inters = index.Index()

    with fiona.open(nodes_data) as all_nodes_in:
        inters = []        
        for node in all_nodes_in:
            idx_inters.insert(int(node['id']), shape(node['geometry']).bounds, node)
            inters.append(shape(node['geometry']))    

# =============================================================================
#     Loop through rows of tanroads network and check if the nodes close to the 
#   network are indeed the nodes there. If not, update
# =============================================================================

    df_fix = []
    for row in tza_new.iterrows():
        line = shape(row[1]['geometry'])    
        line_endpoint_a = (list(line.coords)[0])
        line_endpoint_b = (list(line.coords)[-1])

        # lookup which points are nearest to start and end points        
        point_A = [n.object for n in idx_inters.nearest(line_endpoint_a, objects=True)][0]['properties']['NodeNumber']
        point_A_name = [n.object for n in idx_inters.nearest(line_endpoint_b, objects=True)][0]['properties']['NodeName']
        point_B = [n.object for n in idx_inters.nearest(line_endpoint_b, objects=True)][0]['properties']['NodeNumber']
        point_B_name = [n.object for n in idx_inters.nearest(line_endpoint_b, objects=True)][0]['properties']['NodeName']
    
        # And update each row based on the possible mistake    
        if ((int(row[1]['startumber']) == point_A) & (int(row[1]['endnoumber']) == point_B)) | ((int(row[1]['startumber']) == point_B) & (int(row[1]['endnoumber']) == point_A)):
            df_fix.append(row[1])
        elif ((int(row[1]['startumber']) == point_A) & (int(row[1]['endnoumber']) != point_B)):
            row[1]['endnoumber'] = point_B
            row[1]['endnoename'] = point_B_name
            df_fix.append(row[1])
        elif ((int(row[1]['startumber']) == point_B) & (int(row[1]['endnoumber']) != point_A)):
            row[1]['endnoumber'] = point_A
            row[1]['endnoename'] = point_A_name
            df_fix.append(row[1])
        elif ((int(row[1]['startumber']) != point_A) & (int(row[1]['endnoumber']) == point_B)):
            row[1]['startumber'] = point_A
            row[1]['startename'] = point_A_name
            df_fix.append(row[1])
        elif ((int(row[1]['startumber']) != point_B) & (int(row[1]['endnoumber']) == point_A)):
            row[1]['startumber'] = point_B
            row[1]['startename'] = point_B_name
            df_fix.append(row[1])
        elif ((int(row[1]['startumber']) != point_A) & (int(row[1]['endnoumber']) != point_B)):
            row[1]['startumber'] = point_A
            row[1]['startename'] = point_A_name  
            row[1]['endnoumber'] = point_B
            row[1]['endnoename'] = point_B_name            
            df_fix.append(row[1])
                        
    # and merge and write to a new file        
    df_new = []
    df_fix = gpd.GeoDataFrame(df_fix)


# =============================================================================
#  And if needed, snap the network to the nearest node, to make sure it is consistent and closed network
# =============================================================================
    for row in df_fix.iterrows():
        line = shape(row[1]['geometry'])
        line_endpoint_a = list(line.coords)[0]
        line_endpoint_b = list(line.coords)[-1]
        if (len(nodes_in[nodes_in['NodeNumber'] == row[1]['startumber']]) >= 1) & (len(nodes_in[nodes_in['NodeNumber'] == row[1]['endnoumber']]) >= 1):
            start_node = list(nodes_in[nodes_in['NodeNumber'] == row[1]['startumber']].geometry)[0]
            end_node = list(nodes_in[nodes_in['NodeNumber'] == row[1]['endnoumber']].geometry)[0]
    
            start_to_a = start_node.distance(Point(line_endpoint_a))
            start_to_b = start_node.distance(Point(line_endpoint_b))
            
            list_line = list(MultiPoint(line.coords))
            
            if start_to_a < start_to_b:
                list_line = [start_node] + list_line + [end_node]
            else:
                list_line = [end_node] + list_line + [start_node]
            
            row[1]['geometry'] = LineString(list_line)
            df_new.append(row[1])
        else:
            df_new.append(row[1])

    tza_new = gpd.GeoDataFrame(df_new)
    tza_new.to_file(country_out)  

if __name__ == "__main__":

    base_path = os.path.join(os.path.dirname(__file__), '..')

      