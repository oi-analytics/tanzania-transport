"""Generate detailed road network map of Tanzania
"""
# pylint: disable=C0103
import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import shapely.geometry

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.utils import *


def main():
    """Setup data loading, loop over regions
    """
    config = load_config()
    data_path = config['data_path']
    figures_path = config['figures_path']

    regions = [
        'Arusha',
        'Dar-Es-Salaam',
        'Dodoma',
        'Geita',
        'Iringa',
        'Kagera',
        'Katavi',
        'Kigoma',
        'Kilimanjaro',
        'Lindi',
        'Manyara',
        'Mara',
        'Mbeya',
        'Morogoro',
        'Mtwara',
        'Mwanza',
        'Njombe',
        'Pwani',
        'Rukwa',
        'Ruvuma',
        'Shinyanga',
        'Simiyu',
        'Singida',
        'Tabora',
        'Tanga'
    ]

    # Input data
    inf_path = os.path.join(data_path, 'Infrastructure')

    # Roads
    trunk_road_filename = os.path.join(inf_path, 'Roads', 'road_shapefiles', 'tanroads_main_all_2017_adj.shp')

    # Railways
    railway_ways_filename = os.path.join(inf_path, 'Railways', 'railway_shapefiles', 'tanzania-rail-ways-processed.shp')

    # Ports
    ports_filename = os.path.join(inf_path, 'Ports', 'port_shapefiles', 'tz_port_nodes.shp')
    port_edges_filename = os.path.join(inf_path, 'Ports', 'port_shapefiles', 'tz_port_edges.shp')

    # Airports
    airport_filename = os.path.join(inf_path, 'Airports', 'airport_shapefiles', 'tz_od_airport_nodes.shp')

    # Regions
    provinces_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_1_states_provinces_lakes.shp'
    )

    data = {
        'road': list(shpreader.Reader(trunk_road_filename).records()),
        'rail': list(shpreader.Reader(railway_ways_filename).records()),
        'port': list(shpreader.Reader(ports_filename).records()),
        'waterway': list(shpreader.Reader(port_edges_filename).records()),
        'air': list(shpreader.Reader(airport_filename).records()),
        'regions': [
            record
            for record in shpreader.Reader(provinces_filename).records()
            if record.attributes['iso_a2'] == 'TZ'
        ]
    }


    for flood_type in ['current_fluvial', 'future_fluvial', 'current_pluvial']:
        data['flood_5'] = get_flood_extents(data_path, flood_type, 5)
        data['flood_1000'] = get_flood_extents(data_path, flood_type, 1000)

        for region_name in regions:
            print("Plotting", region_name, flood_type)
            create_regional_map(data_path, figures_path, region_name, flood_type, data)


def get_flood_extents(data_path, flood_type, return_period):
    """Return flood extents at 1m depth for given flood type and return period
    """
    extents = []
    if flood_type == 'current_fluvial':
        # EUWATCH
        extents += list(shpreader.Reader(
            os.path.join(
                data_path,
                'tanzania_flood',
                'threshold_1',
                'EUWATCH_{:05d}_mask-1.shp'.format(return_period)
            )
        ).records())
        # SSBN fluvial
        extents += list(shpreader.Reader(
            os.path.join(
                data_path,
                'tanzania_flood',
                'threshold_1',
                'SSBN_FU_{}_mask-1.shp'.format(return_period)
            )
        ).records())
    if flood_type == 'current_pluvial':
        # SSBN pluvial
        extents += list(shpreader.Reader(
            os.path.join(
                data_path,
                'tanzania_flood',
                'threshold_1',
                'SSBN_PU_{}_mask-1.shp'.format(return_period)
            )
        ).records())
    if flood_type == 'future_fluvial':
        # GLOFRIS
        models = [
            'GFDL-ESM2M',
            'HadGEM2-ES',
            'IPSL-CM5A-LR',
            'MIROC-ESM-CHEM',
            'NorESM1-M',
        ]
        for model in models:
            extents += list(shpreader.Reader(
                os.path.join(
                    data_path,
                    'tanzania_flood',
                    'threshold_1',
                    '{}_{:05d}_mask-1.shp'.format(model, return_period)
                )
            ).records())
    return extents


