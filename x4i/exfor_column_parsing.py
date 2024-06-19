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
#   0.     get rid of more bad-behaving map() functions (David Brown <dbrown@bnl.gov>, 2018-12-05T17:55:16)
#   1.     py3 porting issue: {}.keys() returns view, not list (David Brown <dbrown@bnl.gov>, 2018-12-04T22:02:30)
#   2.     clean up column parser and dicts (David Brown <dbrown@bnl.gov>, 2018-12-04T19:37:40)
#   3.     get rid of obsolete line continuation charactors (David Brown <dbrown@bnl.gov>, 2017-12-21T16:22:47)
#   4.     tweaks to column parsing to attempt to workaround momentum and temperature data
#          (The whole column parsing architecture needs to be redone, probably with PQU's help) (David Brown <dbrown@bnl.gov>, 2014-03-04T16:44:43)
#
################################################################################

from __future__ import print_function, division

import math
from functools import reduce

baseIncidentEnergyKeys = ['EN']
baseOutgoingEnergyKeys = ['E']
baseMomKeys = ['MOM']
baseTempKeys = ['KT']
baseMonitorKeys = ['MONIT']
baseDataKeys = ['DATA', 'RATIO']
baseMiscKeys = ['MISC']
baseAngleKeys = ['COS', 'ANG']

resolutionFWSuffix = ['-RES', '-RSL', '-RSL-FW']
resolutionHWSuffix = ['-RSL-HW']

errorSuffix = ['-ERR']
variableSuffix = ['', '-DUMMY', '-ASSUM', '-MEAN', '-APRX']
frameSuffix = ['-CM']
minSuffix = ['-MIN']
maxSuffix = ['-MAX']
plusPrefix = ['+']
minusPrefix = ['-']
shiftSuffix = ['-K']

dataTotalErrorKeys = ['ERR-T']
dataSystematicErrorKeys = ['ERR']
dataStatisticalErrorKeys = ['ERR-S']

def absOrNone(x):
    if isinstance(x, str):
        return x
    try:
        ans = abs(x)
    except TypeError:
        ans = None
    return ans


def averageColumns(x, y):
    ans = []
    for i in range(max(len(x), len(y))):
        if x[i] is not None:
            if y[i] is None:
                ans.append(x[i])
            else:
                ans.append(0.5 * (x[i] + y[i]))
        else:
            if y[i] is None:
                ans.append(None)
            else:
                ans.append(y[i])
    return ans


def condenseColumn(x, y):
    ans = []
    for i in range(max(len(x), len(y))):
        if x[i] is not None:
            ans.append(x[i])
        else:
            ans.append(y[i])
    return ans


class X4ColumnParser:
    def __init__(self, match_labels=None):
        self.match_labels = match_labels

    def isMatch(self, i, data):
        result = True
        if (i < 0) or (i >= data.numcols()):
            return False
        if self.match_labels is not None:
            result = result and (data.labels[i] in self.match_labels)
        if self.match_units is not None:
            result = result and (data.units[i] in self.match_units)
        return result

    def firstMatch(self, data):
        for i in range(data.numcols()):
            if self.isMatch(i, data):
                return i
        return -1

    def allMatches(self, data):
        match_list = []
        for i in range(data.numcols()):
            if self.isMatch(i, data):
                match_list.append(i)
        return match_list

    def getColumn(self, icol, data):
        if not self.isMatch(icol, data):
            return [None] * (data.numrows() + 2)
        units = self.getConversion(data.units[icol])
        col = [data.labels[icol], units[1]]
        for irow in range(data.numrows()):
            col.append(data.data[irow][icol])
            if col[-1] is not None:
                col[-1] = col[-1] * units[0] * self.scale_factor + self.off_set
        return col


class X4AngleColumnParser(X4ColumnParser):
    def getColumn(self, icol, data):
        # If in either radians or degrees, can handle using base class
        if 'COS' not in data.labels[icol]:
            return X4ColumnParser.getColumn(self, icol, data)
        # Otherwise must undo angular cosine
        if not self.isMatch(icol, data):
            return [None] * (data.numrows() + 2)
        units = self.getConversion('RAD')
        col = [data.labels[icol], units[1]]
        for irow in range(data.numrows()):
            col.append(data.data[irow][icol])
            if col[-1] is not None:
                col[-1] = math.acos(col[-1] * self.scale_factor + self.off_set) * units[0]
        return col


