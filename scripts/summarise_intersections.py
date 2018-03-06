"""Summarise intersections with raster
"""
import csv
import os


def main():
    print("Reading exposure")
    exposure = read_exposure()
    print("Writing exposure")
    write_exposure_by_model(exposure)
    write_exposure_sparse(exposure)


def read_exposure():
    """Read intersections produced by `intersect_networks_with_raster.py`

    Returns
    -------
    exposure: dict of dict
        keys are tuple(sector, id) and values are dicts to lookup exposure
        with keys tuple(model, return_period, (lower, upper)) and values bool
    """
    path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'hazard_network_intersections.csv'
    )
    # header = [
    #     'network_element',
    #     'sector',
    #     'id',
    #     'model',
    #     'return_period',
    #     'flood_depth'
    # ]
    exposure = {}
    with open(path, 'r') as fh:
        r = csv.DictReader(fh)
        for line in r:
            asset_key = (line['sector'], line['id'])

            if asset_key not in exposure:
                exposure[asset_key] = {}

            bounds = get_bounds_for_val(float(line['flood_depth']))
            hazard_key = (line['model'], int(line['return_period']), bounds)

            exposure[asset_key][hazard_key] = True

    return exposure


def write_exposure_by_model(exposure):
    """Write fat table, one row per exposed asset, columns for model/rp/bound
    """
    path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'hazard_network_exposure.csv'
    )
    header = ['sector', 'id'] + [key for key, tup in get_model_rp_bounds()]
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for (sector, asset_id), asset_exposure in exposure.items():
            out = {
                'sector': sector,
                'id': asset_id
            }
            for key_string, model_rp_bounds in get_model_rp_bounds():
                if model_rp_bounds in asset_exposure:
                    out[key_string] = 1
                else:
                    out[key_string] = 0
            w.writerow(out)


def write_exposure_sparse(exposure):
    """Write table, one row per exposed asset, column with list of exposure
    """
    path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'hazard_network_exposure_sparse.csv'
    )
    header = ['sector', 'id', 'exposure']
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for (sector, asset_id), asset_exposure in exposure.items():
            out = {
                'sector': sector,
                'id': asset_id,
                'exposure': list(asset_exposure.keys())
            }
            w.writerow(out)


def get_bounds_for_val(val):
    bounds = get_bounds()
    bound = None
    for lower, upper in bounds:
        if val > lower and val <= upper:
            bound = (lower, upper)
            break
    return bound

def get_bounds():
    """Single place where series of thresholds 'bounds' are defined
    """
    return [
        (0.25, 0.5),
        (0.5, 1.0),
        (1.0, 1.5),
        (1.5, 2.0),
        (2.0, 2.5),
        (2.5, 3.0),
        (3.0, 1000)
    ]

def get_model_rp_bounds():
    """Return a list of string_key, data_tuple tuples

    each string_key is for csv header output, like "{model}_{rp}_{lower}-{upper}"
        e.g. "EUWATCH_1000_0.25-0.5"
    each data_tuple is like tuple(model, return_period, (lower, upper)) (see dict keys above)
    """
    details = []
    bounds = get_bounds()

    rps = [
        2,
        5,
        25,
        50,
        100,
        250,
        500,
        1000
    ]
    for rp in rps:
        for lower, upper in bounds:
            details.append((
                "{}_{}_{}-{}".format('EUWATCH', rp, lower, upper),
                ('EUWATCH', rp, (lower, upper))
            ))

    glofris_models = [
        'GFDL-ESM2M',
        'HadGEM2-ES',
        'IPSL-CM5A-LR',
        'MIROC-ESM-CHEM',
        'NorESM1-M'
    ]
    for model in glofris_models:
        for rp in rps:
            for lower, upper in bounds:
                details.append((
                    "{}_{}_{}-{}".format(model, rp, lower, upper),
                    (model, rp, (lower, upper))
                ))

    # SSBN models have a different set of return periods
    ssbn_rps = [
        5,
        10,
        20,
        50,
        75,
        100,
        200,
        250,
        500,
        1000
    ]
    ssbn_models = [
        'FD', # TZ_fluvial_defended
        'FU', # TZ_fluvial_undefended
        'PD', # TZ_pluvial_defended
        'PU', # TZ_pluvial_undefended
        'UD', # TZ_urban_defended
        'UU' # TZ_urban_undefended
    ]
    for model in ssbn_models:
        for rp in ssbn_rps:
            for lower, upper in bounds:
                details.append((
                    "{}_{}_{}-{}".format(model, rp, lower, upper),
                    (model, rp, (lower, upper))
                ))

    return details


if __name__ == '__main__':
    main()
