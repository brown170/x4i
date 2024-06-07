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
#   0.     Spelling fix: grammar is spelled "grammar" not "grammer" (David Brown <dbrown@bnl.gov>, 2018-12-05T16:41:09)
#   1.     Fix imports for Python3.X (David Brown <dbrown@bnl.gov>, 2018-12-04T18:15:58)
#   2.     Python3.X compatibility & PEP-8 compliance  (David Brown <dbrown@bnl.gov>, 2018-12-04T17:44:23)
#   3.     Tweak test data paths (David Brown <dbrown@bnl.gov>, 2014-09-15T14:19:36)
#   4.     Add unit testing paths (David Brown <dbrown@bnl.gov>, 2014-02-04T17:31:32)
#   5.     Add path to reaction count file (David Brown <dbrown@bnl.gov>, 2013-06-17T16:09:55)
#   6.     PEP-8 compliance; fix global data scope resolution bug (David Brown <dbrown@bnl.gov>, 2013-01-11T16:53:37)
#   7.     Add query() and retrieve() factory functions (not fully implemented though) (David Brown <dbrown@bnl.gov>, 2013-01-10T18:40:19)
#   8.     Add DOI file (David Brown <dbrown@bnl.gov>, 2012-07-24T15:48:33)
#   9.     Fix the paths and move them into the main module __ini__.py and tell exfor_manager about them (David Brown <dbrown@bnl.gov>, 2012-07-24T15:33:16)
#
################################################################################

# General info
import os

MAJOR_VERSION = 1
MINOR_VERSION = 0
PATCH = 0

__package_name__ = "x4i -- The Exfor Interface"
__version__ = '.'.join(map(str, [MAJOR_VERSION, MINOR_VERSION, PATCH]))
__author__ = 'David Brown <brown170@llnl.gov>'
__url__ = 'http://nuclear.llnl.gov/'
__license__ = 'not assigned yet'
__disclaimer__ = """LLNL Disclaimer:
      This work was prepared as an account of work sponsored by an agency of the
      United States Government. Neither the United States Government nor the
      University of California nor any of their employees, makes any warranty,
      express or implied, or assumes any liability or responsibility for the
      accuracy, completeness, or usefulness of any information, apparatus, product,
      or process disclosed, or represents that its use would not infringe
      privately-owned rights.  Reference herein to any specific commercial products,
      process, or service by trade name, trademark, manufacturer or otherwise does
      not necessarily constitute or imply its endorsement, recommendation, or
      favoring by the United States Government or the University of California. The
      views and opinions of authors expressed herein do not necessarily state or
      reflect those of the United States Government or the University of California,
      and shall not be used for advertising or product endorsement purposes."""

from x4i.exfor_paths import *
from x4i.exfor_dicts import get_exfor_dict, get_exfor_dict_entry
from x4i import exfor_manager, exfor_entry

__databaseManager = exfor_manager.X4DBManagerDefault()


def query(**kw): return __databaseManager.query(**kw)


def raw_retrieve(**kw):
    return __databaseManager.retrieve(**kw)


def retrieve(**kw):
    rr = {}
    r = __databaseManager.retrieve(**kw)
    for k, v in r.items():
        rr[k] = exfor_entry.X4Entry(v)
    return rr


__all__ = [
    '__init__', 'exfor_dataset', 'exfor_exceptions', 'exfor_manager', 'exfor_reference', 'exfor_utilities',
    'endl_Z', 'exfor_dicts', 'exfor_field', 'exfor_particle', 'exfor_section', 'pyparsing',
    'exfor_column_parsing', 'exfor_entry', 'exfor_grammars', 'exfor_reactions', 'exfor_subentry']
