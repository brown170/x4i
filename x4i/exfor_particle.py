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
#   0.     Use GNDS isotope/isomer/element styles, not obsolete GND style;
#          Add deprecations (David Brown <dbrown@bnl.gov>, 2021-04-01T08:45:13)
#   1.     Fix bug in handling of fake Z,A for variable particles during initialization (David Brown <dbrown@bnl.gov>, 2019-08-14T18:59:21)
#   2.     Spelling: grammar is spelled "grammar" not "grammer" (David Brown <dbrown@bnl.gov>, 2018-12-05T16:41:09)
#   3.     Change map usage (David Brown <dbrown@bnl.gov>, 2018-12-05T01:21:42)
#   4.     Fix pyparsing import (David Brown <dbrown@bnl.gov>, 2018-12-04T22:15:06)
#   5.     Fix imports (David Brown <dbrown@bnl.gov>, 2018-12-04T21:09:44)
#   6.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T17:44:23)
#   7.     Uncommitted tweaks to paper;
#          An exfor data set now can parse RI correctly;
#          GND particle names as option (David Brown <dbrown@bnl.gov>, 2016-06-29T18:34:25)
#   8.     Fix harmless repr() bug in chemical compounds (David Brown <dbrown@bnl.gov>, 2013-07-01T15:20:19)
#   9.     Correct parsing of monitors to properly distinguish between multiple monitors and those with associated column headings in DATA section (David Brown <dbrown@bnl.gov>, 2013-01-11T18:58:32)
#   10.    Fix antiproton & prompt neutrons;
#          Rebuild indices (David Brown <dbrown@bnl.gov>, 2012-01-04T14:20:40)
#   11.    Handle variable particles better (David Brown <dbrown@bnl.gov>, 2012-01-03T19:59:53)
#   12.    Handle some exotic products/residuals (David Brown <dbrown@bnl.gov>, 2012-01-03T18:57:34)
#
################################################################################

# !/usr/bin/python
# module parse_exfor_particle.py
"""
parse_exfor_particle. module - Classes and Methods to process Exfor Particle and Nucleus strings
"""
from __future__ import print_function, division

__version__ = "0.0.1"
__author__ = "David Brown <brown170@llnl.gov>"

from .exfor_exceptions import *
from .exfor_grammars import *
from .exfor_dicts import *
import pyparsing

# ------------------------------------------------------
# Global data
# ------------------------------------------------------
x4ZMap = {'0': 0, 'G': 0, 'AR': 0, 'N': 0, 'P': 1, 'AP': -1, 'AN': 0, 'H': 1, 'D': 1, 'T': 1, 'A': 2, 'HE3': 2,
          'HE2': 2, 'PI': 0, 'PI0': 0, 'P0': 0, 'PIP': +1, 'ETA': 0, 'PIN': -1, 'KP': +1, 'KN': -1, 'E': -1, 'B': -1,
          'B+': +1, 'B-': -1, 'XR': 0}
x4AMap = {'0': 0, 'G': 0, 'AR': 0, 'N': 1, 'P': 1, 'AP': -1, 'AN': -1, 'H': 1, 'D': 2, 'T': 3, 'A': 4, 'HE3': 3,
          'HE2': 2, 'PI': 0, 'PI0': 0, 'P0': 0, 'PIP': 0, 'ETA': 0, 'PIN': 0, 'KP': 0, 'KN': 0, 'E': 0, 'B': 0, 'B+': 0,
          'B-': 0, 'XR': 0}
x4Chemicals = {'OXI': 'Oxide', 'CMP': 'Compound', 'WTR': 'Water', 'D2O': 'Deuterated_Water'}
x4Hadrons = {'N': 'n', 'P': 'p', 'AP': 'anti-p', 'AN': 'anti-n', 'PI0': "pi0", 'P0': "pi0", 'PIP': "pi+", 'PIN': "pi-",
             'KP': "K+", 'KN': "K-", 'ETA': 'eta'}
x4VariableParticles = {"PI": "any pion", "PN": 'prompt n', "AR": "annih. rad.", "DG": "decay g",
                       "DN": "delayed n", "ER": "???", 'LCP': 'light charged particle', 'FF': "fiss. frag.",
                       'LF': 'light frag.', 'HF': 'heavy frag.',
                       'EC': 'e capture', 'ICE': 'internal conversion e', 'K': "any K",
                       'XR': 'X-rays', 'SF': 'spont. fiss. frag.', 'HCP': "heavy charged particle", 'RSD': "res. nuc."}