class X4ColumnPairParser:
    """
    Simple Base class.  Defines init function, but you must override
    the member functions if you expect anything to work
    """

    def __init__(self, column1Parser, column2Parser):
        self.column1Parser = column1Parser
        self.column2Parser = column2Parser
        self.icol1 = - 1
        self.icol2 = - 1

    def set_icols(self, data):
        pass

    def isMatch(self, data):
        return True

    def getValue(self, data):
        return None

    def getError(self, data):
        return None

    def getDummyColumn(self, data):
        return [None] * (data.numrows() + 2)


class X4MissingErrorColumnPair(X4ColumnPairParser):
    """
    Matches first occurrence of Column 1 (that matches your pointer, if any), ignores Column 2.
    """
    def __init__(self, column1Parser, column2Parser=None):
        X4ColumnPairParser.__init__(self, column1Parser, column2Parser)

    def set_icols(self, data):
        self.icol1 = self.column1Parser.firstMatch(data)

    def isMatch(self, data):
        self.set_icols(data)
        return self.icol1 >= 0

    def getValue(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        return self.column1Parser.getColumn(self.icol1, data)

    def getError(self, data):
        return self.getDummyColumn(data)


class X4IndependentColumnPair(X4MissingErrorColumnPair):
    """
    Matches first occurrences of Column 1 and 2 (that matches your pointer, if any)
    """

    def set_icols(self, data):
        self.icol1 = self.column1Parser.firstMatch(data)
        self.icol2 = self.column2Parser.firstMatch(data)

    def isMatch(self, data):
        self.set_icols(data)
        return (self.icol1 >= 0) and (self.icol2 >= 0)

    def getError(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        err = self.column2Parser.getColumn(self.icol2, data)
        if err[1] == 'PER-CENT':
            col = self.getValue(data)
            err[1] = col[1]
            for i in range(2, len(col)):
                if col[i] is not None and err[i] is not None:
                    err[i] = col[i] * err[i] / 100.0
                else:
                    err[i] = None
        return [absOrNone(x) for x in err]


class X4ConstantPercentColumnPair(X4MissingErrorColumnPair):
    """
    Matches first occurance of Column 1, ignores Column 2.
    Set percentError to something other than 10% for real work!
    """

    def __init__(self, column1Parser):
        X4MissingErrorColumnPair.__init__(self, column1Parser, None)
        self.percentError = 10

    def getError(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        col = self.getValue(data)
        for i in range(2, len(col)):
            if col[i] is not None:
                col[i] = col[i] * self.percentError / 100.0
        return [absOrNone(x) for x in col]


class X4HighLowColumnPair(X4IndependentColumnPair):
    def isMatch(self, data):
        self.set_icols(data)
        return self.icol1 >= 0 or self.icol2 >= 0

    def getValue(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        if self.column1Parser is not None:
            col1 = self.column1Parser.getColumn(self.icol1, data)
        else:
            col1 = self.getDummyColumn(data)
        if self.column2Parser is not None:
            col2 = self.column2Parser.getColumn(self.icol2, data)
        else:
            col2 = self.getDummyColumn(data)
        ans = [None, None]
        for i in [0, 1]:
            for j in [col1[i], col2[i]]:
                if j is not None:
                    ans[i] = j
        for i in range(2, data.numrows() + 2):
            try:
                x1 = col1[i]
            except:
                x1 = 0.0
            try:
                x2 = col2[i]
            except:
                x2 = 0.0
            if x1 is None and x2 is None:
                ans.append(None)
            elif x1 is None and x2 is not None:
                ans.append(0.5 * x2)
            elif x1 is not None and x2 is None:
                ans.append(None)  # '>'+str(x1)
            else:
                ans.append(0.5 * (x1 + x2))
        return ans

    def getError(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        if self.column1Parser is not None:
            col1 = self.column1Parser.getColumn(self.icol1, data)
        else:
            col1 = self.getDummyColumn(data)
        if self.column2Parser is not None:
            col2 = self.column2Parser.getColumn(self.icol2, data)
        else:
            col2 = self.getDummyColumn(data)
        ans = [None, None]
        for i in [0, 1]:
            for j in [col1[i], col2[i]]:
                if j is not None:
                    ans[i] = j
        for i in range(2, data.numrows() + 2):
            try:
                x1 = col1[i]
            except:
                x1 = 0.0
            try:
                x2 = col2[i]
            except:
                x2 = 0.0
            if x1 is None or x2 is None:
                ans.append(None)
            elif x1 is None and x2 is not None:
                ans.append(0.5 * x2)
            elif x1 is not None and x2 is None:
                ans.append(None)
            else:
                ans.append(0.5 * abs(x1 - x2))
        return [absOrNone(x) for x in ans]


class X4HighMidLowColumnPair(X4IndependentColumnPair):
    def __init__(self, column1Parser, column2Parser, column3Parser):
        self.column1Parser = column1Parser  # middle
        self.column2Parser = column2Parser  # -err
        self.column3Parser = column3Parser  # +err
        self.icol1 = -1
        self.icol2 = -1
        self.icol3 = -1

    def set_icols(self, data):
        self.icol1 = self.column1Parser.firstMatch(data)
        self.icol2 = self.column2Parser.firstMatch(data)
        self.icol3 = self.column3Parser.firstMatch(data)

    def isMatch(self, data):
        self.set_icols(data)
        return self.icol1 >= 0 and (self.icol2 >= 0 or self.icol3 >= 0)

    def getValue(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        if self.column1Parser is not None:
            col1 = self.column1Parser.getColumn(self.icol1, data)
        else:
            col1 = self.getDummyColumn(data)
        if self.column2Parser is not None:
            col2 = self.column2Parser.getColumn(self.icol2, data)
        else:
            col2 = self.getDummyColumn(data)
        if self.column3Parser is not None:
            col3 = self.column3Parser.getColumn(self.icol3, data)
        else:
            col3 = self.getDummyColumn(data)
        ans = [None, None]
        for i in [0, 1]:
            for j in [col1[i], col2[i], col3[i]]:
                if j is not None:
                    ans[i] = j
        for i in range(2, data.numrows() + 2):
            try:
                x1 = col1[i]
            except:
                x1 = 0.0
            try:
                x2 = col2[i]
            except:
                x2 = 0.0
            try:
                x3 = col3[i]
            except:
                x3 = 0.0
            if x1 is None or x2 is None or x3 is None:
                ans.append(None)
            else:
                ans.append(0.5 * ((x1 - x2) + (x1 + x3)))
        return ans

    def getError(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        if self.column1Parser is not None:
            col1 = self.column1Parser.getColumn(self.icol1, data)
        else:
            col1 = self.getDummyColumn(data)
        if self.column2Parser is not None:
            col2 = self.column2Parser.getColumn(self.icol2, data)
        else:
            col2 = self.getDummyColumn(data)
        if self.column3Parser is not None:
            col3 = self.column3Parser.getColumn(self.icol3, data)
        else:
            col3 = self.getDummyColumn(data)
        ans = [None, None]
        for i in [0, 1]:
            for j in [col1[i], col2[i], col3[i]]:
                if j is not None:
                    ans[i] = j
        for i in range(2, data.numrows() + 2):
            try:
                x1 = col1[i]
            except:
                x1 = 0.0
            try:
                x2 = col2[i]
            except:
                x2 = 0.0
            try:
                x3 = col3[i]
            except:
                x3 = 0.0
            if x1 is None or x2 is None or x3 is None:
                ans.append(None)
            else:
                ans.append(abs(0.5 * ((x1 - x2) - (x1 + x3))))
        return [absOrNone(x) for x in ans]


class X4AddErrorBarsColumnPair(X4HighMidLowColumnPair):
    def getValue(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        if self.column1Parser is not None:
            col1 = self.column1Parser.getColumn(self.icol1, data)
        else:
            col1 = self.getDummyColumn(data)
        return col1

    def getError(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        # raise UserWarning('got one')
        self.set_icols(data)
        if self.column2Parser is not None:
            col2 = self.column2Parser.getColumn(self.icol2, data)
        else:
            col2 = self.getDummyColumn(data)
        if self.column3Parser is not None:
            col3 = self.column3Parser.getColumn(self.icol3, data)
        else:
            col3 = self.getDummyColumn(data)
        ans = ['ERR', None]
        if 'PER-CENT' in [col2[1], col3[1]]:
            col1 = self.getValue(data)
            ans[1] = col1[1]
            for i in range(2, data.numrows() + 2):
                try:
                    col2[i] = col1[i] * col2[i] / 100.0
                except:
                    col2[i] = None
                try:
                    col3[i] = col1[i] * col3[i] / 100.0
                except:
                    col3[i] = None
        else:
            for j in [col2[1], col3[1]]:
                if j != None: ans[1] = j
        for i in range(2, data.numrows() + 2):
            x2 = col2[i]
            x3 = col3[i]
            if x2 is None and x3 is None:
                ans.append(None)
            else:
                if x2 is None: x2 = 0.0
                if x3 is None: x3 = 0.0
                ans.append(math.sqrt(x2 * x2 + x3 * x3))
        return [absOrNone(x) for x in ans]


class X4BarnsSqrtEColumnPair(X4IndependentColumnPair):
    def __init__(self, column2Parser, column3Parser):
        self.column2Parser = column2Parser  # CS
        self.column3Parser = column3Parser  # dCS
        self.icol2 = -1
        self.icol3 = -1

    def energyColumn(self, data):
        return reduce(condenseColumn, [i.getValue(data) for i in incidentEnergyParserList])

    def set_icols(self, data):
        self.icol2 = self.column2Parser.firstMatch(data)
        self.icol3 = self.column3Parser.firstMatch(data)

    def isMatch(self, data):
        self.set_icols(data)
        return self.icol2 >= 0

    def getValue(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
        self.set_icols(data)
        col1 = self.energyColumn(data)
        if self.column2Parser is not None:
            col2 = self.column2Parser.getColumn(self.icol2, data)
        else:
            col2 = self.getDummyColumn(data)
        ans = [col2[0], 'barns']
        for i in range(2, data.numrows() + 2):
            try:
                x1 = col1[i]
            except:
                x1 = 0.0
            try:
                x2 = col2[i]
            except:
                x2 = 0.0
            if x1 is None or x2 is None:
                ans.append(None)
            else:
                ans.append(x2 / math.sqrt(x1 * 1e6))
        return ans

    def getError(self, data):
        if not self.isMatch(data): return self.getDummyColumn(data)
        self.set_icols(data)
        col1 = self.energyColumn(data)
        if self.column3Parser is not None:
            col3 = self.column3Parser.getColumn(self.icol3, data)
        else:
            col3 = self.getDummyColumn(data)
        ans = [col3[0], 'barns']
        for i in range(2, data.numrows() + 2):
            try:
                x1 = col1[i]
            except:
                x1 = None
            try:
                x3 = col3[i]
            except:
                x3 = 0.0
            if x1 is None or x3 is None:
                ans.append(None)
            else:
                ans.append(x3 / math.sqrt(x1 * 1e6))
        return [absOrNone(x) for x in ans]


class X4CosineAngleColumnPair(X4IndependentColumnPair): pass


class X4EinCMToLabColumnPair(X4IndependentColumnPair): pass


# -----------------------------------
# Below are lists of parsers ... insert detailed explanation here
# -----------------------------------
incidentEnergyParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['EN' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['EN' + s for s in errorSuffix])
    ),
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['EN' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['EN' + s for s in resolutionFWSuffix])
    ),
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['EN' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['EN' + s for s in resolutionHWSuffix])
    ),
    X4HighLowColumnPair(
        X4ColumnParser(match_labels=['EN-MIN']),
        X4ColumnParser(match_labels=['EN-MAX'])
    ),
    X4HighMidLowColumnPair(
        X4ColumnParser(match_labels=['EN'] + baseMomKeys),
        X4ColumnParser(match_labels=['-EN-ERR']),
        X4ColumnParser(match_labels=['+EN-ERR']),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(match_labels=['EN' + s for s in variableSuffix] + baseMomKeys), 
        None
    ),
]

incidentMomentumParserList = [
    X4HighLowColumnPair(
        X4ColumnParser(match_labels=['MOM-MIN']),
        X4ColumnParser(match_labels=['MOM-MAX'])
    ),
]

outgoingEnergyParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['E' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['E' + s for s in errorSuffix])
    ),
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['E' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['E' + s for s in resolutionFWSuffix])
    ),
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['E' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['E' + s for s in resolutionHWSuffix])
    ),
    X4HighLowColumnPair(
        X4ColumnParser(match_labels=['E-MIN']),
        X4ColumnParser(match_labels=['E-MAX'])
    ),
    X4HighMidLowColumnPair(
        X4ColumnParser(match_labels=['E'] + baseMomKeys),
        X4ColumnParser(match_labels=['-E-ERR']),
        X4ColumnParser(match_labels=['+E-ERR']),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(match_labels=['E' + s for s in variableSuffix] + baseMomKeys),
        None,
    ),
]

tempParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['KT' + s for s in variableSuffix + shiftSuffix]),
        X4ColumnParser(match_labels=['KT' + s for s in errorSuffix]),
    ),
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['KT' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['KT' + s for s in resolutionFWSuffix])
    ),
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=['KT' + s for s in variableSuffix]),
        X4ColumnParser(match_labels=['KT' + s for s in resolutionHWSuffix])
    ),
    X4HighLowColumnPair(
        X4ColumnParser(match_labels=['KT-MIN']),
        X4ColumnParser(match_labels=['KT-MAX'])
    ),
    X4HighMidLowColumnPair(
        X4ColumnParser(match_labels=['KT']),
        X4ColumnParser(match_labels=['-KT-ERR']),
        X4ColumnParser(match_labels=['+KT-ERR']),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(
            match_labels=['TEMP' + s for s in variableSuffix + shiftSuffix] + ['KT' + s for s in variableSuffix]),
    ),
]

