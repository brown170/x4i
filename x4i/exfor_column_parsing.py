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
import math
from functools import reduce
from .exfor_units import exfor_unit_registry

baseIncidentEnergyKeys = ['EN']
baseOutgoingEnergyKeys = ['E']
baseMomKeys = ['MOM']
baseTempKeys = ['KT']
baseMonitorKeys = ['MONIT']
baseDataKeys = ['DATA', 'RATIO']
baseMiscKeys = ['MISC']
baseAngleKeys = ['ANG']
baseCosineAngleKeys = ['COS']

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


class X4ColumnProcessor:
    """
    Simple Base class.  Defines init function, but you must override
    the member functions if you expect anything to work
    """

    def __init__(self, **kw):
        self.__data = None

    @property
    def data(self):
        return self.__data

    def set_data(self, data):
        self.__data = data

    def score_label_match(self):
        raise NotImplementedError()

    def score_helper(self, labels):
        for label in labels:
            if label in self.data:
                return 1
        return 0

    def get_column_helper(self, labels, as_list=True):
        for label in labels:
            if label in self.data:
                if as_list:
                    return self.data[label].to_list()
                else:
                    return self.data[label]

    def get_uncertainty_helper(self, labels, value_column, as_list=True):
        for label in labels:
            if label in self.data:
                if self.data[label].pint.units == exfor_unit_registry.percent:
                    self.data[label] *= value_column
                if as_list:
                    return self.data[label].to_list()
                else:
                    return self.data[label]
        
    def get_unit_helper(self, labels):
        for label in labels:
            if label in self.data:
                return self.data[label].pint.units

    def get_values(self):
        raise NotImplementedError()

    def get_uncertainties(self):
        raise NotImplementedError()
    
    def get_unit(self):
        raise NotImplementedError()

    def get_dummy_column(self):
        return [None] * len(self.data)


class X4MissingErrorColumnPair(X4ColumnProcessor):
    """
    Matches first occurrence of column label
    """
    def __init__(self, labels_for_values):
        X4ColumnProcessor.__init__(self)
        self.__labels_for_values = labels_for_values

    def score_label_match(self):
        return self.score_helper(self.__labels_for_values)

    def get_values(self):
        return self.get_column_helper(self.__labels_for_values)

    def get_uncertainties(self):
        return self.get_dummy_column()

    def get_unit(self):
        return self.get_unit_helper(self.__labels_for_values)


class X4IndependentColumnPair(X4ColumnProcessor):
    """
    Matches first occurrences of Column 1 and 2 (that matches your pointer, if any)
    """
    def __init__(self, labels_for_values, labels_for_uncertainties):
        X4ColumnProcessor.__init__(self)
        self.__labels_for_values = labels_for_values
        self.__labels_for_uncertainties = labels_for_uncertainties

    def score_label_match(self):
        return self.score_helper(self.__labels_for_values) + self.score_helper(self.__labels_for_uncertainties)

    def get_values(self):
        return self.get_column_helper(self.__labels_for_values)

    def get_uncertainties(self, as_list=True):
        return self.get_uncertainty_helper(labels=self.__labels_for_uncertainties, 
                                           value_column=self.get_column_helper(self.__labels_for_values, as_list=False), 
                                           as_list=as_list)

    def get_unit(self):
        return self.get_unit_helper(self.__labels_for_values)


class X4IndependentColumnPair_ResolutionFW(X4IndependentColumnPair):
    def get_uncertainties(self):
        return (X4IndependentColumnPair.get_uncertainties(self, as_list=False)/2.0).to_list()


class X4IndependentColumnPair_ResolutionHW(X4IndependentColumnPair):
    pass # already has correct scaling for uncertainties


class X4ConstantPercentColumnPair(X4MissingErrorColumnPair):
    """
    Matches first occurance of Column 1, ignores Column 2.
    Set percentError to something other than 10% for real work!
    """

    def __init__(self, labels_for_values, common_percent_error=10):
        X4MissingErrorColumnPair.__init__(self, labels_for_values, None)
        self.__common_percent_error = common_percent_error
 
    def score_label_match(self):
        return self.score_helper(self.__labels_for_values) + 0.5

    def get_uncertainties(self):
        values = self.get_column_helper(self.__labels_for_values, as_list=False)
        return (0.01 * self.__common_percent_error * values).to_list()


class X4HighLowColumnPair(X4ColumnProcessor):
    
    def __init__(self, labels_for_highs, labels_for_lows):
        X4ColumnProcessor.__init__(self)
        self.__labels_for_highs = labels_for_highs
        self.__labels_for_lows = labels_for_lows

    def score_label_match(self):
        return self.score_helper(self.__labels_for_highs) + self.score_helper(self.__labels_for_lows)

    def get_values(self):
        return (0.5 * (self.get_column_helper(self.__labels_for_highs) + \
                       self.get_column_helper(self.__labels_for_lows))).to_list()

    def get_uncertainties(self):
        return (0.5 * (self.get_column_helper(self.__labels_for_highs) - \
                       self.get_column_helper(self.__labels_for_lows))).abs().to_list()

    def get_unit(self):
        return self.get_unit_helper(self.__labels_for_highs)


