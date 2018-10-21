import csv
import gzip
import operator
import os
import pickle

import shapefile

base_path = os.path.split(os.path.realpath(__file__))[0]

gccsas = {
    '1GSYD': 'sydney',
    '2GMEL': 'melbourne',
    '3GBRI': 'brisbane',
    '4GADE': 'adelaide',
    '5GPER': 'perth',
    '6GHOB': 'hobart',
    '8ACTE': 'canberra',
}

# SA2
shpfile = shapefile.Reader(os.path.join(base_path, 'shapefile', 'SA2_2016_AUST'))
csvfile = open(os.path.join(base_path, 'shapefile', 'SA2_2016_AUST.csv'), 'r')

shapes = shpfile.shapes()
csv_reader = csv.DictReader(csvfile)
outputs = {city: {} for city in gccsas.values()}

for info, shape in zip(csv_reader, shapes):
    sa2_code = info['SA2_MAINCODE_2016']
    sa2_name = info['SA2_NAME_2016']
    gccsa_code = info['GCCSA_CODE_2016']

    if gccsa_code not in gccsas.keys():
        continue
    else:
        city = gccsas[gccsa_code]

    points = shape.points
    if not points:
        continue
    else:
        lng = sum(map(operator.itemgetter(0), points)) / len(points)
        lat = sum(map(operator.itemgetter(1), points)) / len(points)

    outputs[city][sa2_code] = {'sa2_name': sa2_name, 'lng': lng, 'lat': lat, 'points': points}

for city, data in outputs.items():
    pickle.dump(data, gzip.open(os.path.join(base_path, '%s-sa2.pkl.gz' % city), 'wb'))

# SA1
shpfile = shapefile.Reader(os.path.join(base_path, 'shapefile', 'SA1_2016_AUST'))
csvfile = open(os.path.join(base_path, 'shapefile', 'SA1_2016_AUST.csv'), 'r')

shapes = shpfile.shapes()
csv_reader = csv.DictReader(csvfile)
outputs = {city: {} for city in gccsas.values()}

for info, shape in zip(csv_reader, shapes):
    sa1_code = info['SA1_MAINCODE_2016']
    gccsa_code = info['GCCSA_CODE_2016']

    if gccsa_code not in gccsas.keys():
        continue
    else:
        city = gccsas[gccsa_code]

    points = shape.points
    if not points:
        continue
    else:
        lng = sum(map(operator.itemgetter(0), points)) / len(points)
        lat = sum(map(operator.itemgetter(1), points)) / len(points)

    outputs[city][sa1_code] = {'lng': lng, 'lat': lat, 'points': points}

for city, data in outputs.items():
    pickle.dump(data, gzip.open(os.path.join(base_path, '%s-sa1.pkl.gz' % city), 'wb'))
