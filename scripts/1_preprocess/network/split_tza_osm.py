"""Split TZA to multiple files
"""
import os
import fiona

def main():
    base_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'data', 'Infrastructure'
    )
    tza_path = os.path.join(
        base_path,
        'Roads', 'osm_mainroads', 'TZA.shp'
    )

    with fiona.open(tza_path) as source:
        written = 0
        filenum = 0
        sink = get_sink(source, tza_path, filenum)
        for feature in source:
            if written == 20000:
                sink.close()
                written = 0
                filenum += 1
                print(filenum)
                sink = get_sink(source, tza_path, filenum)
            sink.write(feature)
            written += 1
        sink.close()

def get_sink(source, tza_path, filenum):
    return fiona.open(
        str(tza_path) + ".{}.shp".format(filenum),
        'w',
        driver=source.driver,
        crs=source.crs,
        schema=source.schema
    )

if __name__ == '__main__':
    main()
