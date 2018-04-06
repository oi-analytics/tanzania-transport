"""Threshold hazard data and convert to vector polygons

The key command that defines the threshold is an option to gdal_calc::

    --calc=logical_and(A>={}, A<999)

To run with GNU Parallel::
    seq 0.5 0.5 5 | parallel ./convert_hazard_to_vector.py {}
    seq 6 1 15 | parallel ./convert_hazard_to_vector.py {}

Likely to be difficult to run on Windows unless gdal_calc.py and
gdal_polygonize.py are set up as executables and on the user's PATH
"""
import subprocess
import sys

def main(threshold):
    """Clean output folder, run conversion
    """
    print("Processing", threshold)
    subprocess.run(["rm", "-rf", "data/tanzania_flood/threshold_{}".format(threshold)])
    subprocess.run(["mkdir", "data/tanzania_flood/threshold_{}".format(threshold)])
    for arg_set in generate_args(threshold):
        convert(threshold=threshold, **arg_set)

def generate_args(threshold):
    """Generate file arguments for convert function
    """
    # EUWATCH
    return_periods = ['00005', '00025', '00050', '00100', '00250', '00500', '01000']

    for return_period in return_periods:
        print("EUWATCH", return_period, threshold)
        yield {
            'infile': "data/tanzania_flood/EUWATCH/inun_dynRout_RP_{}_Tanzania/inun_dynRout_RP_{}_contour_Tanzania.tif".format(return_period, return_period),
            'tmpfile_1': "data/tanzania_flood/EUWATCH_{}_mask-{}.tif".format(return_period, threshold),
            'tmpfile_2': "data/tanzania_flood/EUWATCH_{}_vector_mask-{}.shp".format(return_period, threshold),
            'outfile': "data/tanzania_flood/threshold_{}/EUWATCH_{}_mask-{}.shp".format(threshold, return_period, threshold)
        }

    # GLOFRIS models
    models = ['GFDL-ESM2M', 'HadGEM2-ES', 'IPSL-CM5A-LR', 'MIROC-ESM-CHEM', 'NorESM1-M']

    for model in models:
        for return_period in return_periods:
            print(model, return_period, threshold)
            yield {
                'infile': "data/tanzania_flood/{}/rcp6p0/2030-2069/inun_dynRout_RP_{}_bias_corr_masked_Tanzania/inun_dynRout_RP_{}_bias_corr_contour_Tanzania.tif".format(model, return_period, return_period),
                'tmpfile_1': "data/tanzania_flood/{}_{}_mask-{}.tif".format(model, return_period, threshold),
                'tmpfile_2': "data/tanzania_flood/{}_{}_vector_mask-{}.shp".format(model, return_period, threshold),
                'outfile': "data/tanzania_flood/threshold_{}/{}_{}_mask-{}.shp".format(threshold, model, return_period, threshold)
            }

    # Convert SSBN models
    ssbn_return_periods=['5', '10', '20', '50', '75', '100', '200', '250', '500', '1000']
    ssbnmodels = {
        "TZ_fluvial_undefended": "FU",
        "TZ_pluvial_undefended": "PU"
    }

    for model, abbr in ssbnmodels.items():
        for return_period in ssbn_return_periods:
            print("SSBN", abbr, return_period, threshold)
            yield {
                'infile': "data/tanzania_flood/SSBN_flood_data/{}/TZ-{}-{}-1.tif".format(model, abbr, return_period),
                'tmpfile_1': "data/tanzania_flood/SSBN_{}_{}_mask-{}.tif".format(abbr, return_period, threshold),
                'tmpfile_2': "data/tanzania_flood/SSBN_{}_{}_vector_mask-{}.shp".format(abbr, return_period, threshold),
                'outfile': "data/tanzania_flood/threshold_{}/SSBN_{}_{}_mask-{}.shp".format(threshold, abbr, return_period, threshold)
            }

def convert(threshold, infile, tmpfile_1, tmpfile_2, outfile):
    """Threshold raster, convert to polygons, assign crs
    """
    args = [
        "gdal_calc.py",
        '-A', infile,
        '--outfile={}'.format(tmpfile_1),
        '--calc=logical_and(A>={}, A<999)'.format(threshold),
        '--type=Byte', '--NoDataValue=0',
        '--co=SPARSE_OK=YES',
        '--co=NBITS=1',
        '--quiet'
        # Could enable compression
        # --co="COMPRESS=LZW"
    ]
    subprocess.run(args)

    subprocess.run([
        "gdal_polygonize.py",
        tmpfile_1,
        '-q',
        '-f', 'ESRI Shapefile',
        tmpfile_2
    ])

    subprocess.run([
        "ogr2ogr",
        '-a_srs', 'EPSG:4326',
        outfile,
        tmpfile_2
    ])

    subprocess.run(["rm", tmpfile_1])
    subprocess.run(["rm", tmpfile_2])
    subprocess.run(["rm", tmpfile_2.replace('shp', 'shx')])
    subprocess.run(["rm", tmpfile_2.replace('shp', 'dbf')])
    subprocess.run(["rm", tmpfile_2.replace('shp', 'prj')])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit("Usage: python convert_hazard_to_vector.py <threshold>")
    main(sys.argv[1])
