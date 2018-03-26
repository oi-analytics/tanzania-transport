# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 11:38:17 2017

@author: cenv0574
"""

import os
import pandas as pd
from shapely.geometry import Point,shape
import networkx as nx
import numpy as np
import geopandas as gpd
import rtree.index as index
from multiprocess import Pool , cpu_count 


def dist_junction(region,regions_shape,base_path):
    print('%s started!' % region)
    
    # load nodes
    nodes_in = os.path.join(base_path,'input','nodes_2017.shp')
    tan_nodes = gpd.read_file(nodes_in)
    tan_nodes.to_crs = {'init' :'epsg:4326'}

    # create calc dir
    calc_dir = os.path.join(base_path,'calc')    

    # load dataframe with regions
    regions_shape = os.path.join(base_path,'regions','Tanzania Regions.shp')
    tza_regions = gpd.read_file(regions_shape)
    
    if region == 'Dar-Es-Salaam':
        region_shape = tza_regions[tza_regions['REGION']=='Dar es Salaam']    
    else:
        region_shape = tza_regions[tza_regions['REGION']==region]
        region_shape['geometry'] = region_shape.buffer(0.01)
 
    region_shape.crs = {'init' :'epsg:4326'}
    region = region.replace(" ", "_")

    '''Set file in and output names'''
    network_in = os.path.join(base_path,'cleaned_regions','%s-highway-1.shp' % region)
    shape_in = os.path.join(calc_dir,'%s.shp' % region)
    raster_out = os.path.join(calc_dir,'%s-globpop.tif' % region) 
    raster_in = os.path.join(base_path,'GLOBPOP', 'TZA_popmap15adj_v2c.tif') 
    outCSVName = os.path.join(calc_dir,'points_%s_in.csv' % region) 
    
    region_shape.to_file(shape_in)

    '''Clip Tan Nodes to region'''
    intersections= gpd.sjoin(region_shape, tan_nodes, how="left", op='intersects')
    list_nodes = list(intersections['NodeNumber'])
    region_nodes = tan_nodes[tan_nodes['NodeNumber'].isin(list_nodes)]
    
    Junc_index = index.Index()
    for node in region_nodes.iterrows():
        Junc_index.insert(node[1]['NodeNumber'],Point(node[1]['geometry']).bounds,node[1])

    '''Clip to region and convert to points'''
    os.system('gdalwarp -cutline '+shape_in+' -crop_to_cutline -dstalpha '+raster_in+' '+raster_out+' -t_srs EPSG:4326 -tr 0.004 0.004 -r average')
    os.system('gdal_translate -of XYZ '+raster_out+' '+ outCSVName)#
    load_points = pd.read_csv(outCSVName,header=None,names=['x','y','pop_dens'],index_col=None,sep=' ')
    load_points = load_points[load_points['pop_dens'] > 5] 
 
    geometry = [Point(xy) for xy in zip(load_points.x, load_points.y)]
    load_points =  load_points.drop(['x', 'y'], axis=1) 
    crs = {'init': 'epsg:4326'}
    points_gdp = gpd.GeoDataFrame(load_points, crs=crs, geometry=geometry)

    '''Load networkX network of region'''        
    g = nx.read_shp(network_in)
    g = max(nx.connected_component_subgraphs(g.to_undirected()), key=len)

    pos = {k: v for k,v in enumerate(g.nodes())}
    idx_nodes = index.Index()
    for key, value in pos.items():
        idx_nodes.insert(key,Point(value).bounds,value)
  
    # Get the closest nodes in the graph.
    all_nodes = {}
    get_new_coords = []
    for pop_point in points_gdp.iterrows():
        pop_node = pop_point[1]
        pop_Pt = Point(pop_node['geometry'])
        pos0 = list([n.object for n in idx_nodes.nearest(pop_Pt.bounds, objects=True)])[0]
        all_nodes[pop_point[0]] = [0,pop_node['pop_dens'],Point(pop_Pt)]

        
        get_new_coords.append(Point(pos0))

        close_nodes = list([n.object for n in Junc_index.nearest(pop_Pt.bounds, num_results=1, objects=True)])

        for node in close_nodes:
            jct_Pt = Point(node['geometry'])
            pos1 = list([n.object for n in idx_nodes.nearest(jct_Pt.bounds, objects=True)])[0]
            
            path = nx.shortest_path(g,
                                    source=pos0,
                                    target=pos1)

            out = sum([g[path[i]][path[i + 1]]['distance'] for i in range(len(path) - 1)])

            all_nodes[pop_point[0]][0] = out

    closest_nodes = gpd.GeoDataFrame(pd.DataFrame.from_dict(all_nodes,orient='index'), crs=crs)
    closest_nodes.columns = ['dist_jct','pop_dens','geometry']
    closest_nodes.to_file(os.path.join(base_path,'output_closest_jct','%s.shp' % region))

    for fname in os.listdir(calc_dir):
        if fname.find(region) >= 0:
            os.remove(os.path.join(calc_dir, fname))

if __name__ == "__main__":

    '''Set some starting variables. i.e. define region'''
    country = 'Tanzania'

    # Define current directory and drive letter
    base_path =   os.path.join(os.path.dirname(__file__),'..')    

    # load dataframe with regions
    regions_shape = os.path.join(base_path,'regions','Tanzania Regions.shp')
    tza_regions = gpd.read_file(regions_shape)
   
    regions = list(filter(None.__ne__, tza_regions['REGION']))

    regions = ['Arusha','Dar-Es-Salaam','Dodoma','Iringa','Kagera','Kigoma','Kilimanjaro','Manyara',
               'Tabora','Mbeya','Morogoro','Mtwara','Mwanza','Pwani','Ruvuma','Singida','Rukwa',
               'Lindi','Tanga','Shinyanga','Manyara'] #[

    base_paths = [base_path]*len(regions)
    region_shapes = [regions_shape]*len(regions)
    
    pool = Pool(cpu_count()-1)
    pool.starmap(dist_junction, zip(regions,region_shapes,base_paths)) 

# =============================================================================
#     # merge output of distance to junction    
# =============================================================================
    shp_network = os.path.join(base_path,'output_closest_jct','dist_to_jct_tza.shp')
    
    df_list_regions = []
    for region in regions:
        if len([i for i in os.listdir(os.path.join(base_path,'output_closest_jct')) if i.endswith('%s.shp' % region)]) != 0:
            try:
                country_path = os.path.join(base_path,'output_closest_jct','%s.shp' % (region))
                inb = gpd.read_file(country_path)
                df_list_regions.append(gpd.read_file(country_path))    
            except:
                print('%s doesnt seem to have been finished'  % (region))
    
    shape_net = gpd.GeoDataFrame( pd.concat( df_list_regions, ignore_index=True) )
    shape_net.crs = {'init' :'epsg:4326'}
    shape_net.to_file(shp_network)  

    print('Succesfully created the combined network of %s regions' % (len(regions)))
    
# =============================================================================
#     # merge all roads
# =============================================================================
#    shp_network = os.path.join(base_path,'output','tanzania-all-osm.shp')
#    
#    df_list_regions = []
#    for region in regions:
#        if len([i for i in os.listdir(os.path.join(base_path,'cleaned_regions')) if i.startswith('%s' % region)]) != 0:
#            try:
#                country_path = os.path.join(base_path,'cleaned_regions','%s-highway-1.shp' % (region))
#                inb = gpd.read_file(country_path)
#                df_list_regions.append(gpd.read_file(country_path))    
#            except:
#                print('%s doesnt seem to have been finished'  % (region))
#    
#    shape_net = gpd.GeoDataFrame( pd.concat( df_list_regions, ignore_index=True) )
#    shape_net.crs = {'init' :'epsg:4326'}
#    shape_net.to_file(shp_network)  