"""Download and filter airport data
"""
import csv
import os

import requests

OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    'data',
    'Airport_data',
    'tanzania_airports.csv'
)
DATA_URL = 'http://ourairports.com/data/airports.csv'
COUNTRY_CODE = 'TZ'
HEADER = (
    'id',
    'ident',
    'type',
    'name',
    'latitude_deg',
    'longitude_deg',
    'elevation_ft',
    'continent',
    'iso_country',
    'iso_region',
    'municipality',
    'scheduled_service',
    'gps_code',
    'iata_code',
    'local_code',
    'home_link',
    'wikipedia_link',
    'keywords',
)

R = requests.get(DATA_URL)
DATA = R.text.split("\n")

with open(OUTPUT_FILE, 'w', newline="") as output_fh:
    READER = csv.DictReader(DATA)
    WRITER = csv.DictWriter(output_fh, fieldnames=HEADER)
    WRITER.writeheader()
    for line in READER:
        if line['iso_country'] == COUNTRY_CODE and \
           line['scheduled_service'] == 'yes':
            WRITER.writerow(line)