spectrumArgumentParserList = tempParserList + incidentEnergyParserList

csDataParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y,
                                           [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys])),
        X4ColumnParser(match_labels=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys),
    ),
    X4HighLowColumnPair(
        X4ColumnParser(match_labels=[b + '-MIN' for b in baseDataKeys]),
        X4ColumnParser(match_labels=[b + '-MAX' for b in baseDataKeys]),
    ),
    X4HighMidLowColumnPair(
        X4ColumnParser(match_labels=baseDataKeys),
        X4ColumnParser(match_labels=['-' + b + '-ERR' for b in baseDataKeys]),
        X4ColumnParser(match_labels=['+' + b + '-ERR' for b in baseDataKeys]),
    ),
    X4AddErrorBarsColumnPair(
        X4ColumnParser(match_labels=baseDataKeys),
        X4ColumnParser(match_labels=dataSystematicErrorKeys),
        X4ColumnParser(match_labels=dataStatisticalErrorKeys),
    ),
    X4BarnsSqrtEColumnPair(
        X4ColumnParser(match_labels=['DATA']),
        X4ColumnParser(match_labels=['DATA-ERR']),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys])),
    ),
]

nubarParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys])),
        X4ColumnParser(match_labels=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys),
    ),
    X4HighLowColumnPair(
        X4ColumnParser(match_labels=[b + '-MIN' for b in baseDataKeys]),
        X4ColumnParser(match_labels=[b + '-MAX' for b in baseDataKeys]),
    ),
    X4HighMidLowColumnPair(
        X4ColumnParser(match_labels=baseDataKeys),
        X4ColumnParser(match_labels=['-' + b + '-ERR' for b in baseDataKeys]),
        X4ColumnParser(match_labels=['+' + b + '-ERR' for b in baseDataKeys]),
    ),
    X4AddErrorBarsColumnPair(
        X4ColumnParser(match_labels=baseDataKeys),
        X4ColumnParser(match_labels=dataSystematicErrorKeys),
        X4ColumnParser(match_labels=dataStatisticalErrorKeys),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys])),
    ),
]

angDistParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y,
                                           [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys])),
        X4ColumnParser(match_labels=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y,
                                           [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys])),
    ),
]

energyDistParserList = [
    X4IndependentColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y,
                                           [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys])),
        X4ColumnParser(match_labels=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys),
    ),
    X4MissingErrorColumnPair(
        X4ColumnParser(match_labels=reduce(lambda x, y: x + y,
                                           [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys])),
    ),
]

angleParserList = [
    X4IndependentColumnPair(
        X4AngleColumnParser(match_labels=reduce(lambda x, y: x + y,
                                                [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys])),
        X4AngleColumnParser(match_labels=reduce(lambda x, y: x + y,
                                                [[b + s for s in errorSuffix + resolutionHWSuffix] for b in
                                                 baseAngleKeys]))
    ),
    X4IndependentColumnPair(
        X4AngleColumnParser(match_labels=reduce(lambda x, y: x + y,
                                                [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys])),
        X4AngleColumnParser(
            match_labels=reduce(lambda x, y: x + y, [[b + s for s in resolutionFWSuffix] for b in baseAngleKeys]))
    ),
    X4MissingErrorColumnPair(
        X4AngleColumnParser(match_labels=reduce(lambda x, y: x + y,
                                                [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys])),
    ),
]

# print reduce( lambda x, y: x + y, [ [ b + s for s in variableSuffix + frameSuffix ] for b in baseAngleKeys ] )
# print reduce( lambda x, y: x + y, [ [ b + s for s in errorSuffix + resolutionHWSuffix ] for b in baseAngleKeys ] )
# print reduce( lambda x, y: x + y, [ [ b + s for s in resolutionFWSuffix ] for b in baseAngleKeys ] )
# print angUnits + noUnits + percentUnits
