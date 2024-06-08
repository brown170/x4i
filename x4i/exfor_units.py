from x4i import exfor_dicts, DICTPATH
import os
import csv
import pint
import bidict

exfor_units_dict = exfor_dicts.get_exfor_dict("Data units")  # This is the NRDC generated dictionary of unit definitions for EXFOR files
del(exfor_units_dict['SEE TEXT'])  # this ain't a unit!
exfor_pint_unit_map = bidict.bidict()  # mapping between EXFOR units and Pint units
exfor_unit_registry = pint.UnitRegistry()
exfor_unit_registry.load_definitions(DICTPATH + os.sep + 'exfor-pint-definitions.txt')  # our unit registry in Pint

with open(DICTPATH + os.sep + 'exfor_units.csv', mode='r') as csvfile:
    csvreader = csv.reader(csvfile)
    for irow, row in enumerate(csvreader):
        if irow == 0: 
            continue
        exfor_pint_unit_map[row[0]]=row[-1]