class X4HighMidLowColumnTriplet(X4ColumnProcessor):
    def __init__(self, labels_for_values, labels_for_highs, labels_for_lows):
        self.__labels_for_values = labels_for_values  # middle
        self.__labels_for_highs = labels_for_highs  # +err
        self.__labels_for_lows = labels_for_lows  # -err

    def score_label_match(self):
        return self.score_helper(self.__labels_for_values) + \
               0.5*(self.score_helper(self.__labels_for_highs) + self.score_helper(self.__labels_for_lows))

    def get_values(self):
        return self.get_column_helper(self.__labels_for_values)

    def get_uncertainties(self):
        highs = self.get_uncertainty_helper(self.__labels_for_highs, as_list=False,
                                            values_column=self.get_column_helper(self.__labels_for_values, as_list=False))
        lows = self.get_uncertainty_helper(self.__labels_for_lows, as_list=False,
                                           values_column=self.get_column_helper(self.__labels_for_values, as_list=False))
        return (0.5 * (highs-lows)).abs().to_list()

    def get_unit(self):
        return self.get_unit_helper(self.__labels_for_values)


class X4AddErrorBarsColumnPair(X4ColumnProcessor):
    def __init__(self, labels_for_values, labels_for_systematic_uncertainties, labels_for_statistical_uncertainties):
        self.__labels_for_values = labels_for_values 
        self.__labels_for_systematic_uncertainties = labels_for_systematic_uncertainties 
        self.__labels_for_statistical_uncertainties = labels_for_statistical_uncertainties 

    def score_label_match(self):
        raise NotImplementedError("X4AddErrorBarsColumnPair")
        return self.score_helper(self.__labels_for_values) + 4

    def get_values(self):
        return self.get_column_helper(self.__labels_for_values)

    def get_uncertainties(self):
        raise NotImplementedError("X4AddErrorBarsColumnPair")
        return (0.5 * (self.get_column_helper(self.__labels_for_highs) - \
                       self.get_column_helper(self.__labels_for_lows))).abs().to_list()

    def get_unit(self):
        return self.get_unit_helper(self.__labels_for_values)

    def getError(self, data):
        if not self.isMatch(data):
            return self.getDummyColumn(data)
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


# -----------------------------------
# Below are lists of parsers ... insert detailed explanation here
# -----------------------------------
incidentEnergyParserList = [
    X4IndependentColumnPair(
        labels_for_values=['EN' + s for s in variableSuffix],
        labels_for_uncertainties=['EN' + s for s in errorSuffix]
    ),
    X4IndependentColumnPair_ResolutionFW(
        labels_for_values=['EN' + s for s in variableSuffix],
        labels_for_uncertainties=['EN' + s for s in resolutionFWSuffix]
    ),
    X4IndependentColumnPair_ResolutionHW(
        labels_for_values=['EN' + s for s in variableSuffix],
        labels_for_uncertainties=['EN' + s for s in resolutionHWSuffix]
    ),
    X4HighLowColumnPair(
        labels_for_highs=['EN-MIN'],
        labels_for_lows=['EN-MAX']
    ),
    X4HighMidLowColumnTriplet(
        labels_for_values=['EN'] + baseMomKeys,
        labels_for_highs=['-EN-ERR'],
        labels_for_lows=['+EN-ERR']
    ),
    X4MissingErrorColumnPair(labels_for_values=['EN' + s for s in variableSuffix] + baseMomKeys),
]

incidentMomentumParserList = [
    X4HighLowColumnPair(
        labels_for_highs=['MOM-MIN'],
        labels_for_lows=['MOM-MAX']
    ),
]

outgoingEnergyParserList = [
    X4IndependentColumnPair(
        labels_for_values=['E' + s for s in variableSuffix],
        labels_for_uncertainties=['E' + s for s in errorSuffix]
    ),
    X4IndependentColumnPair(
        labels_for_values=['E' + s for s in variableSuffix],
        labels_for_uncertainties=['E' + s for s in resolutionFWSuffix]
    ),
    X4IndependentColumnPair(
        labels_for_values=['E' + s for s in variableSuffix],
        labels_for_uncertainties=['E' + s for s in resolutionHWSuffix]
    ),
    X4HighLowColumnPair(
        labels_for_highs=['E-MIN'],
        labels_for_lows=['E-MAX']
    ),
    X4HighMidLowColumnTriplet(
        labels_for_values=['E'] + baseMomKeys,
        labels_for_highs=['-E-ERR'],
        labels_for_lows=['+E-ERR']
    ),
    X4MissingErrorColumnPair(labels_for_values=['E' + s for s in variableSuffix] + baseMomKeys),
]

