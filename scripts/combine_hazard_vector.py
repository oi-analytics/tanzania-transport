"""Combine hazard vector polygons from thresholds to bands
"""
import os
import fiona
import shapely.geometry
import shapely.ops

def main():
    rps = [
        '00002',
        '00005',
        '00025',
        '00050',
        '00100',
        '00250',
        '00500',
        '01000'
    ]

    # Convert EUWATCH observations
    euwatch_output_path = os.path.join('data', 'tanzania_flood', 'hazard_bands_euwatch.shp')
    output_schema = {
        'geometry': 'MultiPolygon',
        'properties': {
            'model': 'str',
            'r_period': 'int',
            'threshold': 'str',
            'upper': 'float',
            'lower': 'float'
        }
    }
    with fiona.open(
            euwatch_output_path, 'w',
            schema=output_schema,
            driver='ESRI Shapefile',
            crs={'no_defs': True, 'ellps': 'WGS84', 'datum': 'WGS84', 'proj': 'longlat'}
            ) as sink:
        for rp in reversed(rps):
            for band in combine('EUWATCH', rp):
                sink.write(band)

    # # Convert models
    # models = ['GFDL-ESM2M', 'HadGEM2-ES', 'IPSL-CM5A-LR', 'MIROC-ESM-CHEM', 'NorESM1-M']

    # glofris_output_path = os.path.join('data', 'tanzania_flood', 'hazard_bands_glofris.shp')
    # for model in models:
    #     for rp in rps:
    #         combine(model, rp)

    # # Convert SSBN models
    # ssbn_rps = ['5', '10', '20', '50', '75', '100', '200', '250', '500', '1000']
    # ssbn_models = {
    #     'TZ_fluvial_defended': 'SSBN_FD',
    #     'TZ_fluvial_undefended': 'SSBN_FU',
    #     'TZ_pluvial_defended': 'SSBN_PD',
    #     'TZ_pluvial_undefended': 'SSBN_PU',
    #     'TZ_urban_defended': 'SSBN_UD',
    #     'TZ_urban_undefended': 'SSBN_UU'
    # }

    # ssbn_output_path = os.path.join('data', 'tanzania_flood', 'hazard_bands_ssbn.shp')
    # for model, abbr in ssbn_models.items():
    #     for rp in ssbn_rps:
    #         bands = combine(abbr, rp)

def combine(model, rp):
    thresholds = [
        # '0.25',
        # '0.5',
        '0.75',
        '1',
        # '1.25',
        # '1.5',
        '1.75',
        '2',
        # '2.25',
        # '2.5',
        '2.75',
        '3'
    ]

    prev_threshold_num = None
    prev_mp = None

    # loop in REVERSE order down through thresholds
    for threshold in reversed(thresholds):
        threshold_num = float(threshold)
        rp_num = int(rp)
        label = '{}-{}'.format(threshold_num, prev_threshold_num)
        print(model, rp, label)
        mp = read_threshold_multipolygon(model, rp, threshold)

        if prev_mp is None:
            # threshold is upper limit, so copy over as "{threshold}-inf" band
            band_mp = mp
            # initialise prev multipolygon
            prev_mp = mp
        else:
            # clip threshold by previous, creating "{threshold}-{prev}" band
            diff = mp.difference(prev_mp)
            if not diff.is_empty:
                band_mp = diff
                # update prev multipolygon only if output band
                prev_mp = mp
            else:
                print("WARNING: empty band", model, rp, label)
                band_mp = None


        if band_mp is not None:
            yield {
                'type': 'Feature',
                'properties': {
                    'model': model,
                    'r_period': rp_num,
                    'threshold': label,
                    'upper': prev_threshold_num,
                    'lower': threshold_num
                },
                'geometry': shapely.geometry.mapping(band_mp)
            }

        # update previous threshold
        prev_threshold_num = threshold_num


def read_threshold_multipolygon(model, rp, threshold):
    polys = []
    with fiona.open(get_threshold_path(model, rp, threshold)) as source:
        for poly in source:
            polys.append(shapely.geometry.shape(poly['geometry']))
    return shapely.geometry.MultiPolygon(shapely.ops.cascaded_union(polys))

def get_threshold_path(model, rp, threshold):
    """Return path to threshold vector, e.g.
        data/tanzania_flood/threshold_0.25/EUWATCH_010000_mask-0.25.shp
    """
    return os.path.join(
        'data',
        'tanzania_flood',
        'threshold_{}'.format(threshold),
        '{}_{}_mask-{}.shp'.format(model, rp, threshold)
    )

if __name__ == '__main__':
    main()
