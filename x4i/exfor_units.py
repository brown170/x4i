from x4i import exfor_dicts, DICTPATH
import os
import csv
import pint
import bidict

exfor_units_dict = exfor_dicts.get_exfor_dict("Data units")
exfor_pint_unit_map = bidict.bidict()
exfor_unit_registry = pint.UnitRegistry()

with open(DICTPATH + os.sep + 'exfor_units.csv', mode='r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        exfor_pint_unit_map[row[0]]=row[-1]

