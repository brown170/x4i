from x4i import exfor_dicts, DICTPATH
import os
import csv
import bidict

exfor_units_dict = exfor_dicts.get_exfor_dict("Data units")
exfor_pint_unit_map = bidict.bidict()

with open(DICTPATH + os.sep + 'exfor_units.csv', mode='r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        exfor_pint_unit_map[row[0]]=row[-1]