class X4ParticleBase:
    """Base class for all particle types"""

    def __init__(self, x):
        if isinstance(x, str):
            x = self.parse(x)
        if not isinstance(x, pyparsing.ParseResults):
            raise TypeError(
                "__init__ takes pyparsing.ParseResults as argument, got " + str(type(x)) + ":" + str(x))
        self.parse_results = x
        self.num = 1
        self.Z = None
        self.sym = None
        self.A = None

    def parse(self, x):
        raise NotImplementedError("Override this function in derived classes")

    def getZ(self):
        if self.num == 'X':
            return int(self.Z)
        return self.num * int(self.Z)

    def getA(self):
        if self.num == 'X':
            return int(self.A)
        return self.num * int(self.A)

    def asList(self):
        if isinstance(self.parse_results, list):
            l = self.parse_results
        else:
            l = self.parse_results.asList()
        return [x.upper() for x in l]

    def __str__(self):
        """Pretty string for print statements"""
        return self.prettyStyle()

    def __repr__(self):
        """Not so pretty form for real work"""
        return self.exforStyle()

    def endlZAStyle(self):
        return None

    def exforStyle(self):
        return None

    def gndStyle(self):
        print(PendingDeprecationWarning("Use gndsStyle()"))
        return None

    def gndsStyle(self):
        return None

    def prettyStyle(self):
        return None


class X4Particle(X4ParticleBase):
    """Parsed particle string (can actually be several real particles)"""

    def __init__(self, x):
        if x == '0':  # spontaneous process, must catch it somehow
            self.num = 0
            self.sym = '0'
            self.Z = 0
            self.A = 0
        else:
            if type(x) == str:
                x = x.upper()
                X4ParticleBase.__init__(self, x)
                x = self.parse_results.asList()
            elif isinstance(x, pyparsing.ParseResults):
                X4ParticleBase.__init__(self, 'N')
                self.parse_results = x
                x = [y.lower() for y in x.asList()]
            else:
                raise TypeError(str(type(x)) + ' is not a valid type for X4particle.__init__, x = ' + str(x))
            if len(x) > 1:
                self.num = int(x[0])
                self.sym = x[1]
            else:
                if x[0][0] == 'X':
                    self.num = 'X'
                    self.sym = x[0][1:]
                else:
                    self.num = 1
                    self.sym = x[0]
            self.Z = x4ZMap.get(self.sym.upper(), None)
            self.A = x4AMap.get(self.sym.upper(), None)

    def parse(self, x):
        try:
            return x4particle.parseString(x)
        except pyparsing.ParseException as err:
            raise ParticleParsingError('Can not parse particle "' + x + '",\n    got error "' + str(err) + '"\n   ')

    def prettyStyle(self):
        if self.num > 1:
            ans = str(self.num)
        else:
            ans = ''
        if self.sym in x4Hadrons:
            return x4Hadrons[self.sym]
        if len(self.sym) == 1:
            if self.sym == 'A':
                ans += 'alpha'
            elif self.sym == 'G':
                ans += 'gamma'
            elif self.sym == '0':
                ans += 'None'
            elif self.sym[0] == 'B':
                ans += 'beta' + self.sym[1:]
            else:
                ans += self.sym.lower()
        else:
            ans += self.sym.capitalize()
        return ans

    def exforStyle(self):
        if self.num > 1:
            return str(self.num) + self.sym
        else:
            return self.sym


class X4Nucleus(X4ParticleBase):
    """Parsed EXFOR nucleus"""

    def __init__(self, x):
        if type(x) == list:
            self.num = 1
            self.parse_results = x
        else:
            X4ParticleBase.__init__(self, x)
            self.num = 1
            x = self.parse_results.asList()
        self.Z = x[0]
        self.sym = x[1].capitalize()
        self.A = x[2]

    def parse(self, x):
        try:
            return x4nucleus.parseString(x)
        except pyparsing.ParseException as err:
            raise ParticleParsingError('Can not parse nucleus "' + x + '",\n    got error "' + str(err) + '"\n   ')

    def endlZAStyle(self):
        return 'za' + self.Z.zfill(3) + self.A.zfill(3)

    def exforStyle(self):
        if self.sym == 'Nn':
            return 'n'
        return self.Z + '-' + self.sym.upper() + '-' + self.A

    def gndStyle(self):
        print(PendingDeprecationWarning("Use gndsStyle()"))
        if self.sym == 'Nn':
            return 'n'
        return self.sym.capitalize() + self.A

    def gndsStyle(self):
        if self.sym == 'Nn':
            return 'n'
        if self.A == 0:
            return self.sym.capitalize()
        return self.sym.capitalize() + self.A

    def prettyStyle(self):
        if self.sym == 'Nn':
            return 'n'
        return self.A + self.sym


