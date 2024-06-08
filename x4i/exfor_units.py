from x4i import exfor_dicts, DICTPATH
import os
import csv
import pint
import bidict

# This is the NRDC generated dictionary of unit definitions for EXFOR files
exfor_units_dict = exfor_dicts.get_exfor_dict("Data units")  
for obsolete in ["GAM/100N", "GAM/PART", "PART/FIS", "1/INC/KEV", "DEG-K", "PART/MUAHR", "N/PART", "NUC/PART"]: # get rid of obsolete defs
    del(exfor_units_dict[obsolete]) 
    # I did this first:
    #   if exfor_units_dict[ent]['status_code'] == 'OBS':  print(ent)  
del(exfor_units_dict['SEE TEXT'])  # this ain't a unit!

# Set up the mapping between EXFOR units and Pint units
exfor_pint_unit_map = bidict.bidict()  
with open(DICTPATH + os.sep + 'exfor_units.csv', mode='r') as csvfile:
    csvreader = csv.reader(csvfile)
    for irow, row in enumerate(csvreader):
        if irow == 0: 
            continue
        exfor_pint_unit_map[row[0]]=row[-1]

# Set up our unit registry in Pint
exfor_unit_registry = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
exfor_unit_registry.load_definitions(DICTPATH + os.sep + 'exfor-pint-definitions.txt')
exfor_unit_registry.enable_contexts('exfor', 'boltzmann')


