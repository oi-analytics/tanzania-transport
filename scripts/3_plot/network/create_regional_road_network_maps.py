"""Generate detailed road network map of Tanzania
"""
# pylint: disable=C0103
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import shapely.geometry

from utils import plot_pop, plot_countries, plot_regions

def main():
    """Setup data loading, loop over regions
    """
    # Input data
    base_path = os.path.join(os.path.dirname(__file__), '..')
    data_path = os.path.join(base_path, 'data')

    # Roads
    tanroad_filename = os.path.join(
        data_path, 'Analysis_results', 'spof_localfailure_results', 'tz_road_spof_geom.shp')

    tanroads = [
        record.geometry
        for record in shpreader.Reader(tanroad_filename).records()
    ]

    regions = [
        'Arusha',
        # 'Dar-Es-Salaam',
        'Dodoma',
        'Iringa',
        'Kagera',
        'Kigoma',
        'Kilimanjaro',
        'Lindi',
        'Manyara',
        'Mara',
        'Mbeya',
        'Morogoro',
        'Mtwara',
        'Mwanza',
        'Pwani',
        'Rukwa',
        'Ruvuma',
        'Shinyanga',
        'Singida',
        'Tabora',
        'Tanga'
    ]

    for region_name in regions:
        print("Plotting", region_name)
        create_regional_map(base_path, data_path, tanroads, region_name)


def create_regional_map(base_path, data_path, tanroads, region_name):
    """Plot single region with local OSM roads
    """
    # Create figure
    plt.figure(figsize=(6, 6), dpi=150)

    proj_lat_lon = ccrs.PlateCarree()
    proj_3857 = ccrs.epsg(3857)
    ax = plt.axes([0.025, 0.025, 0.95, 0.93], projection=proj_lat_lon)

    region_extent = get_region_extent(data_path, region_name)

    ax.set_extent(region_extent, crs=proj_lat_lon)

    # Background
    plot_countries(ax, data_path)
    plot_pop(plt, ax, data_path)
    plot_regions(ax, data_path)

    ax.add_geometries(
        tanroads,
        crs=proj_lat_lon,
        linewidth=1,
        edgecolor='#d1170a',
        facecolor='none',
        zorder=3)

    osm_roads = get_region_osm_roads(data_path, region_name)

    ax.add_geometries(
        [road.geometry for road in osm_roads],
        crs=proj_lat_lon,
        linewidth=1,
        edgecolor='#ed9a36',
        facecolor='none',
        zorder=2)


    # Legend
    legend_handles = [
        mpatches.Patch(color='#d1170a', label='TANROADS Trunk and Regional Roads'),
        mpatches.Patch(color='#ed9a36', label='OpenStreetMap Roads'),
    ]
    plt.legend(
        handles=legend_handles,
        loc='lower left'
    )
    plt.title('TANROADS and OpenStreetMap Roads in {}, Tanzania'.format(region_name))

    add_context(data_path, region_extent)

    output_filename = os.path.join(
        base_path,
        'figures',
        'road_network_map_{}.png'.format(region_name)
    )
    plt.savefig(output_filename)
    plt.close()


def add_context(data_path, zoom_extent):
    """Use plt global to add context box in bottom right
    """
    proj_lat_lon = ccrs.PlateCarree()
    ax = plt.axes([0.72, 0.05, 0.3, 0.25], projection=proj_lat_lon)
    tz_extent = (28.6, 41.4, -0.1, -13.2)
    ax.set_extent(tz_extent, crs=proj_lat_lon)

    states_filename = os.path.join(
        data_path, 'Infrastructure', 'Boundaries', 'ne_10m_admin_0_countries_lakes.shp')

    for record in shpreader.Reader(states_filename).records():
        country_code = record.attributes['ISO_A2']
        # Neighbours
        if country_code in ('BI', 'RW', 'CD', 'UG', 'KE', 'ZM', 'MW', 'MZ', 'SO'):
            geom = record.geometry
            ax.add_geometries([geom], crs=proj_lat_lon, edgecolor='white', facecolor='#efefef')
        # Tanzania
        if country_code == 'TZ':
            geom = record.geometry
            ax.add_geometries([geom], crs=proj_lat_lon, edgecolor='white', facecolor='#d7d7d7')

    # Zoom extent: e.g. (37.5, 39.5, -8.25, -6.25)
    x0, x1, y0, y1 = zoom_extent
    box = shapely.geometry.Polygon(((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)))
    ax.add_geometries([box], crs=proj_lat_lon, edgecolor='#000000', facecolor='#d7d7d700')


def get_region_extent(data_path, region_name):
    """Load region geom, return bbox as [x0, x1, y0, y1]
    """
    # Regions
    provinces_filename = os.path.join(
        data_path,
        'Infrastructure',
        'Boundaries',
        'ne_10m_admin_1_states_provinces_lakes.shp'
    )

    # Regions
    for record in shpreader.Reader(provinces_filename).records():
        country_code = record.attributes['iso_a2']
        region = record.attributes['name']
        if country_code == 'TZ' and region == region_name:
            xmin, ymin, xmax, ymax = record.geometry.bounds
            return [xmin, xmax, ymin, ymax]

    raise KeyError("Region {} not found in regions".format(region_name))


def get_region_osm_roads(data_path, region_name):
    """Load OSM road features
    """
    # Regions
    filename = os.path.join(
        data_path,
        'Infrastructure',
        'Roads',
        'osm_mainroads',
        '{}-highway-1.shp'.format(region_name)
    )

    # Regions
    return shpreader.Reader(filename).records()



if __name__ == '__main__':
    main()