class X4Isomer(X4Nucleus):
    """Parsed Exfor nucleus with list of isomers"""

    def __init__(self, x, IgnoreIsomerMath=False):
        if type(x) == list:
            self.num = 1
            self.parse_results = x
        else:
            X4Nucleus.__init__(self, x)
            x = self.parse_results.asList()
        self.isomers = []
        for i in range(4, len(x)):
            if x[i].lower() == 'g':
                self.isomers.append('0')
            elif x[i].lower() == 'm' and len(x) > i + 1:
                pass
            elif x[i].isdigit():
                self.isomers.append(x[i])
            elif x[i].lower() == 't':
                pass
            else:
                self.isomers.append('1')
            if (('G' in x[4:] or 'T' in x[4:]) and 'M' in x[4:]) or x[4:].count('M') > 1:
                if not IgnoreIsomerMath:
                    raise IsomerMathParsingError(
                        "Math with multiple states in isomer element, who thought of that format?  Found: " + str(x))
                else:
                    self.isomers += ''.join(x[4:])

    def endlZAStyle(self):
        za = X4Nucleus.endlZAStyle(self)
        if len(self.isomers) == 1 and self.isomers[0] == '1':
            return za + 'm'
        for i in self.isomers:
            if i == '0':
                za += 'g'
            else:
                za += 'm' + i
        return za

    def exforStyle(self):
        za = X4Nucleus.exforStyle(self)
        if len(self.isomers) == 1 and self.isomers[0] == '1':
            return za + '-M'
        return za + '-M' + '+M'.join(self.isomers)

    def gndStyle(self):
        print(PendingDeprecationWarning("Use gndsStyle()"))
        if self.sym == 'Nn':
            return 'n'
        if len(self.isomers) == 1 and self.isomers[0] == '1':
            return self.sym.capitalize() + self.A + 'm'
        else:
            return self.sym.capitalize() + self.A + 'm' + ','.join(self.isomers)

    def gndsStyle(self):
        if self.sym == 'Nn':
            return 'n'
        if len(self.isomers) == 1 and self.isomers[0] == '1':
            return self.sym.capitalize() + self.A + '_m1'
        else:
            return self.sym.capitalize() + self.A + '_m' + ','.join(self.isomers)

    def prettyStyle(self):
        if len(self.isomers) == 1 and self.isomers[0] == '1':
            return self.A + 'm' + self.sym
        else:
            return self.A + 'm' + ','.join(self.isomers) + self.sym


class X4Element(X4Nucleus):
    """Parsed EXFOR nucleus with nonsense A because is really a natural element"""

    def getA(self):
        return -3000

    def prettyStyle(self):
        return 'nat' + self.sym

    def gndsStyle(self):
        return self.sym


class X4VariableParticle(X4Particle):
    """Particle with nonsense Z & A when the Z & A are possibly or actually variable"""

    def __init__(self, x):
        X4Particle.__init__(self, x)
        self.parse_results = x
        self.num = 1
        self.Z = -3000
        self.sym = self.parse_results
        self.A = -3000

    def getZ(self):
        if self.Z > 0:
            return self.Z
        return -3000

    def getA(self):
        return -3000


class X4ChemicalCompound(X4ParticleBase):
    """Chemical compound, essentially a variable particle with complicated symbol"""

    def __init__(self, x):
        X4ParticleBase.__init__(self, x)
        x = self.parse_results[0].split('-')
        self.num = 1
        self.sym = x[1]
        self.Z = int(x[0])
        self.A = 0

    def parse(self, x):
        try:
            return x4chemical_compound.parseString(x)
        except pyparsing.ParseException as err:
            raise ParticleParsingError(
                'Can not parse chemical compound "' + x + '",\n    got error "' + str(err) + '"\n   ')

    def getA(self):
        return -3000

    def asList(self):
        return [x.upper() for x in self.parse_results]

    def endlZAStyle(self):
        raise NotImplementedError("ENDL doesn't do chemical compounds")

    def exforStyle(self):
        return str(self.parse_results[0])

    def prettyStyle(self):
        return X4DictionaryServer()["Compounds"][str(self.parse_results[0])][0]
