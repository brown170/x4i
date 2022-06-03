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
#   0.     Python3.X porting issue: {}.keys() returns view, not list (David Brown <dbrown@bnl.gov>, 2018-12-04T22:02:30)
#   1.     Fixing imports (David Brown <dbrown@bnl.gov>, 2018-12-04T21:09:44)
#   2.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T17:44:23)
#   3.     Streamlining X4Entry initialization, hopefully also squashing bugs along the way (David Brown <dbrown@bnl.gov>, 2013-06-19T12:02:54)
#   4.     Add X4MonitorField & add blank line between member functions for clarity (David Brown <dbrown@bnl.gov>, 2013-01-08T19:31:15)
#
################################################################################

# module exfor_subentry.py
"""
exfor_subentry module -
"""
from __future__ import print_function, division

import x4i.exfor_section as exfor_section


def extractX4SubEntryIndex(subentry):
    """
    Grabs the subentry number from the "SUBENT" line of an EXFOR subentry
    @type  subentry: list of strings
    @param subentry: list of string containing the EXFOR subentry
    @rtype:  string or None
    @return: the subentry index as specified by EXFOR
    """
    for line in subentry:
        sline = line.strip().split()
        if sline != [] and sline[0] == "SUBENT":
            return line[14:22]
    return None


def extractX4SectionType(section):
    """
    Extracts the type of EXFOR section from the token in cols[0:10] from the first line that has non-white space there
    @type  section: list of strings
    @param section: list of strings to look to find a valid tag
    @rtype: string or None
    @return: string containing the section type.  Is one of 'BIB', 'DATA' or 'COMMON'
    """
    for line in section:
        tag = line[0:10].strip()
        if tag in ('BIB', 'DATA', 'COMMON'):
            return tag
    return None


class X4SubEntry(dict):
    """
    Exfor SubEntry, composed of X4Sections (X4BibSections and X4DataSections)
    """

    def __init__(self, unprocessed_subentry):
        dict.__init__(self)
        if not isinstance(unprocessed_subentry, list):
            unprocessed_subentry = unprocessed_subentry.split('\n')
        self.accnum = extractX4SubEntryIndex(unprocessed_subentry)
        for section in self.chunkify(unprocessed_subentry):
            tag = extractX4SectionType(section)
            if tag == 'BIB':
                self[tag] = exfor_section.X4BibSection(section)
            elif tag in ('DATA', 'COMMON'):
                self[tag] = exfor_section.X4DataSection(tag, section)
            else:
                raise KeyError(tag + " is not a valid EXFOR Section name")
        self.hascommon = 'COMMON' in self and self['COMMON'] is not None
        self.sorted_keys = list(self.keys())
        self.sorted_keys.sort()

    def __repr__(self):
        """A string representation that should match what comes from IAEA and should be suitable for parsing with x4i"""
        ans = 'SUBENT'.ljust(11) + self.accnum.ljust(11) + '\n'
        for i in self.sorted_keys:
            ans += repr(self[i]) + '\n'
        ans += 'ENDSUBENT'.ljust(11)
        return ans

    def __str__(self):
        """
        Possibly prettier version of the string representation that should match what comes from IAEA
        and should be suitable for parsing with x4i
        """
        ans = 'SUBENT'.ljust(11) + self.accnum.ljust(11) + '\n'
        for i in self.sorted_keys:
            ans += str(self[i]) + '\n'
        ans += 'ENDSUBENT'.ljust(11)
        return ans

    def chunkify(self, oldsubentry):
        """
        Takes a list of strings, assumed to be an EXFOR subentry and returns a list of subsections
        @type  oldsubentry: list of strings
        @param oldsubentry: EXFOR SubEntry to be chopped into subsections
        @rtype: list of list of strings
        @return: list of list of strings w/ innermost list of strings assumed to be Exfor subsections
        """
        if isinstance(oldsubentry, str):
            oldsubentry = oldsubentry.split('\n')
        subentry = []
        inSection = False
        section = []
        for line in oldsubentry:
            if inSection:
                section.append(line)
                if line[0:11][0:3] == 'END':
                    subentry.append(section)
                    inSection = False
            else:
                if line[0:11].strip() in ('BIB', 'DATA', 'COMMON'):
                    inSection = True
                    section = [line]
        return subentry
