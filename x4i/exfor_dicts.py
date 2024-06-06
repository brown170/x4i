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


def get_dict(_dict_key):
    """
    _dict_key: either int, zfilled string of an int, or the key word itself

    >>> print(dict["236"]["CUM,FY,,FRC"]["expansion"])
    """
    # If it is an int (like thing), turn it into a zfilled index
    _dict_index = None 
    try: 
        _dict_index = str(int(_dict_key)).zfill(3)
        return ALL_DICTIONARIES[_dict_index]
    except ValueError:
        pass 

    # OK, have to look it up by name
    for key, val in ALL_DICTIONARIES['950'].items():
        if _dict_key == val['dictionary_name']:
            return ALL_DICTIONARIES[key]

    raise KeyError("Could not find key %s" % _dict_key)
  

def get_dict_entry(_dict_key, _dict_entry):
    """
    _dict_key: either int, zfilled string of an int, or the key word itself
    _dict_entry: the entry in the _dict_key's dictionary aought for

    >>> print(dict["236"]["CUM,FY,,FRC"]["expansion"])
    """
    return get_dict(_dict_key)[_dict_entry]

    # If it is an int (like thing), turn it into a zfilled index
    _dict_index = None 
    try: 
        _dict_index = str(int(_dict_key)).zfill(3)
        return ALL_DICTIONARIES[_dict_index][_dict_entry]
    except ValueError:
        pass 

    # OK, have to look it up by name
    for key, val in ALL_DICTIONARIES['950'].items():
        if _dict_key == val['dictionary_name']:
            return ALL_DICTIONARIES[key][_dict_entry] 

    raise KeyError("Could not find key %s" % _dict_key)
