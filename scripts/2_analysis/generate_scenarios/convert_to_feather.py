"""Convert osm_intersections.csv to feather format

Requires pandas and feather-format.
"""
import pandas

def main():
    """Read, convert categorical and integer datatypes to save space, and write.
    """
    df = pandas.read_csv('osm_intersections.csv')

    df['model'] = df.model.astype('category')
    df['osm_highway'] = df.osm_highway.astype('category')
    df['id'] = df.id.astype('int64')
    df['return_period'] = df.id.astype('int32')

    df.to_feather('osm_intersections.ft')

if __name__ == '__main__':
    main()
