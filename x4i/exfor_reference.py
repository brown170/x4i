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
#   0.     Fix goofed up import (David Alan Brown <dbrown@bnl.gov>, 2021-08-30T19:16:40)
#   1.     Spelling: grammar is spelled "grammar" not "grammer" (David Brown <dbrown@bnl.gov>, 2018-12-05T16:41:09)
#   2.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T17:44:23)
#   3.     Correct parsing of monitors to properly distinguish between multiple monitors and those with
#          associated column headings in DATA section (David Brown <dbrown@bnl.gov>, 2013-01-11T18:58:32)
#
################################################################################
 
from __future__ import print_function, division

from .exfor_utilities import *
from .exfor_grammars import *
from .exfor_exceptions import ReferenceParsingError
import pyparsing


def parseX4Year(date):
    """
    Parses year string in the 50 or so variations in the Exfor data
    @type  date: string
    @param date: String containing the potential date
    @rtype:      string
    @return:     4-digit representation of the year
    """
    if ')' in date:
        date = date.replace(')', '')  # helps when grammar gets confused. I should really fix the grammar though
    if not date.isdigit():
        raise TypeError("date should only have ints inside, found: " + date)
    if type(date) != str:
        raise TypeError("parseYear takes a string as an argument")
    year = date
    # if date format is e.g. 198411, meaning Nov. 1984, use this
    if len(year) == 6:
        year = year[: -2]
    # if date format is e.g. 19840211, meaning 2 Nov. 1984, use this
    if len(year) == 8:
        year = year[: -4]
    # if date format has 4 digits, either it is a year (e.g. 1984) or year+month (8411)
    if len(year) == 4:
        if year[: 2] == "19" or year[: 2] == "20":
            return year
        else:
            year = year[: 2]
    # if date format has 2 digits, it better be a year or we're screwed
    if len(year) == 2:
        if int(year) > 10:
            return '19' + year
        else:
            return '20' + year
    return year


class X4ReferenceCode:

    def __init__(self, x):
        if not str:
            raise TypeError("X4ReferenceCode.__init__ takes a string as an argument")
        try:
            self.refcode = pyparsing.common.comma_separated_list.parseString(x).asList()
        except pyparsing.ParseException as err:
            raise ReferenceParsingError(
                'Can not parse reference code "' + x + '",\n    got error "' + str(err) + '"\n   ')
        self.reftype = self.refcode[0]
        self.name = self.refcode[1]
        self.details = self.refcode[2:-1]
        self.date = self.refcode[-1]
        try:
            self.pubyear = parseX4Year(self.date)
        except TypeError as err:
            raise ReferenceParsingError(str(err) + ' in date ' + self.date)
        self.ugly_name = self.reftype + ',' + self.name
        try:
            self.pretty_name = self.getRefName()
        except KeyError:
            self.pretty_name = self.ugly_name

    def getRefName(self):
        if self.reftype in ['A', 'B', 'C']:
            return get_exfor_dict_entry('Conferences', self.name)['expansion'] + ' '
        elif self.reftype in ['J', 'K']:
            return get_exfor_dict_entry('Journals', self.name)['expansion'] + ' '
        elif self.reftype in ['P', 'R', 'S']:
            return get_exfor_dict_entry('Reference types', self.reftype)['expansion'] + ': ' + self.name + ' '
        elif self.reftype in ['T', 'W', 'X']:
            return get_exfor_dict_entry('Reference types', self.reftype)['expansion'] + ': ' + self.name.capitalize() + ' '
        elif self.reftype in ['0', '3', '4']:
            return get_exfor_dict_entry('Reference types', self.reftype)['expansion'] + ': ' + self.name.capitalize() + ' '
        else:
            raise LookupError("X4ReferenceCode.__str__: can't find type of reference for '" + self.reftype + "'")
        return None

    def __repr__(self):
        return self.ugly_name + ',' + ','.join([x.strip() for x in self.details]) + ',' + self.date

    def __str__(self):
        return self.pretty_name + ', '.join([x.strip() for x in self.details]) + ' (' + self.pubyear + ')'
