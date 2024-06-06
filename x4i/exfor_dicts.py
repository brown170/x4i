# Copyright (c) 2011, Lawrence Livermore National Security, LLC. Produced at
# the Lawrence Livermore National Laboratory. Written by David A. Brown
# <brown170@llnl.gov>.
#
# LLNL-CODE-484151 All rights reserved.
#
# This file is part of EXFOR Interface (x4i)
#
# Please also read the LICENSE.txt file included in this distribution, under
# "Our Notice and GNU General Public License".
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License (as published by the
# Free Software Foundation) version 2, dated June 1991.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# terms and conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
################################################################################
#
# Changes since LLNL release (x4i-1.0):
#
#   0.     Improve author parsing;
#          Improvee reaction parsing error reporting (David Brown <dbrown@bnl.gov>, 2019-08-16T17:26:18)
#   1.     Undo attempts to update universal newline support flags (David Brown <dbrown@bnl.gov>, 2018-12-05T17:09:40)
#   2.     Close two files that aren't automatically closed in Py3 (David Brown <dbrown@bnl.gov>, 2018-12-05T00:51:14)
#   3.     Switch dictionary metadata to use JSON so I can avoid exec() calls in the dictionary parser (David Brown <dbrown@bnl.gov>, 2018-12-04T20:49:58)
#   4.     Clean up column parser and dicts (David Brown <dbrown@bnl.gov>, 2018-12-04T19:37:40)
#   5.     Clear a few uninitialized variable warnings (David Brown <dbrown@bnl.gov>, 2014-03-04T13:53:51)
#
################################################################################

# module exfor_dicts.py
"""
exfor_dicts module - Class and Methods for Server that gives look-up tables for abbreviations in EXFOR files
"""
from __future__ import print_function, division

import os
import json
from . import __path__


PATHTODICTIONARYFILES = __path__[0] + os.sep + "dicts" + os.sep
ALL_DICTIONARIES=json.load(open(PATHTODICTIONARYFILES + "dict_arc_all.json"))


def get_dict_entry(_dict_key, _dict_entry):
    """
    _dict_key: either int, zfilled string of an int, or the key word itself
    _dict_entry: the entry in the _dict_key's dictionary aought for

    >>> print(dict["236"]["CUM,FY,,FRC"]["expansion"])
    """
    # If it is an int (like thing), turn it into a zfilled index
    _dict_index = None 
    try: 
        _dict_index = str(int(_dict_key)).zfill(3)
        return ALL_DICTIONARIES[_dict_index][_dict_entry]["expansion"]
    except ValueError:
        pass 

    # OK, have to look it up by name
    for key, val in ALL_DICTIONARIES['950'].items():
        if _dict_key == val['dictionary_name']:
            return ALL_DICTIONARIES[key][_dict_entry]["expansion"] 

    raise KeyError("Could not find key %s" % _dict_key)
        


# ---------- getDictionary ----------
def getDictionary(filename, VERBOSELEVEL=0):
    if type(filename) is not str:
        raise TypeError('Variable filename is supposed to be a string, got a ' + str(type(filename)))
    try:
        f = open(filename, mode='r')
    except IOError:
        if VERBOSELEVEL > 0:
            print("Dictionary file " + filename + " not found")
        return None

    flines=f.readlines()

    # Initialize variables
    namespace=json.loads(''.join(flines[0:3]))
    Title = namespace["Title"]
    FieldBreaks = namespace["FieldBreaks"]
    NumFields = namespace["NumFields"]
    if VERBOSELEVEL > 1:
        print("*** " + Title + " ***")
    FieldBreaks.insert(0, 0)

    # rest of file is dictionary
    d = {}
    for line in flines[3:]:
        line = line.strip()
        FieldBreaks.append(len(line))
        if line != "":
            fieldlist = []
            for i in range(NumFields):
                fieldlist.append(line[FieldBreaks[i]:FieldBreaks[i + 1]].strip())
            item = []
            for i in range(1, NumFields):
                item.append(fieldlist[i])
            d[fieldlist[0]] = item
        FieldBreaks.pop()
    f.close()
    return d


# -------------------------------------------
#
# X4DictionaryServer
#
# -------------------------------------------
class X4DictionaryServer:

    # ---------- __init__ ----------
    def __init__(self, pathToDictionaryFiles=PATHTODICTIONARYFILES):
        self.pathToDictionaryFiles = pathToDictionaryFiles
        self.DictionaryNames = (
            (3, "Institutes"),
            (4, "ReferenceTypes"),
            (5, "Journals"),
            (7, "ConferencesAndBooks"),
            (9, "Compounds"), #209
            (15, "History"),
            (16, "Status"),
            (17, "Rel_Ref"),
            (18, "Facility"),
            (19, "IncidentSource"),
            (20, "AdditionalResults"),
            (21, "Method"),
            (22, "Detectors"),
            (23, "Analysis"),
            (24, "DataHeadings"),
            (30, "Process"),
            (33, "Particles"),
            (34, "Modifiers"),
            (35, "DataType"),
            (36, "Quantities"), #113
            (37, "Result"))

    # ---------- __getitem__ ----------
    def __getitem__(self, i):
        """
        Shortcut for getDictionary method
        """
        return self.getDictionary(i)

    # ---------- getDictionaryName ----------
    def getDictionaryName(self, x):
        """
        Look up dictionary name
        @type x: int
        @param x: index of the dictionary
        @rtype: string or None
        @return: name of the dictionary
        """
        if isinstance(x, int):
            for i in self.DictionaryNames:
                if i[0] == x:
                    return i[1]
        return None

    # ---------- getDictionaryIndex ----------
    def getDictionaryIndex(self, x):
        """
        Look up index for dictionary named "x"
        @type x: string
        @param x: name of the dictionary
        @rtype: int or None
        @return: index of the dictionary
        """
        if isinstance(x, str):
            for i in self.DictionaryNames:
                if i[1] == x:
                    return i[0]
        return None

    # ---------- getDictionaryFilename ----------
    def getDictionaryFilename(self, x):
        """
        Figure out file name of requested dictionary
        @type x: string or int
        @param x: name or index of the dictionary
        @rtype: string or None
        @return: filename for the dictionary
        """
        if isinstance(x, int):
            for i in self.DictionaryNames:
                if i[0] == x:
                    return "dict" + repr(i[0]).zfill(2) + ".txt"
        elif isinstance(x, str):
            for i in self.DictionaryNames:
                if i[1] == x:
                    return "dict" + repr(i[0]).zfill(2) + ".txt"
        return None

    # ---------- getDictionary ----------
    def getDictionary(self, x, VERBOSELEVEL=0):
        """
        Retrieve requested dictionary
        @type x: string or int
        @param x: name or index of the dictionary
        @param VERBOSELEVEL: verbosity
        @rtype: matrix
        @return: the dictionary
        """
        #return ALL_DICTIONARIES[str(self.getDictionaryIndex(x)).zfill(3)]
        filename = self.getDictionaryFilename(x)
        return getDictionary(self.pathToDictionaryFiles + filename, VERBOSELEVEL=VERBOSELEVEL)

    # ---------- getAllDictionaries ----------
    def getAllDictionaries(self, VERBOSELEVEL=0):
        """
        Retrieve requested dictionary
        @rtype: map or matrices
        @return: map of dictionaries, key is dictionary name
        """
        if VERBOSELEVEL > 1:
            print('Loading EXFOR Dictionaries:')
        dictmap = {}
        for i in self.DictionaryNames:
            tmp = self.getDictionary(i[0], VERBOSELEVEL=VERBOSELEVEL)
            if tmp is not None:
                dictmap[i[1]] = tmp
        return dictmap
