# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 14:08:29 2018

@author: elcok
"""
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.style.use('ggplot')
mpl.rcParams['font.size'] = 12.
mpl.rcParams['font.family'] = 'tahoma'
mpl.rcParams['axes.labelsize'] = 14.
mpl.rcParams['xtick.labelsize'] = 13.
mpl.rcParams['ytick.labelsize'] = 13.

if __name__ == "__main__":

    '''Set some starting variables. i.e. define region'''
    country = 'Tanzania'

    # Define current directory 
    base_path =   os.path.join(os.path.dirname(__file__),'..')    

    macro_all = os.path.join(base_path,'output','macro_losses2.xlsx')
    map_sect_path = os.path.join(base_path,'output','map_sectors.xlsx')

    
    road_out = pd.read_excel(macro_all,sheet_name='output_road').T
#    road_out = road_out.drop('Total', 1)
    road_out = road_out.reindex(sorted(road_out.columns, key=lambda x: float(x[1:])), axis=1)
    
    rail_out = pd.read_excel(macro_all,sheet_name='output_rail').T
    rail_out = rail_out.reindex(sorted(rail_out.columns, key=lambda x: float(x[1:])), axis=1)

    map_sectors = dict(pd.read_excel(map_sect_path,header=None).values)
    
    road_out = road_out.rename(map_sectors,axis=1)

    # CREATE FIGURE WITH TWO SUBPLOTS
    fig, axes = plt.subplots(nrows=2, ncols=1,figsize=(10,12),sharex=True)

    ax1 = rail_out.boxplot(ax=axes[0], showfliers=False)
    ax1.set_ylabel("Daily output loss", fontweight='bold')
    ax1.set_title('Railway',fontweight='bold')

    
    ax2 = road_out.boxplot(ax=axes[1], showfliers=False)          
    ax2.set_ylabel("Daily output loss", fontweight='bold')
    ax2.set_xlabel("Industrial sector", fontweight='bold')
    ax2.set_title('Road',fontweight='bold')

    plt.setp(ax2.get_xticklabels(), rotation=90)

    fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=.5)
   
    fig.savefig(os.path.join(base_path,'output','macro_losses.png'),dpi=500)
