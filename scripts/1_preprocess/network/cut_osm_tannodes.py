# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 10:38:59 2017

@author: cenv0574
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:56:29 2017
@author: cenv0574
"""
from shapely.geometry import LineString, shape,MultiPoint
import fiona
import os
import fiona.crs
import geopandas as gpd
import time
import numpy as np
import shapely.ops
from rtree import index
from shapely.ops import nearest_points

if __name__ == "__main__":

    curdir = os.getcwd()

    # Specify data to download
    continent = 'africa' 
    country = 'tanzania'
    infra_type = 'highway' 
    
    start = time.time()
    
    # download dir osm.pbf
    osm_path = os.path.join(curdir,'..','..','Extract_osm')

    # create output dir
    dir_in = os.path.join(curdir,'..','input_data')

    shape_in = os.path.join(dir_in,'%s-%s.shp' % (country,infra_type))
    shp_out = os.path.join(dir_in,'%s-%s-tr.shp' % (country,infra_type))

    nodes_in = os.path.join(dir_in,'nodes_2017.shp')

    # Initialize Rtree
    idx_osm = index.Index()
    idx_inters = index.Index()

    idx_linepoints = index.Index()
    
    # Load data    
    with fiona.open(shape_in) as shape_input:
#        print(shape_input.schema)
        all_data = []
        i = 0

        for line in shape_input:
            all_data.append(line)
            idx_osm.insert(i, shape(line['geometry']).bounds, line)
            i += 1
            
           
            inb = shape(line['geometry'])
            test = inb.xy
            
    with fiona.open(nodes_in) as all_nodes_in:
        inters = []        
        for node in all_nodes_in:
            idx_inters.insert(i, shape(node['geometry']).bounds, node)
            inters.append(shape(node['geometry']))


    # cut lines where necessary and save all new linestrings to a list 
    new_lines = []
    new_new = []
    new_new2 = []

    count = 0
    for line in all_data:
        hull = shape(line['geometry']).convex_hull
        hits = list(filter(hull.contains, inters))

        if len(hits) != 0:
            count += 1
            all_points = MultiPoint(list(shape(line['geometry']).coords))
            for hit in hits:
                hit = nearest_points(all_points, hit)[0]     
                out = shapely.ops.split(shape(line['geometry']), hit) #MultiPoint(hits))
                new_lines.append([{'geom': LineString(x), 'osm_id':line['properties']['osm_id'], 'name': line['properties']['name'],'service':line['properties']['service'],infra_type:line['properties'][infra_type]} for x in out.geoms])
        else:
            new_lines.append([{'geom': shape(line['geometry']), 'osm_id':line['properties']['osm_id'], 'name': line['properties']['name'],
                    'service':line['properties']['service'],infra_type:line['properties'][infra_type]}])

    print('Cutting is finished')


    # Create one big list and treat all the cutted lines as unique lines    
    flat_list = []
    #item for sublist in new_lines for item in sublist
    for sublist in new_lines:
        if sublist is not None:
            for item in sublist:
                flat_list.append(item)
    
    # Transform into geodataframe and add coordinate system        
    full_gpd = gpd.GeoDataFrame(flat_list,geometry ='geom')

#    if 'highway' in infra_type:
    dic = {'motorway': 1, 'trunk': 2, 'primary': 3,'secondary': 4, 'tertiary':4}
    full_gpd['weight'] = 0
    full_gpd['weight'] = full_gpd['highway'].apply(lambda x: dic[x])

    # Save geodataframe to shapefile
    full_gpd.crs = {'init' :'epsg:4326'}

    full_gpd.to_file(shp_out)

    end = time.time()    
    print('It took ' + str(np.float16((end - start))) + " seconds to finish the %s network of %s!" % (infra_type,country))     