def create_regional_map(data_path, figures_path, region_name, flood_type, data):
    """Plot single region with local OSM roads
    """
    # Create figure
    plt.figure(figsize=(6, 6), dpi=300)

    proj_lat_lon = ccrs.PlateCarree()
    ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)

    region_extent = get_region_extent(region_name, data['regions'])

    ax.set_extent(region_extent, crs=proj_lat_lon)

    # Background
    plot_basemap(ax, data_path)
    plot_basemap_labels(ax, data_path)

    # Output
    output_filename = os.path.join(
        figures_path,
        'exposure_maps',
        'exposure_map_{}_{}.png'.format(region_name, flood_type)
    )

    # Roads
    trunk = [
        record.geometry
        for record in data['road']
        if record.attributes['roadclass'] == 'T'
    ]
    regional = [
        record.geometry
        for record in data['road']
        if record.attributes['roadclass'] != 'T'
    ]

    ax.add_geometries(
        trunk,
        crs=proj_lat_lon,
        edgecolor='#d1170a',
        facecolor='none',
        zorder=5)

    ax.add_geometries(
        regional,
        crs=proj_lat_lon,
        edgecolor='#ed9a36',
        facecolor='none',
        zorder=5)

    # Railways
    rail = [record.geometry for record in data['rail']]
    ax.add_geometries(
        rail,
        crs=proj_lat_lon,
        edgecolor='#33a02c',
        facecolor='none',
        zorder=5)

    # Ferry routes
    water = [record.geometry for record in data['waterway']]
    ax.add_geometries(
        water,
        crs=proj_lat_lon,
        edgecolor='#051591',
        facecolor='none',
        zorder=5)

    # Ferry ports
    xs = [record.geometry.x for record in data['port']]
    ys = [record.geometry.y for record in data['port']]
    ax.scatter(xs, ys, facecolor='#051591', s=11, zorder=6)

    # Airports
    airports = (
        'Julius Nyerere International Airport',
        'Arusha Airport',
        'Kilimanjaro International Airport'
    )
    xs = [
        record.geometry.x
        for record in data['air']
        if record.attributes['name'] in airports
    ]
    ys = [
        record.geometry.y
        for record in data['air']
        if record.attributes['name'] in airports
    ]
    ax.scatter(xs, ys, facecolor='#5b1fb4', s=11, zorder=6)

    # 5yr
    flood_5 = [record.geometry for record in data['flood_5']]
    ax.add_geometries(
        flood_5,
        crs=proj_lat_lon,
        facecolor='#2d8ccb',
        edgecolor='none',
        zorder=4)

    # 1000yr
    flood_1000 = [record.geometry for record in data['flood_1000']]
    ax.add_geometries(
        flood_1000,
        crs=proj_lat_lon,
        facecolor='#00519e',
        edgecolor='none',
        zorder=3)

    # Mask
    mask = [
        record.geometry
        for record in data['regions']
        if record.attributes['name'] != region_name
    ]
    ax.add_geometries(
        mask,
        crs=proj_lat_lon,
        facecolor='#ffffff',
        alpha=0.5,
        edgecolor='none',
        zorder=99)

    # Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(
        fontsize=8,
        handles=[
            mpatches.Patch(label="5yr return", color='#2d8ccb'),
            mpatches.Patch(label="1000yr return", color='#00519e'),
            mpatches.Patch(label="Trunk Road", color='#d1170a'),
            mpatches.Patch(label="Regional Road", color='#ed9a36'),
            mpatches.Patch(label="Railway", color='#33a02c'),
            mpatches.Patch(label="Port/Waterway", color='#051591'),
            mpatches.Patch(label="Airport", color='#5b1fb4'),
        ],
        loc='lower left',
        bbox_to_anchor=(1, 0.5)
    )
    save_fig(output_filename)
    plt.close()


def add_context(data_path, zoom_extent):
    """Use plt global to add context box in bottom right
    """
    proj_lat_lon = ccrs.PlateCarree()
    ax = plt.axes([0.72, 0.05, 0.3, 0.25], projection=proj_lat_lon)
    tz_extent = (28.6, 41.4, -0.1, -13.2)
    ax.set_extent(tz_extent, crs=proj_lat_lon)

    plot_basemap(ax, data_path)

    # Zoom extent: e.g. (37.5, 39.5, -8.25, -6.25)
    x0, x1, y0, y1 = zoom_extent
    box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
    ax.add_geometries([box], crs=proj_lat_lon, edgecolor='#000000', facecolor='none')


def get_region_extent(region_name, regions):
    """Load region geom, return bbox as [x0, x1, y0, y1]
    """
    for record in regions:
        region = record.attributes['name']
        if region == region_name:
            xmin, ymin, xmax, ymax = record.geometry.bounds
            buffer = 0.2
            return [xmin - buffer, xmax + buffer, ymin - buffer, ymax + buffer]

    raise KeyError("Region {} not found in regions".format(region_name))


if __name__ == '__main__':
    main()