tempParserList = [
    X4IndependentColumnPair(
        labels_for_values=['KT' + s for s in variableSuffix + shiftSuffix],
        labels_for_uncertainties=['KT' + s for s in errorSuffix],
    ),
    X4IndependentColumnPair(
        labels_for_values=['KT' + s for s in variableSuffix],
        labels_for_uncertainties=['KT' + s for s in resolutionFWSuffix]
    ),
    X4IndependentColumnPair(
        labels_for_values=['KT' + s for s in variableSuffix],
        labels_for_uncertainties=['KT' + s for s in resolutionHWSuffix]
    ),
    X4HighLowColumnPair(
        labels_for_highs=['KT-MIN'],
        labels_for_lows=['KT-MAX']
    ),
    X4HighMidLowColumnTriplet(
        labels_for_values=['KT'],
        labels_for_highs=['-KT-ERR'],
        labels_for_lows=['+KT-ERR']
    ),
    X4MissingErrorColumnPair(
        labels_for_values=['TEMP' + s for s in variableSuffix + shiftSuffix] + ['KT' + s for s in variableSuffix]
    ),
]

spectrumArgumentParserList = tempParserList + incidentEnergyParserList

csDataParserList = [
    X4IndependentColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys]),
        labels_for_uncertainties=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys
    ),
    X4HighLowColumnPair(
        labels_for_highs=[b + '-MIN' for b in baseDataKeys],
        labels_for_lows=[b + '-MAX' for b in baseDataKeys],
    ),
    X4HighMidLowColumnTriplet(
        labels_for_values=baseDataKeys,
        labels_for_highs=['-' + b + '-ERR' for b in baseDataKeys],
        labels_for_lows=['+' + b + '-ERR' for b in baseDataKeys]
    ),
# FIXME!!!!!
#    X4AddErrorBarsColumnPair(
#        labels_for_values=baseDataKeys,
#        labels_for_systematic_uncertainties=dataSystematicErrorKeys,
#        labels_for_statistical_uncertainties=dataStatisticalErrorKeys
#    ),
    X4MissingErrorColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys]),
    ),
]

nubarParserList = [
    X4IndependentColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys]),
        labels_for_uncertainties=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys
    ),
    X4HighLowColumnPair(
        labels_for_highs=[b + '-MIN' for b in baseDataKeys],
        labels_for_lows=[b + '-MAX' for b in baseDataKeys]
    ),
    X4HighMidLowColumnTriplet(
        labels_for_values=baseDataKeys,
        labels_for_highs=['-' + b + '-ERR' for b in baseDataKeys],
        labels_for_lows=['+' + b + '-ERR' for b in baseDataKeys]
    ),
# FIXME!!!!!
#    X4AddErrorBarsColumnPair(
#        labels_for_values=baseDataKeys,
#        labels_for_systematic_uncertainties=dataSystematicErrorKeys,
#        labels_for_statistical_uncertainties=dataStatisticalErrorKeys
#    ),
    X4MissingErrorColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys]),
    ),
]

# print(reduce(lambda x, y: x + y, [[b + s for s in variableSuffix] for b in baseDataKeys]))
 

angDistParserList = [
    X4IndependentColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys]),
        labels_for_uncertainties=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys
    ),
    X4MissingErrorColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys]),
    ),
]

energyDistParserList = [
    X4IndependentColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys]),
        labels_for_uncertainties=[b + '-ERR' for b in baseDataKeys] + dataTotalErrorKeys
    ),
    X4MissingErrorColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseDataKeys]),
    ),
]

angleParserList = [
    X4IndependentColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys]),
        labels_for_uncertainties=reduce(lambda x, y: x + y, [[b + s for s in errorSuffix] for b in baseAngleKeys])
    ),
    X4IndependentColumnPair_ResolutionHW(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys]),
        labels_for_uncertainties=reduce(lambda x, y: x + y, [[b + s for s in resolutionHWSuffix] for b in baseAngleKeys])
    ),
    X4IndependentColumnPair_ResolutionFW(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys]),
        labels_for_uncertainties=reduce(lambda x, y: x + y, [[b + s for s in resolutionFWSuffix] for b in baseAngleKeys])
    ),
    X4MissingErrorColumnPair(
        labels_for_values=reduce(lambda x, y: x + y, [[b + s for s in variableSuffix + frameSuffix] for b in baseAngleKeys]),
    ),
]
